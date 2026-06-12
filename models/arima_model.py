"""
models/arima_model.py
Figure 5 — ARIMA-style Autoregressive forecast on annual additions
           (implemented with numpy/sklearn since statsmodels is unavailable).
           Uses AR(1) with first-differencing — equivalent to ARIMA(1,1,0).

Data: W1_Final_Objective_Dataset.xlsx (W1_Master_Dataset)
Run standalone:  python models/arima_model.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from utils import (
    HIST_YEARS, HIST_CAP, ADDITIONS, FORECAST_YEARS,
    NAVY, BLUE, TEAL, ORANGE, RED, MGRAY, TEXT,
    set_style, target_lines, forecast_divider, source_note,
    xtick_fy, annotate_val, status_badge, save_fig, fy,
    TARGET_100,
)


def train() -> dict:
    """
    AR(1) model on first-differenced annual additions (stationary series).
    Fitted on W1 additions data (FY2001–FY2025, 25 points).
    Forecasts 5 annual additions → integrates to cumulative capacity.
    """
    add = np.array(ADDITIONS[1:], dtype=float)   # FY2001–FY2025, 25 values

    # First difference for stationarity
    d_add = np.diff(add)   # 24 values

    # AR(1): regress d_add[t] on d_add[t-1]
    X_ar = d_add[:-1].reshape(-1, 1)
    y_ar = d_add[1:]
    ar_model = LinearRegression().fit(X_ar, y_ar)
    phi      = float(ar_model.coef_[0])
    mu       = float(ar_model.intercept_)

    # Fitted annual additions (reconstruct from diffs)
    d_fitted = ar_model.predict(X_ar)
    add_fitted = add[:2].tolist()  # seed
    for df in d_fitted:
        add_fitted.append(add_fitted[-1] + df)
    add_fitted = np.array(add_fitted)

    r2   = r2_score(add[2:], add_fitted[2:])
    rmse = float(np.sqrt(mean_squared_error(add[2:], add_fitted[2:])))
    mae  = float(mean_absolute_error(add[2:], add_fitted[2:]))

    # Forecast 5 steps (2026–2030)
    last_diff = d_add[-1]
    fc_adds   = []
    last_add  = float(add[-1])
    for _ in range(5):
        next_diff = mu + phi * last_diff
        next_add  = last_add + next_diff
        fc_adds.append(next_add)
        last_diff = next_diff
        last_add  = next_add

    fc_adds = np.array(fc_adds)
    # Cumulative capacity from FY2025 base
    base_cap = float(HIST_CAP[-1])
    fc_cum   = [base_cap + sum(fc_adds[:i+1]) for i in range(5)]

    return dict(
        add_fitted=add_fitted, fc_adds=fc_adds,
        fc_cum=[round(v, 2) for v in fc_cum],
        years=FORECAST_YEARS,
        r2=round(r2, 4), rmse=round(rmse, 3), mae=round(mae, 3),
        phi=round(phi, 4), mu=round(mu, 4),
    )


def run() -> dict:
    """Train, forecast, plot Figure 5, return results dict."""
    set_style()
    res = train()
    fc_cum  = np.array(res["fc_cum"])
    fc_adds = res["fc_adds"]

    fig = plt.figure(figsize=(13, 7))
    gs  = gridspec.GridSpec(1, 2, figure=fig, wspace=0.32)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # ── Left: Annual Additions (historical + forecast) ────────────────────────
    add_years = HIST_YEARS[1:]
    add_vals  = ADDITIONS[1:]
    ax1.bar(add_years, add_vals, color=NAVY, width=0.68, zorder=3, alpha=0.75,
            label="Historical Annual Additions")
    ax1.bar(FORECAST_YEARS, fc_adds, color=ORANGE, width=0.68, zorder=4,
            label="ARIMA Forecast Additions")
    ax1.plot(add_years, res["add_fitted"][:len(add_years)],
             color=TEAL, lw=2.0, ls="--", zorder=5, label="AR(1) Fitted")

    for yr, v in zip(FORECAST_YEARS, fc_adds):
        ax1.text(yr, v + 0.05, f"{v:.2f}", ha="center",
                 fontsize=8, color=ORANGE, fontweight="bold")

    ax1.axvline(2025.5, color=MGRAY, lw=1.2, ls=":", zorder=1)
    ax1.set_title("Annual Additions: AR(1) Fit & Forecast")
    ax1.set_xlabel("Financial Year End")
    ax1.set_ylabel("Annual Addition (GW/year)")
    xtick_fy(ax1, add_years, step=3, extra=FORECAST_YEARS)
    ax1.set_ylim(0, 14)
    ax1.legend(fontsize=8.5)
    source_note(ax1)
    ax1.text(0.02, 0.97,
             f"φ={res['phi']}  μ={res['mu']}",
             transform=ax1.transAxes, fontsize=8.5, color="#555",
             va="top", style="italic",
             bbox=dict(facecolor="#F4F6F7", edgecolor=MGRAY,
                       boxstyle="round,pad=0.4", alpha=0.85))

    # ── Right: Cumulative Capacity ─────────────────────────────────────────────
    ax2.scatter(HIST_YEARS, HIST_CAP, color=NAVY, s=50, zorder=6,
                label="Actual Data (FY2000–FY2025)")
    ax2.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=1.5, alpha=0.45)
    ax2.plot(FORECAST_YEARS, fc_cum, color=ORANGE, lw=2.6, marker="^",
             ms=8, zorder=7,
             label=f"ARIMA Forecast → 2030: {fc_cum[-1]:.1f} GW")
    ax2.plot([HIST_YEARS[-1], FORECAST_YEARS[0]],
             [HIST_CAP[-1], fc_cum[0]], color=ORANGE, lw=2.6, ls="--")

    # Uncertainty band ±2 std of residuals on additions
    resid_std = float(np.std(np.array(ADDITIONS[3:]) - res["add_fitted"][2:]))
    cum_lo = [HIST_CAP[-1] + sum(fc_adds[:i+1]) - 2*resid_std*(i+1)
              for i in range(5)]
    cum_hi = [HIST_CAP[-1] + sum(fc_adds[:i+1]) + 2*resid_std*(i+1)
              for i in range(5)]
    ax2.fill_between(FORECAST_YEARS, cum_lo, cum_hi,
                     color=ORANGE, alpha=0.12, label="±2 Std band")

    for yr, v in zip(FORECAST_YEARS, fc_cum):
        annotate_val(ax2, yr, v, ORANGE)

    forecast_divider(ax2, x=2025.5, y_txt=3)
    target_lines(ax2)
    source_note(ax2)

    ax2.text(0.98, 0.14,
             f"RMSE: {res['rmse']} GW  |  MAE: {res['mae']} GW",
             transform=ax2.transAxes, fontsize=8, color="#7F8C8D", ha="right")
    ax2.set_title("Cumulative Capacity: ARIMA Forecast (FY2026–FY2030)")
    ax2.set_xlabel("Financial Year End")
    ax2.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax2, np.array(HIST_YEARS), step=3, extra=FORECAST_YEARS)
    ax2.set_ylim(0, 155)
    ax2.legend(loc="upper left", fontsize=9)

    fc30  = fc_cum[-1]
    badge = "AT RISK" if fc30 < TARGET_100 else "LIKELY ACHIEVED"
    status_badge(ax2, badge)

    fig.suptitle(
        "Figure 5 — ARIMA (AR1+Differencing) Forecast: Annual Additions & Cumulative Capacity\n"
        "Data: W1_Final_Objective_Dataset.xlsx (FY2000–FY2025)",
        fontsize=11, fontweight="bold", color=NAVY, y=1.01,
    )

    save_fig(fig, "fig5_arima.png")
    print(f"\n  ARIMA 2030 forecast: {fc30:.2f} GW  [{badge}]")
    print(f"  φ={res['phi']}  μ={res['mu']}")
    print(f"  RMSE={res['rmse']} GW  MAE={res['mae']} GW  R²={res['r2']}")
    return res


if __name__ == "__main__":
    print("\n── Model 3 · ARIMA/AR(1) (W1 Dataset) ─────────────────────")
    run()
