"""
models/arima_model.py
Figure 5 — ARIMA(1,1,1) forecast of India's wind capacity.
Left panel  : annual additions forecast with 80 % CI.
Right panel : cumulative capacity trajectory to FY2030.

Run standalone:  python models/arima_model.py
"""

import sys, os, warnings
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
warnings.filterwarnings("ignore")

import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

from utils import (
    HIST_YEARS, HIST_CAP, ADDITIONS, FORECAST_YEARS, N_FORECAST,
    NAVY, TEAL, ORANGE, RED, MGRAY, LGRAY, TEXT,
    set_style, target_lines, source_note, xtick_fy, status_badge,
    save_fig, fy, TARGET_100,
)

ARIMA_ORDER = (1, 1, 1)


def train() -> dict:
    """
    Fit ARIMA on the annual-additions series (ADDITIONS[1:]).
    Forecast 4 steps ahead.  Integrate to get cumulative capacity.
    """
    add_series = np.array(ADDITIONS[1:], dtype=float)   # FY2000-01–FY2024-25
    add_years  = np.array(HIST_YEARS[1:], dtype=float)

    model  = ARIMA(add_series, order=ARIMA_ORDER).fit()
    fitted = model.fittedvalues

    fc_obj = model.get_forecast(steps=N_FORECAST)
    fc_ann = fc_obj.predicted_mean               # forecast annual additions

    # Confidence interval (80 %)
    ci = fc_obj.conf_int(alpha=0.20)
    if hasattr(ci, "values"):
        ci = ci.values
    else:
        ci = np.array(ci)

    # Integrate additions → cumulative capacity
    base   = HIST_CAP[-1]                        # 56.09 GW
    fc_cum = []
    running = base
    for a in fc_ann:
        running += max(float(a), 0)
        fc_cum.append(round(running, 2))

    lo_cum = np.array([base + sum(max(float(ci[j,0]),0) for j in range(i+1))
                       for i in range(N_FORECAST)])
    hi_cum = np.array([base + sum(max(float(ci[j,1]),0) for j in range(i+1))
                       for i in range(N_FORECAST)])

    r2_add = 1 - np.var(add_series[1:] - fitted[1:]) / np.var(add_series[1:])
    rmse   = round(float(np.sqrt(mean_squared_error(add_series[1:], fitted[1:]))), 3)
    mae    = round(float(mean_absolute_error(add_series[1:], fitted[1:])), 3)

    return dict(
        add_series=add_series, add_years=add_years, fitted=fitted,
        fc_ann=fc_ann, ci=ci,
        fc_cum=fc_cum, lo_cum=lo_cum, hi_cum=hi_cum,
        years=FORECAST_YEARS,
        r2=round(r2_add, 4), rmse=rmse, mae=mae,
    )


def run(plots_dir=None) -> dict:
    """Train, forecast, plot Figure 5 and return results dict."""
    set_style()
    res = train()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # ── Left: Annual additions ─────────────────────────────────────────────────
    ax1.bar(res["add_years"], res["add_series"], color=LGRAY,
            width=0.65, label="Actual Annual Additions", zorder=2)
    ax1.plot(res["add_years"], res["add_series"], color=NAVY,
             lw=1.5, alpha=0.6)
    ax1.plot(res["add_years"], res["fitted"], color=MGRAY,
             lw=1.5, ls="-", alpha=0.8, label="ARIMA Fitted")

    ax1.bar(FORECAST_YEARS, np.maximum(res["fc_ann"], 0),
            color=ORANGE, alpha=0.78, width=0.65,
            label="ARIMA Forecast (GW/yr)", zorder=3)
    ax1.fill_between(FORECAST_YEARS,
                     np.maximum(res["ci"][:, 0], 0),
                     np.maximum(res["ci"][:, 1], 0),
                     color=ORANGE, alpha=0.20, label="80% CI")

    # Label only first and last forecast bars to avoid crowding
    for i, (yr, v) in enumerate(zip(FORECAST_YEARS, res["fc_ann"])):
        if i in (0, len(FORECAST_YEARS)-1):
            ax1.text(yr, max(float(v), 0) + 0.18, f"{max(float(v),0):.2f}",
                     ha="center", fontsize=9, color=ORANGE, fontweight="bold")

    req_100 = round((TARGET_100 - HIST_CAP[-1]) / N_FORECAST, 1)
    ax1.axhline(req_100, color=TEAL, lw=1.8, ls="--",
                label=f"Req. ~{req_100} GW/yr for 100 GW")
    ax1.axvline(HIST_YEARS[-1] + 0.5, color=MGRAY, lw=1, ls=":")
    ax1.set_title("ARIMA(1,1,1) — Annual Addition Forecast")
    ax1.set_xlabel("Financial Year")
    ax1.set_ylabel("Annual Addition (GW/year)")
    xtick_fy(ax1, res["add_years"].astype(int), step=2, extra=FORECAST_YEARS)
    ax1.set_ylim(0, 12)
    ax1.legend(fontsize=8, loc="upper left")

    # ── Right: Cumulative capacity ─────────────────────────────────────────────
    fc_cum = np.array(res["fc_cum"])
    ax2.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=2.4, marker="o",
             ms=4.5, label="Actual Capacity (GW)", zorder=5)
    ax2.plot(FORECAST_YEARS, fc_cum, color=ORANGE, lw=2.6,
             marker="s", ms=7,
             label=f"ARIMA Forecast → 2030: {fc_cum[-1]:.1f} GW", zorder=6)
    ax2.plot([HIST_YEARS[-1], FORECAST_YEARS[0]],
             [HIST_CAP[-1], fc_cum[0]], color=ORANGE, lw=2.6, ls="--")
    ax2.fill_between(FORECAST_YEARS, res["lo_cum"], res["hi_cum"],
                     color=ORANGE, alpha=0.15, label="80% CI band")

    for yr, v in zip(FORECAST_YEARS, fc_cum):
        ax2.annotate(f"{v:.1f}", (yr, v), textcoords="offset points",
                     xytext=(5, 9), fontsize=9, color=ORANGE, fontweight="bold")

    target_lines(ax2)
    ax2.axvline(HIST_YEARS[-1] + 0.5, color=MGRAY, lw=1, ls=":")
    ax2.set_title("ARIMA — Cumulative Capacity Forecast to FY2030")
    ax2.set_xlabel("Financial Year")
    ax2.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax2, np.array(HIST_YEARS), step=2, extra=FORECAST_YEARS)
    ax2.set_ylim(0, 155)
    ax2.legend(loc="upper left", fontsize=8)

    badge = "AT RISK" if fc_cum[-1] < TARGET_100 else "LIKELY ACHIEVED"
    status_badge(ax2, badge)

    fig.suptitle(
        "Figure 5 — ARIMA(1,1,1) Forecast: Annual Additions & Cumulative Capacity (FY2025-26–FY2029-30)",
        fontsize=12, fontweight="bold", color=NAVY, y=1.02,
    )

    save_fig(fig, "fig5_arima.png")
    print(f"\n  ARIMA 2030 forecast: {fc_cum[-1]:.2f} GW  [{badge}]")
    print(f"  R²(additions)={res['r2']}  RMSE={res['rmse']} GW  MAE={res['mae']} GW")
    return dict(forecast=res["fc_cum"], years=FORECAST_YEARS,
                annual_fc=[round(float(v),2) for v in res["fc_ann"]],
                r2=res["r2"], rmse=res["rmse"], mae=res["mae"])


if __name__ == "__main__":
    print("\n── Model 3 · ARIMA(1,1,1) ─────────────────────────────────")
    run()
