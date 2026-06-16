"""
utils.py
Shared data, colour palette, and plot helpers for the
India Wind W1 Forecast project.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

# ── Output directory ──────────────────────────────────────────────────────────
ROOT     = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(ROOT, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

# ── Targets ───────────────────────────────────────────────────────────────────
TARGET_100 = 100.0   # Official MNRE target (GW)
TARGET_140 = 140.0   # Aspirational / planning target (GW)

# ── Historical dataset (Calendar/FY end-year → cumulative GW) ────────────────
# Source: W1_Final_Objective_Dataset.xlsx — W1_Master_Dataset sheet
# "Year" column = FY-end year (Year 2025 == FY2024-25 == 50.04 GW, matches CEA/PIB)
# 26 observed data points: 2000-2025
HIST_YEARS = list(range(2000, 2026))
HIST_CAP   = [
     1.024,  1.161,  1.367,  1.628,  1.870,  2.483,  3.585,  7.114,
     8.098, 10.182, 11.753, 14.089, 17.277, 19.899, 21.077, 23.394,
    26.797, 32.302, 34.13568, 35.626, 37.719, 39.243, 40.324, 42.620,
    45.88545, 50.03782,
]
ADDITIONS  = [
    0.0,    0.137,  0.206,  0.261,  0.242,  0.613,  1.102,  3.529,
    0.984,  2.084,  1.571,  2.336,  3.188,  2.622,  1.178,  2.317,
    3.403,  5.505,  1.83368, 1.49032, 2.093, 1.524,  1.081,  2.296,
    3.26545, 4.15237,
]

# 5-year forecast horizon: FY2025-26 to FY2029-30
FORECAST_YEARS = [2026, 2027, 2028, 2029, 2030]
N_FORECAST     = len(FORECAST_YEARS)   # = 5

# ── Feature / milestone indicators (W1_Feature_Indicators sheet) ─────────────
# (FY label, end-year, short label for plotting)
MILESTONES = [
    ("2011-12", 2012, "821 wind monitoring\nlocations assessed"),
    ("2014-15", 2015, "Repowering\nInitiative started"),
    ("2015-16", 2016, "Forecasting Service\nlaunched"),
    ("2016-17", 2017, "Forecasting cuts\ncurtailment 26%"),
    ("2017-18", 2018, "Offshore LiDAR\noperational"),
    ("2023-24", 2024, "Gulf of Mannar\noffshore survey (108 km²)"),
    ("2024-25", 2025, "SCADA coverage:\n13 substations"),
]

# ── Brand colours ─────────────────────────────────────────────────────────────
NAVY   = "#1B3A5C"
BLUE   = "#2980B9"
TEAL   = "#009688"
ORANGE = "#E07B39"
PURPLE = "#8E44AD"
RED    = "#C0392B"
AMBER  = "#F39C12"
MGRAY  = "#BDC3C7"
LGRAY  = "#F4F6F7"
TEXT   = "#2C3E50"

# ── Financial-year label helper ───────────────────────────────────────────────
def fy(year: int) -> str:
    return f"FY{str(year-1)[2:]}-{str(year)[2:]}"


# ── Global matplotlib style ───────────────────────────────────────────────────
def set_style():
    rcParams.update({
        "font.family":        "DejaVu Sans",
        "axes.facecolor":     "white",
        "figure.facecolor":   "white",
        "axes.grid":          True,
        "grid.color":         MGRAY,
        "grid.linestyle":     "--",
        "grid.alpha":         0.45,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.edgecolor":     MGRAY,
        "axes.titlesize":     12,
        "axes.titleweight":   "bold",
        "axes.titlecolor":    NAVY,
        "axes.labelsize":     10,
        "xtick.labelsize":    8.5,
        "ytick.labelsize":    8.5,
        "legend.fontsize":    8.5,
        "legend.framealpha":  0.9,
    })


# ── Axis helpers ──────────────────────────────────────────────────────────────
def target_lines(ax, label100=True, label140=True):
    if label100:
        ax.axhline(TARGET_100, color=TEAL,   lw=1.8, ls="--", alpha=0.9,
                   label="100 GW Target (MNRE)")
    if label140:
        ax.axhline(TARGET_140, color=ORANGE, lw=1.8, ls="-.", alpha=0.9,
                   label="140 GW Aspirational Target")


def forecast_divider(ax, y_txt=10):
    boundary = HIST_YEARS[-1] + 0.5   # = 2025.5 (between last actual & first forecast)
    ax.axvline(boundary, color=MGRAY, lw=1, ls=":")
    ax.text(boundary + 0.1, y_txt, "← Historical  |  Forecast →",
            fontsize=7.5, color="#7F8C8D", va="bottom")


def source_note(ax, text="Source: W1_Final_Objective_Dataset.xlsx"):
    ax.text(0.02, 0.03, text, transform=ax.transAxes,
            fontsize=7.5, color="#95A5A6", ha="left", va="bottom")


def xtick_fy(ax, years, step=2, extra=None):
    ticks = list(years[::step])
    if extra:
        ticks += extra
    ax.set_xticks(ticks)
    ax.set_xticklabels([fy(y) for y in ticks], rotation=38, ha="right")


def annotate_val(ax, x, y, col, offset=(4, 9)):
    ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points",
                xytext=offset, fontsize=9, color=col, fontweight="bold")


def status_badge(ax, text, x=0.97, y=0.96):
    colors = {
        "ACHIEVED":        TEAL,
        "LIKELY ACHIEVED": "#27AE60",
        "AT RISK":         AMBER,
        "NOT ACHIEVED":    RED,
        "BORDERLINE":      ORANGE,
    }
    c = colors.get(text, "#7F8C8D")
    ax.text(x, y, text, transform=ax.transAxes, fontsize=8.5,
            fontweight="bold", color="white", ha="right", va="top",
            bbox=dict(facecolor=c, alpha=0.9, boxstyle="round,pad=0.3",
                      edgecolor="none"))


# ── Save helper ───────────────────────────────────────────────────────────────
def save_fig(fig, name: str, dpi=180) -> str:
    path = os.path.join(PLOT_DIR, name)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✔  Saved → {name}")
    return path
