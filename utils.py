"""
utils.py — Shared constants, colour palette, style helpers, and save utility.
All data sourced from W1_Final_Objective_Dataset.xlsx (W1_Master_Dataset sheet).
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Output directory ──────────────────────────────────────────────────────────
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# ── Dataset — W1_Final_Objective_Dataset.xlsx (W1_Master_Dataset) ─────────────
# Years mapped to FY end integer (FY2006-07 → 2007, etc.)
# Source: MNRE / CEA / PIB 2026
HIST_YEARS = list(range(2000, 2026))   # 2000..2025 (FY ends: 2000=FY99-00)

# Installed capacity in GW (converted from MW ÷ 1000)
_CAP_MW = [
    1024,     # 2000
    1161,     # 2001
    1367,     # 2002
    1628,     # 2003
    1870,     # 2004
    2483,     # 2005
    3585,     # 2006
    7114,     # 2007
    8098,     # 2008
    10182,    # 2009
    11753,    # 2010
    14089,    # 2011
    17277,    # 2012
    19899,    # 2013
    21077,    # 2014
    23394,    # 2015
    26797,    # 2016
    32302,    # 2017
    34135.68, # 2018
    35626,    # 2019
    37719,    # 2020
    39243,    # 2021
    40324,    # 2022
    42620,    # 2023
    45885.45, # 2024
    50037.82, # 2025
]
HIST_CAP = [round(mw / 1000, 3) for mw in _CAP_MW]  # GW

# Annual additions (GW) — year-on-year difference
_ADD_MW = [
    0,          # 2000 (no prior)
    137,        # 2001
    206,        # 2002
    261,        # 2003
    242,        # 2004
    613,        # 2005
    1102,       # 2006
    3529,       # 2007
    984,        # 2008
    2084,       # 2009
    1571,       # 2010
    2336,       # 2011
    3188,       # 2012
    2622,       # 2013
    1178,       # 2014
    2317,       # 2015
    3403,       # 2016
    5505,       # 2017
    1833.68,    # 2018
    1490.32,    # 2019
    2093,       # 2020
    1524,       # 2021
    1081,       # 2022
    2296,       # 2023
    3265.45,    # 2024
    4152.37,    # 2025
]
ADDITIONS = [round(mw / 1000, 3) for mw in _ADD_MW]  # GW

# Targets from W1 Targets_and_Gaps sheet
TARGET_100 = 100.0   # Conservative 2030 target (GW)
TARGET_140 = 140.0   # Ambitious 2030 target (GW)
CURRENT_2025 = 50.038  # GW (FY2024-25 per dataset)

# Forecast years: 2026–2030 (FY2025-26 to FY2029-30)
FORECAST_YEARS = [2026, 2027, 2028, 2029, 2030]

# ── Colour palette ────────────────────────────────────────────────────────────
NAVY   = "#1B3A6B"
BLUE   = "#2980B9"
TEAL   = "#1ABC9C"
ORANGE = "#E67E22"
RED    = "#E74C3C"
AMBER  = "#F39C12"
MGRAY  = "#BDC3C7"
LGRAY  = "#ECF0F1"
TEXT   = "#2C3E50"

# ── Style ─────────────────────────────────────────────────────────────────────
def set_style():
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor":   "#F8FAFC",
        "axes.edgecolor":   MGRAY,
        "axes.grid":        True,
        "grid.color":       MGRAY,
        "grid.linestyle":   "--",
        "grid.linewidth":   0.55,
        "grid.alpha":       0.6,
        "font.family":      "DejaVu Sans",
        "font.size":        10,
        "axes.titlesize":   11,
        "axes.titleweight": "bold",
        "axes.titlecolor":  NAVY,
        "axes.labelcolor":  TEXT,
        "xtick.color":      TEXT,
        "ytick.color":      TEXT,
        "legend.framealpha": 0.9,
        "legend.edgecolor": MGRAY,
        "figure.dpi":       150,
        "savefig.dpi":      150,
        "savefig.bbox":     "tight",
        "savefig.facecolor": "white",
    })


# ── Helpers ───────────────────────────────────────────────────────────────────
def fy(year: int) -> str:
    """Convert year integer to FY label, e.g. 2017 → 'FY17'."""
    return f"FY{str(year)[2:]}"


def xtick_fy(ax, years, step=2, extra=None):
    all_years = list(years)
    if extra:
        all_years = sorted(set(all_years) | set(extra))
    ticks = [y for y in all_years if (y - all_years[0]) % step == 0]
    ax.set_xticks(ticks)
    ax.set_xticklabels([fy(y) for y in ticks], fontsize=8.5, rotation=45, ha="right")


def target_lines(ax):
    ax.axhline(TARGET_100, color=TEAL, lw=1.8, ls="--", alpha=0.85, zorder=2)
    ax.axhline(TARGET_140, color=RED,  lw=1.5, ls="-.", alpha=0.85, zorder=2)
    ax.text(HIST_YEARS[0] + 0.3, TARGET_100 + 1.5,
            f"100 GW Target (MNRE)", fontsize=8.5, color=TEAL, fontweight="bold")
    ax.text(HIST_YEARS[0] + 0.3, TARGET_140 + 1.5,
            f"140 GW Aspirational", fontsize=8.5, color=RED,  fontweight="bold")


def forecast_divider(ax, x=2025.5, y_txt=6):
    ax.axvline(x, color=MGRAY, lw=1.2, ls=":", zorder=1)
    ax.text(x + 0.12, y_txt, "← Historical  |  Forecast →",
            fontsize=7.5, color="#7F8C8D", va="bottom")


def source_note(ax):
    ax.text(0.99, 0.01,
            "Source: W1_Final_Objective_Dataset.xlsx | MNRE / CEA / PIB 2026",
            transform=ax.transAxes, fontsize=7, color="#95A5A6",
            ha="right", va="bottom")


def annotate_val(ax, x, y, color, offset=(4, 8)):
    ax.annotate(f"{y:.1f}", (x, y),
                textcoords="offset points", xytext=offset,
                fontsize=8.5, color=color, fontweight="bold")


def status_badge(ax, text, x=0.98, y=0.97):
    color = RED if "RISK" in text or "NOT" in text else TEAL
    ax.text(x, y, f"  {text}  ",
            transform=ax.transAxes, fontsize=9, fontweight="bold",
            color="white", ha="right", va="top",
            bbox=dict(facecolor=color, alpha=0.92,
                      boxstyle="round,pad=0.4", edgecolor="none"))


def save_fig(fig, filename: str) -> str:
    path = os.path.join(PLOTS_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✔  Saved → {path}")
    return path
