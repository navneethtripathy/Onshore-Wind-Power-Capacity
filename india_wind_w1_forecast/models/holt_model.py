"""
models/holt_model.py
Figure 6 — Holt Exponential Smoothing (additive trend) forecast of India's
           wind installed capacity with uncertainty band.

Run standalone:  python models/holt_model.py
"""

import sys, os, warnings
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
warnings.filterwarnings("ignore")

import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

from utils import (
    HIST_YEARS, HIST_CAP, FORECAST_YEARS, N_FORECAST,
    NAVY, TEAL, ORANGE, MGRAY, TEXT,
    set_style, target_lines, forecast_divider, source_note,
    xtick_fy, annotate_val, status_badge, save_fig,
    TARGET_100,
)

PURPLE = "#8E44AD"


def train() -> dict:
    """Fit Holt additive-trend ES on cumulative capacity; forecast 4 steps."""
    cap = np.array(HIST_CAP, dtype=float)

    model = ExponentialSmoothing(
        cap, trend="add", damped_trend=False,
        initialization_method="estimated",
    ).fit(optimized=True)

    fc     = model.forecast(N_FORECAST)
    fitted = model.fittedvalues
    resid_std = float(np.std(cap - fitted))

    r2   = r2_score(cap, fitted)
    rmse = float(np.sqrt(mean_squared_error(cap, fitted)))
    mae  = float(mean_absolute_error(cap, fitted))

    return dict(
        fitted=fitted, fc=fc, resid_std=resid_std,
        years=FORECAST_YEARS, forecast=list(np.round(fc, 2)),
        r2=round(r2,4), rmse=round(rmse,3), mae=round(mae,3),
        alpha=round(float(model.params.get("smoothing_level", 0)),4),
        beta =round(float(model.params.get("smoothing_trend",  0)),4),
    )


def run(plots_dir=None) -> dict:
    """Train, forecast, plot Figure 6 and return results dict."""
    set_style()
    res = train()
    fc  = np.array(res["fc"])

    fig, ax = plt.subplots(figsize=(11, 6))

    # Historical actual
    ax.scatter(HIST_YEARS, HIST_CAP, color=NAVY, s=55, zorder=6,
               label="Actual Data (FY2000-01–FY2024-25)")
    ax.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=1.5, alpha=0.45)

    # Fitted values
    ax.plot(HIST_YEARS, res["fitted"], color=MGRAY, lw=1.5, ls="-",
            alpha=0.75, label="Holt Fitted Values")

    # Forecast line
    ax.plot(FORECAST_YEARS, fc, color=PURPLE, lw=2.6, marker="^",
            ms=8, zorder=7,
            label=f"Holt Forecast → 2030: {fc[-1]:.1f} GW")
    ax.plot([HIST_YEARS[-1], FORECAST_YEARS[0]],
            [HIST_CAP[-1], fc[0]], color=PURPLE, lw=2.6, ls="--")

    # Uncertainty band ±2 std
    ax.fill_between(
        FORECAST_YEARS,
        fc - 2 * res["resid_std"],
        fc + 2 * res["resid_std"],
        color=PURPLE, alpha=0.12, label="±2 Std band",
    )

    for yr, v in zip(FORECAST_YEARS, fc):
        annotate_val(ax, yr, v, PURPLE)

    forecast_divider(ax, y_txt=8)
    target_lines(ax)
    source_note(ax)

    # Parameter box
    ax.text(0.02, 0.97,
            f"α (level) = {res['alpha']}   β (trend) = {res['beta']}",
            transform=ax.transAxes, fontsize=8.5, color="#555",
            va="top", style="italic",
            bbox=dict(facecolor="#F4F6F7", edgecolor=MGRAY,
                      boxstyle="round,pad=0.4", alpha=0.85))

    ax.text(0.98, 0.14,
            f"RMSE: {res['rmse']} GW  |  MAE: {res['mae']} GW",
            transform=ax.transAxes, fontsize=8, color="#7F8C8D", ha="right")

    ax.set_title(
        "Figure 6 — Holt Exponential Smoothing Forecast: India Wind Capacity (FY2025-26–FY2029-30)",
        pad=12,
    )
    ax.set_xlabel("Financial Year")
    ax.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax, np.array(HIST_YEARS), step=2, extra=FORECAST_YEARS)
    ax.set_ylim(0, 155)
    ax.legend(loc="upper left")

    badge = "AT RISK" if fc[-1] < TARGET_100 else "LIKELY ACHIEVED"
    status_badge(ax, badge)

    save_fig(fig, "fig6_holt.png")
    print(f"\n  Holt 2030 forecast: {fc[-1]:.2f} GW  [{badge}]")
    print(f"  R²={res['r2']}  RMSE={res['rmse']} GW  MAE={res['mae']} GW")
    print(f"  α={res['alpha']}  β={res['beta']}")
    return dict(forecast=res["forecast"], years=FORECAST_YEARS,
                r2=res["r2"], rmse=res["rmse"], mae=res["mae"])


if __name__ == "__main__":
    print("\n── Model 4 · Holt Exponential Smoothing ───────────────────")
    run()
