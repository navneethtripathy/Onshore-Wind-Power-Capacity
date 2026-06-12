"""
models/model_comparison.py
Figure 8 — Consolidated comparison of all four ML model forecasts
           vs 100 GW and 140 GW targets.

Data: W1_Final_Objective_Dataset.xlsx (W1_Master_Dataset)
Run standalone:  python models/model_comparison.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt

from utils import (
    HIST_YEARS, HIST_CAP, FORECAST_YEARS, TARGET_100, TARGET_140,
    NAVY, BLUE, TEAL, ORANGE, RED, AMBER, MGRAY, TEXT,
    set_style, target_lines, source_note, xtick_fy, status_badge, save_fig,
)

PURPLE = "#8E44AD"


def _collect_results() -> list:
    """Import and run all four models; return list of result dicts."""
    from models.linear_regression     import train as lr_train
    from models.polynomial_regression import train as poly_train
    from models.arima_model            import train as arima_train
    from models.holt_model             import train as holt_train

    lr   = lr_train()
    poly = poly_train()
    ar   = arima_train()
    holt = holt_train()

    return [
        dict(name="Linear Regression",        short="Linear\nReg.",
             forecast=lr["forecast"],         color=BLUE,   ls="-",
             r2=lr["r2"],     rmse=lr["rmse"]),
        dict(name="Polynomial Reg. (Deg-3)",   short="Poly\nReg.",
             forecast=poly["forecast"],       color=TEAL,   ls="-.",
             r2=poly["r2"],   rmse=poly["rmse"]),
        dict(name="ARIMA / AR(1)",             short="ARIMA\n/AR(1)",
             forecast=ar["fc_cum"],           color=ORANGE, ls="--",
             r2=ar["r2"],     rmse=ar["rmse"]),
        dict(name="Holt Exp. Smoothing",       short="Holt\nSmoothing",
             forecast=holt["forecast"],       color=PURPLE, ls=":",
             r2=holt["r2"],   rmse=holt["rmse"]),
    ]


def run(results=None) -> None:
    if results is None:
        results = _collect_results()

    set_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5))

    # ── Left: Trajectory comparison ───────────────────────────────────────────
    ax1.scatter(HIST_YEARS, HIST_CAP, color=NAVY, s=35, alpha=0.65, zorder=6)
    ax1.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=2.2, alpha=0.65,
             label="Historical Actual (W1 Dataset)")

    for res in results:
        fc  = np.array(res["forecast"])
        ax1.plot(FORECAST_YEARS, fc, color=res["color"], lw=2.3,
                 ls=res["ls"], marker="^", ms=5.5,
                 label=f"{res['name']}  →FY2030: {fc[-1]:.1f} GW")
        ax1.plot([HIST_YEARS[-1], FORECAST_YEARS[0]],
                 [HIST_CAP[-1], fc[0]], color=res["color"], lw=2.3, ls=res["ls"])

    target_lines(ax1)
    ax1.axvline(2025.5, color=MGRAY, lw=1, ls=":")
    ax1.text(2025.6, 6, "← Historical  |  Forecast →",
             fontsize=7.5, color="#7F8C8D", va="bottom")
    ax1.set_title("All Model Forecasts vs Targets (FY2026–FY2030)")
    ax1.set_xlabel("Financial Year End")
    ax1.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax1, np.array(HIST_YEARS), step=3, extra=FORECAST_YEARS)
    ax1.set_ylim(0, 155)
    ax1.legend(fontsize=7.5, loc="upper left")
    source_note(ax1)

    # ── Right: 2030 bar comparison ────────────────────────────────────────────
    fc2030 = [float(np.array(r["forecast"])[-1]) for r in results]
    labels = [r["short"] for r in results]
    colors = [r["color"] for r in results]

    bars = ax2.bar(range(4), fc2030, color=colors, width=0.55,
                   edgecolor="white", linewidth=1.8, zorder=3)
    for bar, val in zip(bars, fc2030):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.9,
                 f"{val:.1f} GW", ha="center", fontsize=11,
                 fontweight="bold", color=TEXT)

    ax2.axhline(TARGET_100, color=TEAL, lw=2.3, ls="--",
                label=f"100 GW Target", zorder=4)
    ax2.axhline(TARGET_140, color=RED,  lw=1.8, ls="-.",
                label=f"140 GW Target", zorder=4)
    ax2.fill_between([-0.5, 3.5], [TARGET_100]*2, [155]*2,
                     color=TEAL, alpha=0.06, label="Above 100 GW zone")
    ax2.fill_between([-0.5, 3.5], [0]*2, [TARGET_100]*2,
                     color="#FADBD8", alpha=0.20, label="Gap zone")

    for i, val in enumerate(fc2030):
        gap = TARGET_100 - val
        if gap > 0:
            ax2.annotate("", xy=(i, TARGET_100), xytext=(i, val + 0.5),
                         arrowprops=dict(arrowstyle="<->", color="#888", lw=1.3))
            ax2.text(i + 0.28, (val + TARGET_100) / 2,
                     f"−{gap:.1f}", fontsize=8.5, color=RED,
                     fontweight="bold", va="center")

    for i, val in enumerate(fc2030):
        if   val >= TARGET_100:           badge, c = "ACHIEVED",   TEAL
        elif val >= TARGET_100 * 0.95:    badge, c = "BORDERLINE", AMBER
        else:                             badge, c = "AT RISK",     RED
        ax2.text(i, 2.5, badge, ha="center", fontsize=7.5,
                 fontweight="bold", color="white",
                 bbox=dict(facecolor=c, alpha=0.9,
                           boxstyle="round,pad=0.25", edgecolor="none"))

    ax2.set_xticks(range(4))
    ax2.set_xticklabels(labels, fontsize=9.5)
    ax2.set_ylabel("Forecast FY2030 Capacity (GW)")
    ax2.set_ylim(0, 155)
    ax2.legend(fontsize=8.5, loc="upper right")
    ax2.set_title("FY2030 Forecast: All Models vs Targets")

    # Model accuracy table
    rows = [[r["name"], f"{r['r2']}", f"{r['rmse']} GW",
             f"{float(np.array(r['forecast'])[-1]):.1f} GW"]
            for r in results]
    col_labels = ["Model", "R²", "RMSE", "FY2030 FC"]
    table = ax2.table(cellText=rows, colLabels=col_labels,
                      bbox=[0.0, -0.42, 1.0, 0.32], cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    for j in range(4):
        table[0, j].set_facecolor(NAVY)
        table[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, 5):
        for j in range(4):
            table[i, j].set_facecolor("#F4F6F7" if i % 2 == 0 else "white")

    fig.suptitle(
        "Figure 8 — Consolidated ML Forecast Comparison: All Models vs 100 GW & 140 GW Targets\n"
        "Data: W1_Final_Objective_Dataset.xlsx | Base: 50.04 GW (FY2024-25)",
        fontsize=11, fontweight="bold", color=NAVY, y=1.02,
    )
    fig.subplots_adjust(bottom=0.28)

    save_fig(fig, "fig8_all_models.png")
    print("\n  ── FY2030 Summary (W1 Dataset) ──────────────────────────")
    for r in results:
        fc  = float(np.array(r["forecast"])[-1])
        gap = TARGET_100 - fc
        print(f"  {r['name']:30s}: {fc:.2f} GW  gap={gap:+.1f} GW  R²={r['r2']}")


if __name__ == "__main__":
    print("\n── Figure 8 · All Models Comparison (W1 Dataset) ──────────")
    run()
