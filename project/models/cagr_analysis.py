"""
models/cagr_analysis.py
Figure 9 — CAGR Analysis: Historical growth rates vs rates required to
            meet 100 GW and 140 GW targets by FY2030.

Data: W1_Final_Objective_Dataset.xlsx (W1_Master_Dataset)
Run standalone:  python models/cagr_analysis.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt

from utils import (
    HIST_YEARS, HIST_CAP, TARGET_100, TARGET_140,
    NAVY, BLUE, TEAL, ORANGE, RED, TEXT, MGRAY,
    set_style, save_fig,
)


def cagr(start: float, end: float, n: int) -> float:
    """Return CAGR as a percentage."""
    return ((end / start) ** (1 / n) - 1) * 100


def compute_cagr() -> dict:
    """Compute CAGR values from W1 dataset."""
    # W1 data points
    cap_2000 = HIST_CAP[0]   # 1.024 GW (year index 0 = 2000)
    cap_2016 = HIST_CAP[16]  # 26.797 GW (index 16 = 2016)
    cap_2021 = HIST_CAP[21]  # 39.243 GW (index 21 = 2021)
    cap_2023 = HIST_CAP[23]  # 42.620 GW (index 23 = 2023)
    current  = HIST_CAP[-1]  # 50.038 GW (FY2024-25)

    return {
        "overall_25yr": cagr(cap_2000,  current, 25),   # FY2000–FY2025
        "decade_9yr":   cagr(cap_2016,  current,  9),   # FY2016–FY2025
        "5yr":          cagr(cap_2021,  current,  4),   # FY2021–FY2025 (4 steps)
        "2yr":          cagr(cap_2023,  current,  2),   # FY2023–FY2025
        "required_100": cagr(current, TARGET_100, 5),   # FY2025–FY2030
        "required_140": cagr(current, TARGET_140, 5),   # FY2025–FY2030
    }


def run() -> dict:
    """Generate Figure 9 and return CAGR dict."""
    set_style()
    data = compute_cagr()

    hist_labels = [
        "Overall\nFY00–FY25\n(25 yr)",
        "Decade\nFY16–FY25\n(9 yr)",
        "5-Year\nFY21–FY25\n(4 yr)",
        "2-Year\nFY23–FY25\n(2 yr)",
    ]
    hist_values = [data["overall_25yr"], data["decade_9yr"],
                   data["5yr"], data["2yr"]]
    hist_colors = [NAVY, BLUE, TEAL, ORANGE]

    req_labels = ["5-Year\nCAGR\n(baseline)", "Required\nfor 100 GW", "Required\nfor 140 GW"]
    req_values = [data["5yr"], data["required_100"], data["required_140"]]
    req_colors = [TEAL, ORANGE, RED]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5))

    # ── Left: Historical CAGRs ─────────────────────────────────────────────────
    bars1 = ax1.bar(range(4), hist_values, color=hist_colors,
                    width=0.52, edgecolor="white", lw=1.5, zorder=3)
    for bar, val in zip(bars1, hist_values):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                 f"{val:.1f}%", ha="center", fontsize=12, fontweight="bold", color=TEXT)
    ax1.set_xticks(range(4))
    ax1.set_xticklabels(hist_labels, fontsize=9)
    ax1.set_title("Historical CAGR by Period (W1 Dataset)")
    ax1.set_ylabel("Compound Annual Growth Rate (%)")
    ax1.set_ylim(0, max(hist_values) * 1.3)
    ax1.text(0.02, 0.97,
             "CAGR = (End / Start)^(1/n) − 1\nBase: 50.04 GW (FY2024-25)",
             transform=ax1.transAxes, fontsize=8.5, color="#7F8C8D",
             va="top", style="italic",
             bbox=dict(facecolor="#F4F6F7", edgecolor=MGRAY,
                       boxstyle="round,pad=0.4", alpha=0.8))

    # ── Right: Required CAGRs vs baseline ─────────────────────────────────────
    bars2 = ax2.bar(range(3), req_values, color=req_colors,
                    width=0.52, edgecolor="white", lw=1.5, zorder=3)
    for bar, val in zip(bars2, req_values):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 f"{val:.1f}%", ha="center", fontsize=12, fontweight="bold", color=TEXT)

    baseline = data["5yr"]
    for i, val in enumerate(req_values[1:], start=1):
        gap = val - baseline
        ax2.annotate("",
                     xy=(i, val), xytext=(i, baseline),
                     arrowprops=dict(arrowstyle="<->", color="#7F8C8D", lw=1.3))
        ax2.text(i + 0.28, (val + baseline) / 2,
                 f"+{gap:.1f} pp\nneeded", fontsize=8, color="#555", va="center")

    ax2.axhline(baseline, color=TEAL, lw=1.6, ls="--",
                label=f"5-Yr Baseline: {baseline:.1f}%")
    ax2.set_xticks(range(3))
    ax2.set_xticklabels(req_labels, fontsize=9)
    ax2.set_title("Required CAGR vs Baseline to Hit 2030 Targets")
    ax2.set_ylabel("Required Annual CAGR (%)")
    ax2.set_ylim(0, max(req_values) * 1.25)
    ax2.legend(fontsize=9)

    fig.suptitle(
        "Figure 9 — CAGR Analysis: Historical Growth vs Required Growth for 2030 Targets\n"
        "Data: W1_Final_Objective_Dataset.xlsx | Base Capacity: 50.04 GW (FY2024-25)",
        fontsize=11, fontweight="bold", color=NAVY, y=1.02,
    )

    save_fig(fig, "fig9_cagr.png")
    return data


if __name__ == "__main__":
    print("\n── CAGR Analysis (W1 Dataset) ──────────────────────────────")
    d = run()
    print(f"\n  Results:")
    for k, v in d.items():
        print(f"    {k:20s}: {v:.2f}%")
