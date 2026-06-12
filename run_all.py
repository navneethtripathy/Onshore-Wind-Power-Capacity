"""
run_all.py — Run all models and generate all figures for india-wind-2030.
Data: W1_Final_Objective_Dataset.xlsx

Usage:  python run_all.py
Output: plots/ directory (9 PNG figures)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("  India Wind 2030 — Full Model Run")
    print("  Data: W1_Final_Objective_Dataset.xlsx")
    print("=" * 60)

    # Fig 1 & 2 — Historical growth
    print("\n[1/7] Historical Growth Figures...")
    from models.historical_growth import figure1_capacity_growth, figure2_annual_additions
    figure1_capacity_growth()
    figure2_annual_additions()

    # Fig 3 — Linear Regression
    print("\n[2/7] Linear Regression...")
    from models.linear_regression import run as lr_run
    lr_results = lr_run()

    # Fig 4 — Polynomial Regression
    print("\n[3/7] Polynomial Regression (Degree 3)...")
    from models.polynomial_regression import run as poly_run
    poly_results = poly_run()

    # Fig 5 — ARIMA
    print("\n[4/7] ARIMA / AR(1)...")
    from models.arima_model import run as arima_run
    arima_results = arima_run()

    # Fig 6 — Holt
    print("\n[5/7] Holt Exponential Smoothing...")
    from models.holt_model import run as holt_run
    holt_results = holt_run()

    # Fig 7 — Scenario Analysis
    print("\n[6/7] Scenario Analysis...")
    from models.scenario_analysis import run as scenario_run
    scenario_run()

    # Fig 8 — Model Comparison
    print("\n[7/7] Model Comparison...")
    from models.model_comparison import run as compare_run
    compare_run()

    # Fig 9 — CAGR Analysis
    print("\n[8/8] CAGR Analysis...")
    from models.cagr_analysis import run as cagr_run
    cagr_run()

    print("\n" + "=" * 60)
    print("  All figures saved to plots/")
    print("  Figures generated:")
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    for f in sorted(os.listdir(plots_dir)):
        if f.endswith(".png"):
            print(f"    ✔  {f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
