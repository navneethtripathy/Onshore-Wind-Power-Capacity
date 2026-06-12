# India Wind Energy 2030 — Forecasting India's Progress Towards 100 GW & 140 GW Targets

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data: W1_Final_Objective_Dataset](https://img.shields.io/badge/data-W1__Final__Objective__Dataset-orange.svg)](#)

> **Prepared for:** National Institute of Wind Energy (NIWE)  
> **By:** Navneeth Tripathy,Neil Nickson,Keith Rocha  
> **Date:** June 2026  
> **Data Source:** `W1_Final_Objective_Dataset.xlsx` | MNRE / CEA / PIB / GWEC 2026

---

## Overview

This repository contains the complete data science pipeline for forecasting India's wind energy installed capacity through FY2030, benchmarked against:

- **100 GW** — MNRE Official Target (Conservative)
- **140 GW** — Aspirational Target (Ambitious)

Four ML/statistical models are applied to **W1_Final_Objective_Dataset.xlsx** (FY2000–FY2025, n=26 data points):

| Model | FY2030 Forecast | R² | RMSE |
|---|---|---|---|
| Linear Regression | 57.2 GW | 0.9719 | 2.68 GW |
| Polynomial Regression (Deg-3) | 52.5 GW | 0.9961 | 1.00 GW |
| ARIMA / AR(1) | 72.4 GW | — | 1.41 GW |
| Holt Exponential Smoothing | 52.2 GW | 0.9999 | 0.18 GW |

**Key Finding:** All four models project India reaching **52–72 GW** by FY2030 — well below the 100 GW target. Annual additions must grow from the current ~4.15 GW/yr (FY2025) to ~10 GW/yr and sustain for 5 years to hit 100 GW.

---

## Repository Structure

```
india-wind-2030/
├── utils.py                          # Shared constants, palette, helpers (W1 dataset embedded)
├── run_all.py                        # Run all models → generate all 9 figures
├── build_report.js                   # Generate full Word report with embedded plots
│
├── models/
│   ├── historical_growth.py          # Fig 1 & 2 — Capacity growth & annual additions
│   ├── linear_regression.py          # Fig 3 — Linear Regression forecast
│   ├── polynomial_regression.py      # Fig 4 — Polynomial Regression (Degree 3)
│   ├── arima_model.py                # Fig 5 — ARIMA / AR(1) with differencing
│   ├── holt_model.py                 # Fig 6 — Holt Exponential Smoothing
│   ├── scenario_analysis.py          # Fig 7 — Scenario Analysis (6/8/10/11/18 GW/yr)
│   ├── model_comparison.py           # Fig 8 — All models consolidated comparison
│   └── cagr_analysis.py              # Fig 9 — CAGR analysis historical vs required
│
├── plots/                            # Generated PNG figures (Fig 1–9)
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
└── India_Wind_Outlook_2030_FINAL.docx  # Full report with embedded figures
```

---

## Dataset — W1_Final_Objective_Dataset.xlsx

The dataset spans **FY2000–FY2025** (26 annual observations) and contains three sheets:

| Sheet | Contents |
|---|---|
| `W1_Master_Dataset` | Cumulative installed capacity (MW→GW), annual additions, YoY growth % |
| `W1_Feature_Indicators` | Policy milestones, WMS stations, SCADA coverage, auction pipeline |
| `Targets_and_Gaps` | MNRE 100 GW conservative target, 140 GW ambitious target, gap calculations |

**Key W1 data points:**

| Financial Year | Cumulative (GW) | Annual Addition (GW) |
|---|---|---|
| FY2017 | 32.302 | **5.505 (record until W1 period)** |
| FY2022 | 40.324 | 1.081 (post-COVID low) |
| FY2023 | 42.620 | 2.296 |
| FY2024 | 45.885 | 3.265 |
| **FY2025** | **50.038** | **4.152** |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/india-wind-2030.git
cd india-wind-2030

# Install Python dependencies
pip install numpy matplotlib seaborn scikit-learn

# Install Node.js dependency (for Word report generation)
npm install -g docx
```

**Dependencies:**
- Python 3.8+: `numpy`, `matplotlib`, `scikit-learn`
- Node.js 16+: `docx` (v9.6+)
- No `statsmodels` required — Holt and ARIMA implemented in pure numpy/sklearn

---

## Usage

### Generate All Plots (9 Figures)

```bash
python run_all.py
```

Output: All figures saved to `plots/` directory.

### Run Individual Models

```bash
# Historical trend figures (Fig 1 & 2)
python models/historical_growth.py

# Linear Regression forecast (Fig 3)
python models/linear_regression.py

# Polynomial Regression (Fig 4)
python models/polynomial_regression.py

# ARIMA / AR(1) forecast (Fig 5)
python models/arima_model.py

# Holt Exponential Smoothing (Fig 6)
python models/holt_model.py

# Scenario Analysis (Fig 7)
python models/scenario_analysis.py

# All Models Comparison (Fig 8)
python models/model_comparison.py

# CAGR Analysis (Fig 9)
python models/cagr_analysis.py
```

### Generate Word Report

```bash
node build_report.js
# Output: India_Wind_Outlook_2030_FINAL.docx
```

---

## Figures

| Figure | Description |
|---|---|
| Fig 1 | Cumulative installed capacity growth FY2000–FY2025 (W1 data) |
| Fig 2 | Annual capacity additions vs required rates for 100/140 GW |
| Fig 3 | Linear Regression forecast FY2026–FY2030 with ±2 RMSE band |
| Fig 4 | Polynomial Regression (Deg-3) forecast with ±1.5 RMSE band |
| Fig 5 | ARIMA/AR(1) — annual additions forecast + cumulative capacity |
| Fig 6 | Holt Exponential Smoothing forecast with ±2 Std band |
| Fig 7 | Scenario Analysis — 6/8/10/11/18 GW/yr trajectories |
| Fig 8 | All models consolidated comparison + 2030 bar chart |
| Fig 9 | CAGR analysis: historical periods vs required rate for 2030 |

---

## Key Findings

1. **All models show India reaching 52–72 GW by FY2030** — a significant shortfall vs the 100 GW target.
2. **ARIMA (best-case):** 72.4 GW — still 27.6 GW short of 100 GW.
3. **Required annual additions:** ~10 GW/yr for 100 GW, vs current 4.15 GW/yr (W1 FY2025).
4. **140 GW is not achievable by 2030** — would require ~18 GW/yr (4.3x current rate).
5. **Realistic 2030 outcome:** 75–80 GW under accelerated policy scenario.

---

## Data Sources

| Source | Role |
|---|---|
| `W1_Final_Objective_Dataset.xlsx` | **Primary dataset** — FY2000–FY2025 capacity data |
| MNRE / PIB Press Releases | Verification of annual additions |
| CEA Annual Reports | Historical capacity cross-reference |
| NIWE Annual Reports | Wind resource, CUF, state-wise context |
| GWEC Global Wind Report 2026 | Global benchmarking, India projections |
| UNFCCC NDC (India, Aug 2022) | 2030 target framework |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*India Wind Capacity Outlook 2030 | NIWE / Energy Analytics Division | June 2026*  
*Data: W1_Final_Objective_Dataset.xlsx | MNRE | CEA | PIB | GWEC 2026*
