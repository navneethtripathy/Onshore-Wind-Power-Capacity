"""
models/linear_regression.py
Figure 3 — Linear Regression forecast of India's wind installed capacity
           with ±2 RMSE confidence band and 100/140 GW target lines.

Run standalone:  python models/linear_regression.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

from utils import (
    HIST_YEARS, HIST_CAP, FORECAST_YEARS,
    NAVY, BLUE, TEAL, ORANGE, MGRAY, TEXT,
    set_style, target_lines, forecast_divider, source_note,
    xtick_fy, annotate_val, status_badge, save_fig, fy,
    TARGET_100,
)


def train() -> dict:
    """Fit Linear Regression on historical data; return model + metrics."""
    X      = np.array(HIST_YEARS, dtype=float).reshape(-1, 1)
    y      = np.array(HIST_CAP,   dtype=float)
    model  = LinearRegression().fit(X, y)
    y_fit  = model.predict(X)
    r2     = r2_score(y, y_fit)
    rmse   = np.sqrt(mean_squared_error(y, y_fit))
    mae    = mean_absolute_error(y, y_fit)

    X_fc   = np.array(FORECAST_YEARS, dtype=float).reshape(-1, 1)
    fc     = model.predict(X_fc)

    X_all  = np.concatenate([X, X_fc])
    y_all  = model.predict(X_all)

    return dict(
        model=model, r2=round(r2,4), rmse=round(rmse,3), mae=round(mae,3),
        y_fit=y_fit, y_all=y_all, X_all=X_all.flatten(),
        forecast=list(np.round(fc, 2)), years=FORECAST_YEARS, rmse_raw=rmse,
    )


def run(plots_dir=None) -> dict:
    """Train, forecast, plot Figure 3 and return results dict."""
    set_style()
    res = train()
    fc  = np.array(res["forecast"])

    fig, ax = plt.subplots(figsize=(11, 6))

    # Historical scatter + model line
    ax.scatter(HIST_YEARS, HIST_CAP, color=NAVY, s=55, zorder=6,
               label="Actual Data (FY2000-01–FY2024-25)")
    ax.plot(res["X_all"], res["y_all"], color=BLUE, lw=2.3,
            label=f"Linear Regression  R²={res['r2']:.4f}")

    # Confidence band ±2 RMSE
    ax.fill_between(FORECAST_YEARS,
                    fc - 2 * res["rmse_raw"], fc + 2 * res["rmse_raw"],
                    color=BLUE, alpha=0.13, label="±2 RMSE band")

    # Forecast point labels
    for yr, v in zip(FORECAST_YEARS, fc):
        annotate_val(ax, yr, v, BLUE)

    forecast_divider(ax, y_txt=8)
    target_lines(ax)

    ax.set_title("Figure 3 — Linear Regression Forecast: India Wind Capacity (FY2025-26–FY2029-30)",
                 pad=12)
    ax.set_xlabel("Financial Year")
    ax.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax, np.array(HIST_YEARS), step=2, extra=FORECAST_YEARS)
    ax.set_ylim(0, 155)
    ax.legend(loc="upper left")
    source_note(ax)
    ax.text(0.98, 0.14,
            f"RMSE: {res['rmse']} GW  |  MAE: {res['mae']} GW",
            transform=ax.transAxes, fontsize=8, color="#7F8C8D", ha="right")

    fc30 = fc[-1]
    badge = "AT RISK" if fc30 < TARGET_100 else "LIKELY ACHIEVED"
    status_badge(ax, badge)

    save_fig(fig, "fig3_linear_regression.png")
    print(f"\n  Linear Regression 2030 forecast: {fc30:.2f} GW  [{badge}]")
    print(f"  R²={res['r2']}  RMSE={res['rmse']} GW  MAE={res['mae']} GW")
    return res


if __name__ == "__main__":
    print("\n── Model 1 · Linear Regression ────────────────────────────")
    run()
