# 🌬️ India Wind Energy — Goal W1 Forecast
## Will India Achieve 100 GW / 140 GW Wind Capacity by 2030?

> A complete ML forecasting project for **Goal W-1** — India's total installed wind power capacity target.  
> Prepared for: **National Institute of Wind Energy (NIWE)** | Data: FY2007–FY2026

---

## 📊 Key Result

| Model | 2030 Forecast | Gap to 100 GW | Gap to 140 GW | Status |
|---|---|---|---|---|
| Linear Regression | ~61.6 GW | −38.4 GW | −78.4 GW | ⚠️ AT RISK |
| Polynomial Reg. (Deg-3) | ~67.3 GW | −32.7 GW | −72.7 GW | ⚠️ AT RISK |
| ARIMA(1,1,1) | ~80.3 GW | −19.7 GW | −59.7 GW | ⚠️ AT RISK |
| Holt Exp. Smoothing | ~77.9 GW | −22.1 GW | −62.1 GW | ⚠️ AT RISK |

> **Verdict:** 100 GW is AT RISK — requires ~11 GW/yr sustained additions vs current 6.05 GW/yr record.  
> **140 GW is NOT ACHIEVABLE** by 2030 under any realistic scenario.

---

## 🗂️ Project Structure

```
india_wind_w1_forecast/
│
├── run_all.py                    ← Entry point: run this first
├── utils.py                      ← Shared data, colours, plot helpers
├── requirements.txt
├── .gitignore
│
├── data/
│   └── wind_capacity.csv         ← Historical FY2007–FY2026 dataset
│
├── models/
│   ├── __init__.py
│   ├── historical_growth.py      → Figures 1 & 2 (capacity + additions)
│   ├── cagr_analysis.py          → Figure 9  (CAGR analysis)
│   ├── linear_regression.py      → Figure 3  (Linear Regression)
│   ├── polynomial_regression.py  → Figure 4  (Polynomial Regression Deg-3)
│   ├── arima_model.py            → Figure 5  (ARIMA 1,1,1)
│   ├── holt_model.py             → Figure 6  (Holt Exponential Smoothing)
│   ├── scenario_analysis.py      → Figure 7  (100/140 GW Scenarios)
│   └── model_comparison.py       → Figure 8  (All models combined)
│
├── plots/                        ← Auto-generated PNG figures (9 total)
│   ├── fig1_capacity_growth.png
│   ├── fig2_annual_additions.png
│   ├── fig3_linear_regression.png
│   ├── fig4_polynomial_regression.png
│   ├── fig5_arima.png
│   ├── fig6_holt.png
│   ├── fig7_scenario.png
│   ├── fig8_all_models.png
│   └── fig9_cagr.png
│
├── generate_report.js            ← Word report generator (Node.js)
└── report/
    └── India_Wind_Capacity_Outlook_2030.docx
```

---

## 🚀 Quick Start

### Step 1 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Generate all figures
```bash
python run_all.py
```
All 9 PNG figures are saved to `plots/`.  
Forecast data is saved to `data/forecast_results.json`.

### Step 3 (optional) — Generate Word report
```bash
npm install -g docx
python run_all.py --report
```

---

## 🤖 ML Models

| # | Model | File | Target Variable | Key Feature |
|---|---|---|---|---|
| 1 | Linear Regression | `linear_regression.py` | Cumulative capacity (GW) | Year (numeric) |
| 2 | Polynomial Reg. Deg-3 | `polynomial_regression.py` | Cumulative capacity (GW) | Year + non-linear terms |
| 3 | ARIMA(1,1,1) | `arima_model.py` | Annual additions (GW/yr) | Autoregressive lag-1 |
| 4 | Holt Exp. Smoothing | `holt_model.py` | Cumulative capacity (GW) | Level + trend components |

Each model file is **standalone** — run any one independently:
```bash
python models/linear_regression.py
python models/arima_model.py
# etc.
```

---

## 📈 Figures Generated

| Figure | File | Description |
|---|---|---|
| Fig 1 | `fig1_capacity_growth.png` | Cumulative installed capacity FY2007–FY2026 |
| Fig 2 | `fig2_annual_additions.png` | Annual additions with required-rate reference lines |
| Fig 3 | `fig3_linear_regression.png` | Linear Regression forecast with CI band |
| Fig 4 | `fig4_polynomial_regression.png` | Polynomial Regression (Deg-3) forecast |
| Fig 5 | `fig5_arima.png` | ARIMA annual additions + cumulative capacity (dual panel) |
| Fig 6 | `fig6_holt.png` | Holt Exponential Smoothing forecast |
| Fig 7 | `fig7_scenario.png` | Scenario trajectories for all addition rates |
| Fig 8 | `fig8_all_models.png` | All 4 models vs 100 GW & 140 GW targets |
| Fig 9 | `fig9_cagr.png` | CAGR historical vs required for 2030 |

---

## 📁 Data

All data sourced from official publications only:

| Source | Data Provided |
|---|---|
| **MNRE / PIB Press Releases** | Annual installed capacity, additions FY2010–FY2026 |
| **CEA Annual Reports** | Cumulative capacity FY2007–FY2026 |
| **NIWE** | Wind resource, CUF, state-wise assessments |
| **GWEC Global Wind Report 2026** | Global context, India comparisons |
| **Ember Global Electricity Review 2026** | Generation data |

No fabricated or estimated values. Confidence: HIGH for all data points.

---

## 📋 Model Accuracy (In-Sample Metrics)

| Model | R² | RMSE (GW) | MAE (GW) |
|---|---|---|---|
| Linear Regression | 0.9888 | 1.47 | 1.12 |
| Polynomial Reg. (Deg-3) | 0.9909 | 1.33 | 1.06 |
| ARIMA(1,1,1)* | 0.0968* | 1.32 | 1.01 |
| Holt Exp. Smoothing | 0.9909 | 1.33 | 1.03 |

\* ARIMA R² computed on the annual additions series (not cumulative).

---

## 📜 License
MIT — free to use for research and educational purposes.

---

*Prepared for NIWE | India Wind Capacity Outlook 2030 | June 2026*
