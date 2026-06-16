"""
models/scenario_analysis.py
Figure 7 — Scenario Analysis: wind capacity trajectories for different
           annual addition rates, benchmarked against 100 GW and 140 GW
           by FY2029-30 (5-year horizon from FY2024-25 base of 50.04 GW).

Scenarios modelled
──────────────────
  Conservative  :  4.0 GW/yr  (≈ FY2024-25 actual addition)
  Moderate      :  6.0 GW/yr
  Accelerated   :  8.0 GW/yr
  100-GW Path   : ~10.0 GW/yr (exact requirement)
  140-GW Path   : ~18.0 GW/yr (exact requirement)

Run standalone:  python models/scenario_analysis.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from utils import (
    HIST_YEARS, HIST_CAP, FORECAST_YEARS, N_FORECAST, TARGET_100, TARGET_140,
    NAVY, BLUE, TEAL, ORANGE, RED, MGRAY, TEXT,
    set_style, source_note, xtick_fy, save_fig, fy,
)


# ── Scenario definitions ──────────────────────────────────────────────────────
def build_scenarios(base: float = HIST_CAP[-1]) -> dict:
    """Build cumulative GW trajectories for each scenario from the base year."""
    req_100 = (TARGET_100 - base) / N_FORECAST   # ≈ 9.99 GW/yr
    req_140 = (TARGET_140 - base) / N_FORECAST   # ≈ 17.99 GW/yr
    return {
        "Conservative\n(4 GW/yr)":            dict(rate=4.0,     color=BLUE,   ls="-"),
        "Moderate\n(6 GW/yr)":                dict(rate=6.0,     color=TEAL,   ls="-"),
        "Accelerated\n(8 GW/yr)":             dict(rate=8.0,     color=ORANGE, ls="-"),
        f"100 GW Path\n({req_100:.1f} GW/yr)": dict(rate=req_100, color=NAVY, ls="--"),
        f"140 GW Path\n({req_140:.1f} GW/yr)": dict(rate=req_140, color=RED,  ls="--"),
    }


def run(plots_dir=None) -> None:
    set_style()
    base      = HIST_CAP[-1]                 # 50.038 GW (FY2024-25)
    scenarios = build_scenarios(base)

    fig, ax = plt.subplots(figsize=(12, 6.5))

    # ── Historical ────────────────────────────────────────────────────────────
    ax.scatter(HIST_YEARS, HIST_CAP, color=NAVY, s=26, alpha=0.65, zorder=5)
    ax.plot(HIST_YEARS, HIST_CAP, color=NAVY, lw=2.2, alpha=0.65,
            label="Historical Actual (FY2000-01–FY2024-25)")

    # ── Scenario trajectories ─────────────────────────────────────────────────
    for name, cfg in scenarios.items():
        vals = [base + cfg["rate"] * (i + 1) for i in range(N_FORECAST)]
        label_str = name.replace("\n", " ") + f"  →FY29-30: {vals[-1]:.1f} GW"
        ax.plot(FORECAST_YEARS, vals, color=cfg["color"],
                lw=2.3, ls=cfg["ls"], marker="o", ms=5.5, label=label_str)
        ax.plot([HIST_YEARS[-1], FORECAST_YEARS[0]], [base, vals[0]],
                color=cfg["color"], lw=2.3, ls=cfg["ls"])
        # End-label at FY2029-30
        ax.text(FORECAST_YEARS[-1] + 0.15, vals[-1],
                f"{vals[-1]:.1f}", fontsize=8.5, color=cfg["color"],
                va="center", fontweight="bold")

    # Likely-range shading (Moderate to Accelerated)
    mod = [base + 6.0 * (i+1) for i in range(N_FORECAST)]
    acc = [base + 8.0 * (i+1) for i in range(N_FORECAST)]
    ax.fill_between(FORECAST_YEARS, mod, acc,
                    color=TEAL, alpha=0.08, label="Likely range (6–8 GW/yr)")

    # ── Target lines ──────────────────────────────────────────────────────────
    ax.axhline(TARGET_100, color=TEAL, lw=2.0, ls=":", alpha=0.9)
    ax.axhline(TARGET_140, color=RED,  lw=1.8, ls=":", alpha=0.9)
    ax.text(2026.05, TARGET_100 + 1.6, "100 GW Target (MNRE)",
            fontsize=9, color=TEAL, fontweight="bold")
    ax.text(2026.05, TARGET_140 + 1.6, "140 GW Aspirational Target",
            fontsize=9, color=RED, fontweight="bold")

    # ── Gap annotation for 100 GW path (using likely-range midpoint) ──────────
    likely_2030 = base + 7.0 * N_FORECAST    # midpoint of 6-8 GW/yr range
    gap_100 = TARGET_100 - likely_2030
    ax.annotate("",
                xy=(2030, TARGET_100), xytext=(2030, likely_2030),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=1.3))
    ax.text(2030.18, (TARGET_100 + likely_2030) / 2,
            f"Gap\n~{gap_100:.0f} GW",
            fontsize=8.5, color="#555", va="center", fontweight="bold")

    # ── Historical/Forecast divider ───────────────────────────────────────────
    boundary = HIST_YEARS[-1] + 0.5   # 2025.5
    ax.axvline(boundary, color=MGRAY, lw=1, ls=":")
    ax.text(boundary + 0.1, 8, "← Historical  |  Forecast →",
            fontsize=7.5, color="#7F8C8D", va="bottom")

    ax.set_title("Figure 7 — Scenario Analysis: India Wind Capacity Trajectories\n"
                 "FY2025-26 to FY2029-30 (Base: 50.04 GW at FY2024-25)", pad=12)
    ax.set_xlabel("Financial Year")
    ax.set_ylabel("Cumulative Installed Capacity (GW)")
    xtick_fy(ax, np.array(HIST_YEARS), step=3, extra=FORECAST_YEARS)
    ax.set_xlim(1999, 2031.5)
    ax.set_ylim(0, 155)
    ax.legend(loc="upper left", fontsize=7.8, ncol=1)
    source_note(ax)

    save_fig(fig, "fig7_scenario.png")
    print("\n  Scenario analysis FY2029-30 projections (base = "
          f"{base:.2f} GW at FY2024-25):")
    for name, cfg in scenarios.items():
        vals = [base + cfg["rate"] * (i+1) for i in range(N_FORECAST)]
        n    = name.replace("\n", " ")
        print(f"    {n:35s}: {vals[-1]:.1f} GW")


if __name__ == "__main__":
    print("\n── Scenario Analysis (26-point dataset, 5-yr horizon) ─────")
    run()
