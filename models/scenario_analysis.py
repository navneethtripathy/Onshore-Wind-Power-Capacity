"""
models/scenario_analysis.py
Figure 7 — Scenario Analysis: wind capacity trajectories for different
           annual addition rates, benchmarked against 100 GW and 140 GW.

Data: W1_Final_Objective_Dataset.xlsx (W1_Master_Dataset)
Base capacity: 50.038 GW (FY2024-25)

Scenarios modelled
──────────────────
  Conservative  :  6.0 GW/yr  (close to recent peak additions)
  Moderate      :  8.0 GW/yr
  Accelerated   : 10.0 GW/yr
  100-GW path   : ~10.0 GW/yr  (exact requirement from 50.04 GW base)
  140-GW path   : ~18.0 GW/yr  (exact requirement)

Run standalone:  python models/scenario_analysis.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from utils import (
    HIST_YEARS, HIST_CAP, FORECAST_YEARS, TARGET_100, TARGET_140,
    NAVY, BLUE, TEAL, ORANGE, RED, MGRAY, TEXT,
    set_style, source_note, xtick_fy, save_fig,
)


def build_scenarios(base: float) -> dict:
    req_100 = (TARGET_100 - base) / len(FORECAST_YEARS)
    req_140 = (TARGET_140 - base) / len(FORECAST_YEARS)
    return {
        "Conservative\n(6 GW/yr)":            dict(rate=6.0,     color=BLUE,   ls="-"),
        "Moderate\n(8 GW/yr)":                dict(rate=8.0,     color=TEAL,   ls="-"),
        "Accelerated\n(10 GW/yr)":            dict(rate=10.0,    color=ORANGE, ls="-"),
        f"100 GW Path\n({req_100:.1f} GW/yr)": dict(rate=req_100, color=NAVY,   ls="--"),
        f"140 GW Path\n({req_140:.1f} GW/yr)": dict(rate=req_140, color=RED,    ls="--"),
    }


def run() -> None:
    set_style()
    base      = float(HIST_CAP[-1])   # 50.038 GW
    scenarios = build_scenarios(base)

    fig, ax = plt.subplots(figsize=(13, 7))

    # Historical
    ax.scatter(HIST_YEARS, HIST_CAP, color=NAVY, s=30, alpha=0.65, zorder=5)
    ax.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=2.2, alpha=0.65,
            label="Historical Actual (W1 Dataset)")

    # Scenario trajectories
    for name, cfg in scenarios.items():
        vals       = [base + cfg["rate"] * (i + 1) for i in range(5)]
        label_str  = name.replace("\n", " ") + f"  →FY2030: {vals[-1]:.1f} GW"
        ax.plot(FORECAST_YEARS, vals, color=cfg["color"],
                lw=2.3, ls=cfg["ls"], marker="o", ms=5.5, label=label_str)
        ax.plot([HIST_YEARS[-1], FORECAST_YEARS[0]], [base, vals[0]],
                color=cfg["color"], lw=2.3, ls=cfg["ls"])
        ax.text(FORECAST_YEARS[-1] + 0.12, vals[-1],
                f"{vals[-1]:.0f}", fontsize=8.5, color=cfg["color"],
                va="center", fontweight="bold")

    # Likely-range shading
    mod = [base + 8.0  * (i+1) for i in range(5)]
    acc = [base + 10.0 * (i+1) for i in range(5)]
    ax.fill_between(FORECAST_YEARS, mod, acc,
                    color=TEAL, alpha=0.08, label="Likely range (8–10 GW/yr)")

    # Target lines
    ax.axhline(TARGET_100, color=TEAL, lw=2.0, ls=":", alpha=0.9)
    ax.axhline(TARGET_140, color=RED,  lw=1.8, ls=":", alpha=0.9)
    ax.text(2027.05, TARGET_100 + 1.5, "100 GW Target (MNRE)",
            fontsize=9, color=TEAL, fontweight="bold")
    ax.text(2027.05, TARGET_140 + 1.5, "140 GW Aspirational Target",
            fontsize=9, color=RED,  fontweight="bold")

    # Gap annotation
    likely_2030 = base + 9.0 * 5
    ax.annotate("",
                xy=(2030, TARGET_100), xytext=(2030, likely_2030),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=1.3))
    ax.text(2030.18, (TARGET_100 + likely_2030) / 2,
            f"Gap\n~{TARGET_100-likely_2030:.0f} GW",
            fontsize=8.5, color="#555", va="center", fontweight="bold")

    ax.axvline(2025.5, color=MGRAY, lw=1, ls=":")
    ax.text(2025.6, 8, "← Historical  |  Forecast →",
            fontsize=7.5, color="#7F8C8D", va="bottom")

    ax.set_title("Figure 7 — Scenario Analysis: India Wind Capacity Trajectories (FY2026–FY2030)\n"
                 "Base: 50.04 GW (FY2024-25) | W1_Final_Objective_Dataset.xlsx",
                 pad=12)
    ax.set_xlabel("Financial Year End")
    ax.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax, np.array(HIST_YEARS), step=3, extra=FORECAST_YEARS)
    ax.set_xlim(1999, 2031.5)
    ax.set_ylim(0, 155)
    ax.legend(loc="upper left", fontsize=7.8, ncol=1)
    source_note(ax)

    save_fig(fig, "fig7_scenario.png")
    print("\n  Scenario analysis FY2030 projections (base: 50.04 GW):")
    for name, cfg in scenarios.items():
        vals = [base + cfg["rate"] * (i+1) for i in range(5)]
        n    = name.replace("\n"," ")
        print(f"    {n:38s}: {vals[-1]:.1f} GW")


if __name__ == "__main__":
    print("\n── Scenario Analysis (W1 Dataset) ─────────────────────────")
    run()
