"""
models/historical_growth.py
Figure 1 — Installed Capacity Growth (FY2000-01 to FY2024-25) with
            NIWE/MNRE numbered milestone markers and clean legend table.
Figure 2 — Annual Capacity Additions with required rates for 100/140 GW.
Run standalone:  python models/historical_growth.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

from utils import (
    HIST_YEARS, HIST_CAP, ADDITIONS, FORECAST_YEARS, MILESTONES, N_FORECAST,
    NAVY, TEAL, ORANGE, RED, MGRAY, TEXT, LGRAY,
    set_style, source_note, xtick_fy, save_fig, fy,
    TARGET_100, TARGET_140,
)

RECENT_YEARS = HIST_YEARS[-6:]
RECENT_CAP   = HIST_CAP[-6:]


def figure1_capacity_growth(plots_dir=None):
    """Line chart with clean numbered milestone markers and legend table."""
    set_style()
    fig = plt.figure(figsize=(13, 7.5))
    gs  = gridspec.GridSpec(2, 1, height_ratios=[5.5, 1], hspace=0.08)
    ax  = fig.add_subplot(gs[0])
    ax_tbl = fig.add_subplot(gs[1])
    ax_tbl.axis("off")

    # Main line
    ax.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=2.2, marker="o",
            ms=4, zorder=5, label="Cumulative Installed Capacity (GW)")
    ax.fill_between(HIST_YEARS, HIST_CAP, alpha=0.07, color=NAVY)

    # Recent highlight
    ax.plot(RECENT_YEARS, RECENT_CAP, color=TEAL, lw=3.0,
            marker="D", ms=7, zorder=6, label="Recent Period (FY20–FY25)")
    for yr, cap in zip(RECENT_YEARS[-3:], RECENT_CAP[-3:]):
        ax.annotate(f"{cap:.1f}", (yr, cap), textcoords="offset points",
                    xytext=(2, 10), fontsize=8, color=NAVY, fontweight="bold")

    # Numbered milestone star markers
    milestone_colors = ["#E07B39","#C0392B","#8E44AD","#2980B9","#009688","#E67E22","#1B3A5C"]
    table_rows = []
    for idx, ((fy_lbl, end_yr, label), mc) in enumerate(zip(MILESTONES, milestone_colors), start=1):
        cap_val = HIST_CAP[HIST_YEARS.index(end_yr)]
        ax.scatter(end_yr, cap_val, marker="*", s=180, color=mc,
                   edgecolors="white", linewidths=0.8, zorder=9)
        ax.text(end_yr, cap_val + 2.2, str(idx), fontsize=7.5,
                ha="center", va="bottom", fontweight="bold", color=mc,
                bbox=dict(boxstyle="circle,pad=0.15", facecolor="white",
                          edgecolor=mc, linewidth=0.8, alpha=0.9))
        table_rows.append([f"★{idx}", fy_lbl, f"{cap_val:.1f} GW", label.replace("\n", " ")])

    ax.set_title("Figure 1 — India Installed Wind Capacity Growth (FY2000-01 to FY2024-25)\n"
                 "with NIWE/MNRE Infrastructure & Capability Milestones", pad=10)
    ax.set_xlabel("Financial Year")
    ax.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax, np.array(HIST_YEARS), step=3)
    ax.set_ylim(-3, 62)
    ax.set_xlim(1999, 2026.5)
    ax.legend(loc="upper left", fontsize=9)
    source_note(ax)

    # Milestone legend table at bottom
    col_labels = ["#", "FY", "Capacity", "Milestone"]
    col_widths  = [0.06, 0.12, 0.12, 0.70]
    tbl = ax_tbl.table(
        cellText=table_rows, colLabels=col_labels,
        cellLoc="left", loc="center",
        bbox=[0.0, 0.0, 1.0, 1.0],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.8)
    for j in range(4):
        tbl[0, j].set_facecolor(NAVY)
        tbl[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, len(table_rows)+1):
        for j in range(4):
            tbl[i, j].set_facecolor("#F4F6F7" if i % 2 == 0 else "white")
        tbl[i, 0].set_text_props(color=milestone_colors[i-1], fontweight="bold")
    for j, w in enumerate(col_widths):
        tbl.auto_set_column_width(j)

    fig.patch.set_facecolor("white")
    return save_fig(fig, "fig1_capacity_growth.png")


def figure2_annual_additions(plots_dir=None):
    """Bar chart: annual additions with required-rate reference lines."""
    set_style()
    fig, ax = plt.subplots(figsize=(13, 6.5))

    add_years = HIST_YEARS[1:]
    add_vals  = ADDITIONS[1:]
    bar_colors = [TEAL if yr >= 2021 else NAVY for yr in add_years]

    bars = ax.bar(add_years, add_vals, color=bar_colors, width=0.68, zorder=3)

    for bar, val, yr in zip(bars, add_vals, add_years):
        if val >= 2.0 or yr >= 2021:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.12,
                    f"{val:.2f}", ha="center", fontsize=8,
                    color=NAVY, fontweight="bold")

    base    = HIST_CAP[-1]
    req_100 = (TARGET_100 - base) / N_FORECAST
    req_140 = (TARGET_140 - base) / N_FORECAST
    ax.axhline(req_100, color=TEAL, lw=2.0, ls="--")
    ax.axhline(req_140, color=RED,  lw=1.8, ls="-.")

    # Annotate the lines on the right edge
    ax.text(2025.4, req_100 + 0.25, f"Req. for 100 GW: {req_100:.1f} GW/yr",
            fontsize=8.5, color=TEAL, fontweight="bold", ha="right")
    ax.text(2025.4, req_140 + 0.25, f"Req. for 140 GW: {req_140:.1f} GW/yr",
            fontsize=8.5, color=RED, fontweight="bold", ha="right")

    legend_patches = [
        mpatches.Patch(facecolor=NAVY, label="Historical (FY01–FY20)"),
        mpatches.Patch(facecolor=TEAL, label="Recent Period (FY21–FY25)"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=9)

    ax.set_title("Figure 2 — Annual Wind Capacity Additions (FY2000-01 to FY2024-25)\n"
                 "vs Required Rates for 100 GW / 140 GW by FY2029-30", pad=12)
    ax.set_xlabel("Financial Year")
    ax.set_ylabel("Annual Addition (GW/year)")
    xtick_fy(ax, np.array(HIST_YEARS), step=3)
    ax.set_ylim(0, 22)
    ax.set_xlim(2000.2, 2025.8)
    source_note(ax)
    return save_fig(fig, "fig2_annual_additions.png")


if __name__ == "__main__":
    print("\n── Historical Growth Figures ────────────────────────────────")
    figure1_capacity_growth()
    figure2_annual_additions()
