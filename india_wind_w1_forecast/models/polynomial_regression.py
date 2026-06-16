"""
models/polynomial_regression.py
Figure 4 — Polynomial Regression (Degree 3) forecast of India's wind
           installed capacity with confidence band and target lines.

Run standalone:  python models/polynomial_regression.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

from utils import (
    HIST_YEARS, HIST_CAP, FORECAST_YEARS,
    NAVY, BLUE, TEAL, ORANGE, MGRAY, TEXT,
    set_style, target_lines, forecast_divider, source_note,
    xtick_fy, annotate_val, status_badge, save_fig, fy,
    TARGET_100,
)

DEGREE = 3   # Polynomial degree — change to 2 for quadratic


def train(degree: int = DEGREE) -> dict:
    """Fit Polynomial Regression (degree) on historical data."""
    X   = np.array(HIST_YEARS, dtype=float).reshape(-1, 1)
    y   = np.array(HIST_CAP,   dtype=float)

    pipe = Pipeline([
        ("poly", PolynomialFeatures(degree, include_bias=False)),
        ("lr",   LinearRegression()),
    ])
    pipe.fit(X, y)
    y_fit = pipe.predict(X)
    r2    = r2_score(y, y_fit)
    rmse  = np.sqrt(mean_squared_error(y, y_fit))
    mae   = mean_absolute_error(y, y_fit)

    X_fc  = np.array(FORECAST_YEARS, dtype=float).reshape(-1, 1)
    fc    = pipe.predict(X_fc)
    X_all = np.concatenate([X, X_fc])
    y_all = pipe.predict(X_all)

    return dict(
        model=pipe, degree=degree,
        r2=round(r2,4), rmse=round(rmse,3), mae=round(mae,3), rmse_raw=rmse,
        y_fit=y_fit, y_all=y_all, X_all=X_all.flatten(),
        forecast=list(np.round(fc, 2)), years=FORECAST_YEARS,
    )


def run(plots_dir=None) -> dict:
    """Train, forecast, plot Figure 4 and return results dict."""
    set_style()
    res = train(DEGREE)
    fc  = np.array(res["forecast"])

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.scatter(HIST_YEARS, HIST_CAP, color=NAVY, s=55, zorder=6,
               label="Actual Data (FY2000-01–FY2024-25)")
    ax.plot(res["X_all"], res["y_all"], color=TEAL, lw=2.3,
            label=f"Polynomial Reg. Degree-{DEGREE}  R²={res['r2']:.4f}")

    # Confidence band ±1.5 RMSE
    ax.fill_between(FORECAST_YEARS,
                    fc - 1.5 * res["rmse_raw"], fc + 1.5 * res["rmse_raw"],
                    color=TEAL, alpha=0.13, label="±1.5 RMSE band")

    # Stagger forecast labels to avoid overlap (values cluster near 50-52 GW)
    y_offsets = [12, -18, 12, -18, 12]
    for yr, v, dy in zip(FORECAST_YEARS, fc, y_offsets):
        ax.annotate(f"{v:.1f}", (yr, v), textcoords="offset points",
                    xytext=(4, dy), fontsize=8.5, color=TEAL, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=TEAL, lw=0.6, alpha=0.5)
                    if abs(dy) > 12 else None)

    # Degree-3 model note — curve flattens in forecast region (expected behaviour)
    ax.text(0.02, 0.60,
            "Note: Degree-3 polynomial curve flattens\nnear the historical data boundary.\n"
            "This is a known extrapolation behaviour\n— use with ARIMA / Holt for context.",
            transform=ax.transAxes, fontsize=8, color="#7F8C8D",
            va="top", style="italic",
            bbox=dict(facecolor="#F4F6F7", edgecolor=MGRAY,
                      boxstyle="round,pad=0.4", alpha=0.85))

    forecast_divider(ax, y_txt=8)
    target_lines(ax)

    ax.set_title(f"Figure 4 — Polynomial Regression (Degree-{DEGREE}) Forecast: "
                 f"India Wind Capacity (FY2025-26–FY2029-30)", pad=12)
    ax.set_xlabel("Financial Year")
    ax.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax, np.array(HIST_YEARS), step=2, extra=FORECAST_YEARS)
    ax.set_ylim(0, 155)
    ax.legend(loc="upper left")
    source_note(ax)
    ax.text(0.98, 0.14,
            f"RMSE: {res['rmse']} GW  |  MAE: {res['mae']} GW",
            transform=ax.transAxes, fontsize=8, color="#7F8C8D", ha="right")

    fc30  = fc[-1]
    badge = "AT RISK" if fc30 < TARGET_100 else "LIKELY ACHIEVED"
    status_badge(ax, badge)

    save_fig(fig, "fig4_polynomial_regression.png")
    print(f"\n  Polynomial (Deg-{DEGREE}) 2030 forecast: {fc30:.2f} GW  [{badge}]")
    print(f"  R²={res['r2']}  RMSE={res['rmse']} GW  MAE={res['mae']} GW")
    return res


if __name__ == "__main__":
    print("\n── Model 2 · Polynomial Regression ────────────────────────")
    run()
