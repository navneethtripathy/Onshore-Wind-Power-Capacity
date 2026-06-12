"""
models/historical_growth.py
Figure 1 — Installed Capacity Growth (FY2000–FY2025)
Figure 2 — Annual Capacity Additions with required rates

Data: W1_Final_Objective_Dataset.xlsx (W1_Master_Dataset)
Run standalone:  python models/historical_growth.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from utils import (
    HIST_YEARS, HIST_CAP, ADDITIONS, FORECAST_YEARS,
    NAVY, TEAL, ORANGE, RED, MGRAY, TEXT, LGRAY,
    set_style, target_lines, source_note, xtick_fy, save_fig, fy,
    TARGET_100, TARGET_140,
)

# Recent acceleration window (last 6 data points from W1 dataset)
RECENT_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
RECENT_CAP   = [37.719, 39.243, 40.324, 42.620, 45.885, 50.038]


def figure1_capacity_growth():
    """Line chart: cumulative installed capacity FY2000–FY2025 (W1 dataset)."""
    set_style()
    fig, ax = plt.subplots(figsize=(12, 6.5))

    ax.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=2.4, marker="o",
            ms=4.5, zorder=5, label="Cumulative Installed Capacity (GW)")
    ax.fill_between(HIST_YEARS, HIST_CAP, alpha=0.07, color=NAVY)

    # Highlight recent acceleration
    ax.plot(RECENT_YEARS, RECENT_CAP, color=TEAL, lw=3.2,
            marker="D", ms=7, zorder=6, label="Recent Acceleration (FY2020–FY2025)")
    for yr, cap in zip(RECENT_YEARS[-4:], RECENT_CAP[-4:]):
        ax.annotate(f"{cap:.3f}", (yr, cap),
                    textcoords="offset points", xytext=(4, 10),
                    fontsize=8.5, color=NAVY, fontweight="bold")

    # Key event annotations
    ax.annotate("Policy-transition\nslowdown\n(FY2018–FY2022)",
                xy=(2020, 37.7), xytext=(2013, 42),
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.3),
                fontsize=8, color=ORANGE)
    ax.annotate("Record addition\n3.53 GW (FY2007)",
                xy=(2007, 7.114), xytext=(2002, 14),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.3),
                fontsize=8, color=TEAL)
    ax.annotate("5.50 GW record\n(FY2017)",
                xy=(2017, 32.302), xytext=(2013, 37),
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.3),
                fontsize=8, color=ORANGE)
    ax.annotate(f"Latest: {HIST_CAP[-1]:.3f} GW\n(FY2024-25)",
                xy=(2025, HIST_CAP[-1]), xytext=(2021, 46),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.3),
                fontsize=8.5, color=TEAL, fontweight="bold")

    ax.set_title("Figure 1 — India Installed Wind Capacity Growth (FY2000–FY2025)\n"
                 "Source: W1_Final_Objective_Dataset.xlsx | MNRE / CEA / PIB", pad=12)
    ax.set_xlabel("Financial Year End")
    ax.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax, HIST_YEARS, step=2)
    ax.set_ylim(0, 68)
    ax.legend(loc="upper left", fontsize=9)
    source_note(ax)

    return save_fig(fig, "fig1_capacity_growth.png")


def figure2_annual_additions():
    """Bar chart: annual additions with required-rate reference lines."""
    set_style()
    fig, ax = plt.subplots(figsize=(12, 6.5))

    add_years = HIST_YEARS[1:]          # 2001–2025
    add_vals  = ADDITIONS[1:]
    bar_colors = [TEAL if yr >= 2022 else NAVY for yr in add_years]

    bars = ax.bar(add_years, add_vals, color=bar_colors, width=0.68, zorder=3)

    # Label notable bars
    for bar, val, yr in zip(bars, add_vals, add_years):
        if val >= 2.5 or yr >= 2022:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.04,
                    f"{val:.2f}", ha="center", fontsize=8,
                    color=NAVY, fontweight="bold")

    # Required-rate reference lines
    current_gw = HIST_CAP[-1]  # 50.038 GW (FY2024-25)
    years_left = 5             # FY2026–FY2030
    req_100 = (TARGET_100 - current_gw) / years_left
    req_140 = (TARGET_140 - current_gw) / years_left

    ax.axhline(req_100, color=TEAL, lw=2.0, ls="--",
               label=f"Required for 100 GW ≈ {req_100:.1f} GW/yr")
    ax.axhline(req_140, color=RED,  lw=1.8, ls="-.",
               label=f"Required for 140 GW ≈ {req_140:.1f} GW/yr")

    legend_patches = [
        mpatches.Patch(facecolor=NAVY, label="Historical (FY2001–FY2021)"),
        mpatches.Patch(facecolor=TEAL, label="Recent Acceleration (FY2022–FY2025)"),
        Line2D([0],[0], color=TEAL, ls="--", lw=2.0,
               label=f"Req. for 100 GW (~{req_100:.1f} GW/yr)"),
        Line2D([0],[0], color=RED,  ls="-.", lw=1.8,
               label=f"Req. for 140 GW (~{req_140:.1f} GW/yr)"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=8.5)

    ax.set_title("Figure 2 — Annual Wind Capacity Additions (FY2001–FY2025) vs Required Rates\n"
                 "Source: W1_Final_Objective_Dataset.xlsx | MNRE / CEA", pad=12)
    ax.set_xlabel("Financial Year End")
    ax.set_ylabel("Annual Addition (GW/year)")
    xtick_fy(ax, add_years, step=2)
    ax.set_ylim(0, 12.5)
    source_note(ax)

    return save_fig(fig, "fig2_annual_additions.png")


if __name__ == "__main__":
    print("\n── Historical Growth Figures ──────────────────────────────")
    figure1_capacity_growth()
    figure2_annual_additions()
    print("\n  Done.")
