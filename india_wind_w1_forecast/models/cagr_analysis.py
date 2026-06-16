"""
models/cagr_analysis.py
Figure 9 — CAGR Analysis: Historical growth rates (26-point dataset,
            FY2000-01 to FY2024-25) vs rates required to meet 100 GW
            and 140 GW targets by FY2029-30 (5-year horizon).

Run standalone:  python models/cagr_analysis.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from utils import (
    HIST_YEARS, HIST_CAP, TARGET_100, TARGET_140, N_FORECAST,
    NAVY, BLUE, TEAL, ORANGE, RED, TEXT, MGRAY,
    set_style, save_fig, fy,
)


def cagr(start: float, end: float, n: int) -> float:
    """Return CAGR as a percentage."""
    return ((end / start) ** (1 / n) - 1) * 100


def compute_cagr() -> dict:
    current = HIST_CAP[-1]   # 50.038 GW (FY2024-25)
    n = len(HIST_CAP)        # 26

    return {
        "overall_25yr": cagr(HIST_CAP[0],  current, 25),  # FY00-01 -> FY24-25
        "decade_10yr":  cagr(HIST_CAP[n-11], current, 10),  # FY14-15 -> FY24-25
        "5yr":          cagr(HIST_CAP[n-6],  current, 5),   # FY19-20 -> FY24-25
        "3yr":          cagr(HIST_CAP[n-4],  current, 3),   # FY21-22 -> FY24-25
        "required_100": cagr(current, TARGET_100, N_FORECAST),
        "required_140": cagr(current, TARGET_140, N_FORECAST),
    }


def run(plots_dir=None) -> dict:
    set_style()
    data = compute_cagr()

    hist_labels = [
        f"Overall\nFY00-01–FY24-25\n(25 yr)",
        f"Decade\nFY14-15–FY24-25\n(10 yr)",
        f"5-Year\nFY19-20–FY24-25\n(5 yr)",
        f"3-Year\nFY21-22–FY24-25\n(3 yr)",
    ]
    hist_values = [data["overall_25yr"], data["decade_10yr"],
                   data["5yr"], data["3yr"]]
    hist_colors = [NAVY, BLUE, TEAL, ORANGE]

    req_labels = ["5-Year\nCAGR\n(baseline)", "Required\nfor 100 GW", "Required\nfor 140 GW"]
    req_values = [data["5yr"], data["required_100"], data["required_140"]]
    req_colors = [TEAL, ORANGE, RED]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ── Left: Historical CAGRs ─────────────────────────────────────────────────
    bars1 = ax1.bar(range(4), hist_values, color=hist_colors,
                    width=0.52, edgecolor="white", lw=1.5, zorder=3)
    for bar, val in zip(bars1, hist_values):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.25,
                 f"{val:.1f}%", ha="center", fontsize=12, fontweight="bold", color=TEXT)
    ax1.set_xticks(range(4))
    ax1.set_xticklabels(hist_labels, fontsize=8.5)
    ax1.set_title("Historical CAGR by Period")
    ax1.set_ylabel("Compound Annual Growth Rate (%)")
    ax1.set_ylim(0, 20)
    ax1.text(0.02, 0.97,
             "CAGR = (End / Start)^(1/n) − 1",
             transform=ax1.transAxes, fontsize=8.5, color="#7F8C8D",
             va="top", style="italic",
             bbox=dict(facecolor="#F4F6F7", edgecolor=MGRAY,
                       boxstyle="round,pad=0.4", alpha=0.8))

    # ── Right: Required CAGRs vs baseline ─────────────────────────────────────
    bars2 = ax2.bar(range(3), req_values, color=req_colors,
                    width=0.52, edgecolor="white", lw=1.5, zorder=3)
    for bar, val in zip(bars2, req_values):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
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
    ax2.set_title(f"Required CAGR vs Baseline to Hit FY2029-30 Targets\n({N_FORECAST}-year horizon: FY25-26 to FY29-30)")
    ax2.set_ylabel("Required Annual CAGR (%)")
    ax2.set_ylim(0, 28)
    ax2.legend(fontsize=9)

    fig.suptitle(
        "Figure 9 — CAGR Analysis: Historical Growth vs Required Growth for FY2029-30 Targets",
        fontsize=12, fontweight="bold", color=NAVY, y=1.02,
    )

    save_fig(fig, "fig9_cagr.png")
    return data


if __name__ == "__main__":
    print("\n── CAGR Analysis (26-point dataset, 5-yr horizon) ─────────")
    d = run()
    print(f"\n  Results:")
    for k, v in d.items():
        print(f"    {k:20s}: {v:.2f}%")
