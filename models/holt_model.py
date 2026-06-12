"""
models/holt_model.py
Figure 6 — Holt Exponential Smoothing (additive trend) forecast of India's
           wind installed capacity with uncertainty band.
           Implemented in pure numpy (statsmodels not available in this env).

Data: W1_Final_Objective_Dataset.xlsx (W1_Master_Dataset)
Run standalone:  python models/holt_model.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

from utils import (
    HIST_YEARS, HIST_CAP, FORECAST_YEARS,
    NAVY, TEAL, ORANGE, MGRAY, TEXT,
    set_style, target_lines, forecast_divider, source_note,
    xtick_fy, annotate_val, status_badge, save_fig,
    TARGET_100,
)

PURPLE = "#8E44AD"


def holt_fit(data: np.ndarray, alpha: float, beta: float):
    """Holt's double (linear) exponential smoothing — additive trend."""
    n = len(data)
    L = np.zeros(n)
    T = np.zeros(n)
    # Initialise
    L[0] = data[0]
    T[0] = data[1] - data[0]
    for t in range(1, n):
        L[t] = alpha * data[t]       + (1 - alpha) * (L[t-1] + T[t-1])
        T[t] = beta  * (L[t] - L[t-1]) + (1 - beta)  * T[t-1]
    fitted = L + T
    return L, T, fitted


def optimise_holt(data: np.ndarray):
    """Grid-search alpha & beta to minimise RMSE on in-sample fit."""
    best_rmse  = np.inf
    best_alpha = 0.5
    best_beta  = 0.1
    for alpha in np.arange(0.05, 1.0, 0.05):
        for beta in np.arange(0.01, 0.5, 0.02):
            _, _, fitted = holt_fit(data, alpha, beta)
            rmse = float(np.sqrt(np.mean((data - fitted) ** 2)))
            if rmse < best_rmse:
                best_rmse  = rmse
                best_alpha = alpha
                best_beta  = beta
    return round(best_alpha, 2), round(best_beta, 2)


def train() -> dict:
    """Optimise and fit Holt ES on W1 cumulative capacity data."""
    cap = np.array(HIST_CAP, dtype=float)

    alpha, beta = optimise_holt(cap)
    L, T, fitted = holt_fit(cap, alpha, beta)

    r2   = r2_score(cap, fitted)
    rmse = float(np.sqrt(mean_squared_error(cap, fitted)))
    mae  = float(mean_absolute_error(cap, fitted))
    resid_std = float(np.std(cap - fitted))

    # Forecast h=1..5 steps beyond last observed
    fc = [L[-1] + i * T[-1] for i in range(1, 6)]

    return dict(
        fitted=fitted, fc=np.array(fc), resid_std=resid_std,
        years=FORECAST_YEARS, forecast=[round(v, 2) for v in fc],
        r2=round(r2, 4), rmse=round(rmse, 3), mae=round(mae, 3),
        alpha=alpha, beta=beta,
    )


def run() -> dict:
    """Train, forecast, plot Figure 6, return results dict."""
    set_style()
    res = train()
    fc  = res["fc"]

    fig, ax = plt.subplots(figsize=(12, 6.5))

    ax.scatter(HIST_YEARS, HIST_CAP, color=NAVY, s=55, zorder=6,
               label="Actual Data (FY2000–FY2025) — W1 Dataset")
    ax.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=1.5, alpha=0.45)
    ax.plot(HIST_YEARS, res["fitted"], color=MGRAY, lw=1.5,
            alpha=0.75, label="Holt Fitted Values")

    ax.plot(FORECAST_YEARS, fc, color=PURPLE, lw=2.6, marker="^",
            ms=8, zorder=7,
            label=f"Holt Forecast → 2030: {fc[-1]:.1f} GW")
    ax.plot([HIST_YEARS[-1], FORECAST_YEARS[0]],
            [HIST_CAP[-1], fc[0]], color=PURPLE, lw=2.6, ls="--")

    ax.fill_between(FORECAST_YEARS,
                    fc - 2 * res["resid_std"],
                    fc + 2 * res["resid_std"],
                    color=PURPLE, alpha=0.12, label="±2 Std band")

    for yr, v in zip(FORECAST_YEARS, fc):
        annotate_val(ax, yr, v, PURPLE)

    forecast_divider(ax, x=2025.5, y_txt=3)
    target_lines(ax)
    source_note(ax)

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
        "Figure 6 — Holt Exponential Smoothing Forecast: India Wind Capacity (FY2026–FY2030)\n"
        "Data: W1_Final_Objective_Dataset.xlsx (FY2000–FY2025, n=26)",
        pad=12,
    )
    ax.set_xlabel("Financial Year End")
    ax.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax, np.array(HIST_YEARS), step=2, extra=FORECAST_YEARS)
    ax.set_ylim(0, 155)
    ax.legend(loc="upper left", fontsize=9)

    fc30  = float(fc[-1])
    badge = "AT RISK" if fc30 < TARGET_100 else "LIKELY ACHIEVED"
    status_badge(ax, badge)

    save_fig(fig, "fig6_holt.png")
    print(f"\n  Holt 2030 forecast: {fc30:.2f} GW  [{badge}]")
    print(f"  R²={res['r2']}  RMSE={res['rmse']} GW  MAE={res['mae']} GW")
    print(f"  α={res['alpha']}  β={res['beta']}")
    return dict(forecast=res["forecast"], years=FORECAST_YEARS,
                r2=res["r2"], rmse=res["rmse"], mae=res["mae"])


if __name__ == "__main__":
    print("\n── Model 4 · Holt Exponential Smoothing (W1 Dataset) ──────")
    run()
