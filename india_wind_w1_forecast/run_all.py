"""
run_all.py
Master runner for the India Wind W1 Forecast project.
Trains all four ML models, generates all 9 figures, exports forecast data.

Usage:
    python run_all.py            # generate all figures
    python run_all.py --report   # generate figures + Word report (needs Node.js)
"""

import os, sys, time, json, argparse, warnings
warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from utils import HIST_YEARS, HIST_CAP, ADDITIONS, FORECAST_YEARS, PLOT_DIR

SEP  = "─" * 62
SEP2 = "═" * 62


def banner(text):
    print(f"\n{SEP}")
    print(f"  {text}")
    print(SEP)


def run_all_models():
    t0 = time.time()

    print(f"\n{SEP2}")
    print("  INDIA WIND W1 FORECAST  —  Full Model Pipeline")
    print(f"  Output directory: {PLOT_DIR}")
    print(SEP2)

    # ── Step 1: Historical growth plots ───────────────────────────────────────
    banner("Step 1/7 · Historical Growth  (Figures 1 & 2)")
    from models.historical_growth import figure1_capacity_growth, figure2_annual_additions
    figure1_capacity_growth()
    figure2_annual_additions()

    # ── Step 2: CAGR Analysis ─────────────────────────────────────────────────
    banner("Step 2/7 · CAGR Analysis  (Figure 9)")
    from models.cagr_analysis import run as cagr_run
    cagr_data = cagr_run()

    # ── Step 3: Linear Regression ─────────────────────────────────────────────
    banner("Step 3/7 · Linear Regression  (Figure 3)")
    from models.linear_regression import run as lr_run
    lr_res = lr_run()

    # ── Step 4: Polynomial Regression ─────────────────────────────────────────
    banner("Step 4/7 · Polynomial Regression  (Figure 4)")
    from models.polynomial_regression import run as poly_run
    poly_res = poly_run()

    # ── Step 5: ARIMA ─────────────────────────────────────────────────────────
    banner("Step 5/7 · ARIMA(1,1,1)  (Figure 5)")
    from models.arima_model import run as arima_run
    arima_res = arima_run()

    # ── Step 6: Holt Smoothing ────────────────────────────────────────────────
    banner("Step 6/7 · Holt Exponential Smoothing  (Figure 6)")
    from models.holt_model import run as holt_run
    holt_res = holt_run()

    # ── Step 7: Scenario Analysis + All Models Comparison ────────────────────
    banner("Step 7/7 · Scenario Analysis (Figure 7) + Comparison (Figure 8)")
    from models.scenario_analysis import run as scenario_run
    scenario_run()

    # Pass pre-computed results to avoid re-training
    results_list = [
        dict(name="Linear Regression",       short="Linear\nReg.",
             forecast=lr_res["forecast"],   color="#2980B9", ls="-",
             r2=lr_res["r2"],   rmse=lr_res["rmse"]),
        dict(name="Polynomial Reg. (Deg-3)", short="Poly\nReg.",
             forecast=poly_res["forecast"], color="#009688", ls="-.",
             r2=poly_res["r2"], rmse=poly_res["rmse"]),
        dict(name="ARIMA(1,1,1)",            short="ARIMA\n(1,1,1)",
             forecast=arima_res["forecast"], color="#E07B39", ls="--",
             r2=arima_res["r2"], rmse=arima_res["rmse"]),
        dict(name="Holt Exp. Smoothing",     short="Holt\nSmoothing",
             forecast=holt_res["forecast"],  color="#8E44AD", ls=":",
             r2=holt_res["r2"],  rmse=holt_res["rmse"]),
    ]
    from models.model_comparison import run as comp_run
    comp_run(results=results_list)

    # ── Export JSON ───────────────────────────────────────────────────────────
    output = {
        "metadata": {
            "project":   "India Wind W1 Forecast",
            "goal":      "100 GW and 140 GW by FY2030",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "historical": {
            "years":     HIST_YEARS,
            "capacity":  HIST_CAP,
            "additions": ADDITIONS,
        },
        "forecast_years": FORECAST_YEARS,
        "models": {
            "linear_regression":    {"forecast": lr_res["forecast"],   "r2": lr_res["r2"],   "rmse": lr_res["rmse"],   "mae": lr_res["mae"]},
            "polynomial_regression":{"forecast": poly_res["forecast"], "r2": poly_res["r2"], "rmse": poly_res["rmse"], "mae": poly_res["mae"]},
            "arima":                {"forecast": arima_res["forecast"], "annual_fc": arima_res.get("annual_fc",[]),     "r2": arima_res["r2"], "rmse": arima_res["rmse"], "mae": arima_res["mae"]},
            "holt":                 {"forecast": holt_res["forecast"],  "r2": holt_res["r2"],  "rmse": holt_res["rmse"],  "mae": holt_res["mae"]},
        },
        "cagr": cagr_data,
    }
    json_path = os.path.join(ROOT, "data", "forecast_results.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)

    elapsed = time.time() - t0

    # ── Final summary ─────────────────────────────────────────────────────────
    print(f"\n{SEP2}")
    print(f"  ✔  All 9 figures generated in {elapsed:.1f}s")
    print(f"  ✔  Forecast data saved → data/forecast_results.json")
    print(f"\n  {'Model':<32} {'2030 GW':>8}  {'R²':>7}  {'RMSE':>8}  Status")
    print(f"  {'─'*32}  {'─'*6}  {'─'*6}  {'─'*6}  ──────────────")
    for r in results_list:
        fc30   = float(r["forecast"][-1])
        status = "AT RISK" if fc30 < 100 else "ACHIEVED"
        print(f"  {r['name']:<32} {fc30:>7.2f}  {r['r2']:>7}  {r['rmse']:>6} GW  {status}")

    print(f"\n  Plots saved to: {PLOT_DIR}")
    print(SEP2 + "\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true",
                        help="Also generate Word report (requires Node.js + docx)")
    args = parser.parse_args()

    result = run_all_models()

    if args.report:
        print("\n── Generating Word Report ──────────────────────────────────")
        ret = os.system("node generate_report.js")
        if ret != 0:
            print("  ✘ Word report generation failed. Ensure Node.js and 'docx' npm package are installed.")
            print("    Run: npm install -g docx")
        else:
            print("  ✔ Word report generated → report/India_Wind_Capacity_Outlook_2030.docx")
