const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageBreak,
  LevelFormat, ExternalHyperlink
} = require('docx');
const fs = require('fs');
const path = require('path');

// ─── Colour palette ─────────────────────────────────────────────────────────
const NAVY   = "1B3A6B";
const TEAL   = "1ABC9C";
const BLUE   = "2980B9";
const ORANGE = "E67E22";
const RED    = "E74C3C";
const LGRAY  = "F4F6F7";
const MGRAY  = "BDC3C7";
const WHITE  = "FFFFFF";

// ─── Helpers ─────────────────────────────────────────────────────────────────
const PLOTS = '/home/claude/india-wind-2030/plots/';
const pageW = 9360; // US Letter content width in DXA (1440 DXA = 1 inch)

function loadImg(filename) {
  return fs.readFileSync(path.join(PLOTS, filename));
}

// Full-width image paragraph (scales to page width proportionally)
function imgPara(filename, captionText, origW, origH) {
  const emW = 5486400; // ~6.05 inches = content width in EMU (1 inch = 914400 EMU)
  const emH = Math.round(emW * origH / origW);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 160, after: 100 },
      children: [
        new ImageRun({
          data: loadImg(filename),
          transformation: { width: emW / 9144, height: emH / 9144 },
          type: "png",
        })
      ]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 200 },
      children: [
        new TextRun({
          text: captionText,
          italics: true, size: 18, color: "555555", font: "Arial"
        })
      ]
    })
  ];
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: NAVY, space: 4 } },
    children: [new TextRun({ text, bold: true, size: 32, color: NAVY, font: "Arial" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 120 },
    children: [new TextRun({ text, bold: true, size: 26, color: NAVY, font: "Arial" })]
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, bold: true, size: 22, color: "2C3E50", font: "Arial" })]
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 100, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    children: [new TextRun({
      text,
      size: 22,
      font: "Arial",
      color: opts.color || "2C3E50",
      bold: opts.bold || false,
      italics: opts.italic || false,
    })]
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 60 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: "2C3E50" })]
  });
}

function pb() {
  return new Paragraph({
    children: [new PageBreak()],
    spacing: { before: 0, after: 0 }
  });
}

function spacer(n = 1) {
  return Array.from({ length: n }, () =>
    new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun("")] })
  );
}

// Cell helper
function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.w || 4680, type: WidthType.DXA },
    shading: { fill: opts.fill || WHITE, type: ShadingType.CLEAR },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    borders: {
      top:    { style: BorderStyle.SINGLE, size: 1, color: "DDDDDD" },
      bottom: { style: BorderStyle.SINGLE, size: 1, color: "DDDDDD" },
      left:   { style: BorderStyle.SINGLE, size: 1, color: "DDDDDD" },
      right:  { style: BorderStyle.SINGLE, size: 1, color: "DDDDDD" },
    },
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({
        text,
        bold: opts.bold || false,
        size: opts.size || 20,
        color: opts.textColor || (opts.darkBg ? WHITE : "2C3E50"),
        font: "Arial",
      })]
    })]
  });
}

function headerRow(cols, widths) {
  return new TableRow({
    tableHeader: true,
    children: cols.map((c, i) => cell(c, {
      w: widths[i], fill: NAVY, bold: true, textColor: WHITE, darkBg: true, center: true, size: 19
    }))
  });
}

function dataRow(cols, widths, even = false) {
  return new TableRow({
    children: cols.map((c, i) => cell(c, { w: widths[i], fill: even ? LGRAY : WHITE, size: 19 }))
  });
}

// ─── Banner box ───────────────────────────────────────────────────────────────
function verdictBox(label, text, fillColor) {
  return new Table({
    width: { size: pageW, type: WidthType.DXA },
    columnWidths: [1440, pageW - 1440],
    rows: [new TableRow({ children: [
      new TableCell({
        width: { size: 1440, type: WidthType.DXA },
        shading: { fill: fillColor, type: ShadingType.CLEAR },
        verticalAlign: VerticalAlign.CENTER,
        margins: { top: 120, bottom: 120, left: 160, right: 120 },
        borders: {
          top: { style: BorderStyle.SINGLE, size: 2, color: fillColor },
          bottom: { style: BorderStyle.SINGLE, size: 2, color: fillColor },
          left: { style: BorderStyle.SINGLE, size: 2, color: fillColor },
          right: { style: BorderStyle.SINGLE, size: 1, color: fillColor },
        },
        children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: label, bold: true, size: 19, color: WHITE, font: "Arial" })]
        })]
      }),
      new TableCell({
        width: { size: pageW - 1440, type: WidthType.DXA },
        shading: { fill: "FFF9F0", type: ShadingType.CLEAR },
        verticalAlign: VerticalAlign.CENTER,
        margins: { top: 100, bottom: 100, left: 160, right: 120 },
        borders: {
          top: { style: BorderStyle.SINGLE, size: 2, color: fillColor },
          bottom: { style: BorderStyle.SINGLE, size: 2, color: fillColor },
          left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
          right: { style: BorderStyle.SINGLE, size: 2, color: fillColor },
        },
        children: [new Paragraph({
          children: [new TextRun({ text, size: 20, font: "Arial", color: "2C3E50" })]
        })]
      })
    ]})],
    margins: { top: 120, bottom: 120 },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// DOCUMENT ASSEMBLY
// ═══════════════════════════════════════════════════════════════════════════
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    }]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: NAVY },
        paragraph: { spacing: { before: 400, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: NAVY },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: "2C3E50" },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ]
  },

  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 }
      }
    },

    // ── Header ──────────────────────────────────────────────────────────────
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            spacing: { after: 0 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: NAVY, space: 4 } },
            children: [
              new TextRun({ text: "India Wind Capacity Outlook 2030  |  NIWE / Energy Analytics Division  |  June 2026",
                size: 18, color: "7F8C8D", font: "Arial" }),
              new TextRun({ text: "\t", size: 18, font: "Arial" }),
              new TextRun({ text: "W1_Final_Objective_Dataset.xlsx", size: 18, color: "7F8C8D",
                font: "Arial", italics: true }),
            ]
          })
        ]
      })
    },

    // ── Footer ──────────────────────────────────────────────────────────────
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            spacing: { before: 0 },
            border: { top: { style: BorderStyle.SINGLE, size: 2, color: MGRAY, space: 4 } },
            children: [
              new TextRun({ text: "Confidential | For Official Use Only  |  Data: MNRE / CEA / PIB / GWEC 2026",
                size: 17, color: "95A5A6", font: "Arial" }),
              new TextRun({ text: "\t\t\tConfidential | Official Use Only", size: 17, color: "95A5A6", font: "Arial" }),
            ]
          })
        ]
      })
    },

    children: [

      // ══════════════════════════════════════════════════════════════════════
      // COVER PAGE
      // ══════════════════════════════════════════════════════════════════════
      ...spacer(4),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 160 },
        children: [new TextRun({ text: "NATIONAL INSTITUTE OF WIND ENERGY (NIWE)", bold: true,
          size: 24, color: NAVY, font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 480 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY, space: 8 } },
        children: [new TextRun({ text: "Energy Analytics Division — Wind Research Team",
          size: 21, color: "555555", font: "Arial", italics: true })]
      }),
      ...spacer(2),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
        children: [new TextRun({ text: "INDIA WIND CAPACITY", bold: true,
          size: 56, color: NAVY, font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 200 },
        children: [new TextRun({ text: "OUTLOOK 2030", bold: true,
          size: 56, color: TEAL, font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 480 },
        children: [new TextRun({
          text: "Forecasting India's Progress Towards the 100 GW and 140 GW Wind Power Targets",
          size: 26, color: "2C3E50", font: "Arial", italics: true })]
      }),
      ...spacer(2),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [3120, 6240],
        rows: [
          new TableRow({ children: [
            new TableCell({ width: { size: 3120, type: WidthType.DXA },
              shading: { fill: LGRAY, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                right: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
              },
              children: [new Paragraph({ children: [
                new TextRun({ text: "Prepared for:", bold: true, size: 20, font: "Arial", color: NAVY })] })]
            }),
            new TableCell({ width: { size: 6240, type: WidthType.DXA },
              shading: { fill: WHITE, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                right: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
              },
              children: [new Paragraph({ children: [
                new TextRun({ text: "National Institute of Wind Energy (NIWE)", size: 20, font: "Arial" })] })]
            }),
          ]}),
          new TableRow({ children: [
            new TableCell({ width: { size: 3120, type: WidthType.DXA },
              shading: { fill: LGRAY, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                right: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
              },
              children: [new Paragraph({ children: [
                new TextRun({ text: "Data Source:", bold: true, size: 20, font: "Arial", color: NAVY })] })]
            }),
            new TableCell({ width: { size: 6240, type: WidthType.DXA },
              shading: { fill: WHITE, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                right: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
              },
              children: [new Paragraph({ children: [
                new TextRun({ text: "W1_Final_Objective_Dataset.xlsx | MNRE / CEA / PIB / GWEC 2026", size: 20, font: "Arial" })] })]
            }),
          ]}),
          new TableRow({ children: [
            new TableCell({ width: { size: 3120, type: WidthType.DXA },
              shading: { fill: LGRAY, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                right: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
              },
              children: [new Paragraph({ children: [
                new TextRun({ text: "Models:", bold: true, size: 20, font: "Arial", color: NAVY })] })]
            }),
            new TableCell({ width: { size: 6240, type: WidthType.DXA },
              shading: { fill: WHITE, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                right: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
              },
              children: [new Paragraph({ children: [
                new TextRun({ text: "Linear Regression | Polynomial Regression | ARIMA/AR(1) | Holt Exponential Smoothing", size: 20, font: "Arial" })] })]
            }),
          ]}),
          new TableRow({ children: [
            new TableCell({ width: { size: 3120, type: WidthType.DXA },
              shading: { fill: LGRAY, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                right: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
              },
              children: [new Paragraph({ children: [
                new TextRun({ text: "GitHub Repository:", bold: true, size: 20, font: "Arial", color: NAVY })] })]
            }),
            new TableCell({ width: { size: 6240, type: WidthType.DXA },
              shading: { fill: WHITE, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                left: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
                right: { style: BorderStyle.SINGLE, size: 1, color: MGRAY },
              },
              children: [new Paragraph({ children: [
                new ExternalHyperlink({
                  link: "https://github.com/YOUR_USERNAME/india-wind-2030",
                  children: [new TextRun({
                    text: "https://github.com/YOUR_USERNAME/india-wind-2030",
                    style: "Hyperlink", size: 20, font: "Arial", color: BLUE,
                  })]
                })
              ]})]
            }),
          ]}),
        ]
      }),
      ...spacer(2),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "GWEC Global Wind Report 2026 Data Integrated",
          size: 19, color: "7F8C8D", font: "Arial", italics: true })]
      }),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // EXECUTIVE SUMMARY
      // ══════════════════════════════════════════════════════════════════════
      h1("Executive Summary"),
      body("India's wind energy sector has entered an era of accelerated deployment. As of FY2024-25, the country has installed 50.04 GW of wind power capacity — the latest verified data from W1_Final_Objective_Dataset.xlsx — and faces a significant challenge in bridging the gap to the government's official target of 100 GW and the aspirational 140 GW goal by 2030."),
      ...spacer(1),
      h2("Current Status"),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [4000, 2800, 2560],
        rows: [
          headerRow(["Metric", "Value", "Source"], [4000, 2800, 2560]),
          dataRow(["Installed Wind Capacity (FY2024-25)", "50.04 GW", "W1 Dataset / MNRE"], [4000, 2800, 2560], false),
          dataRow(["Annual Addition (FY2024-25)", "4.15 GW", "W1 Dataset / PIB"], [4000, 2800, 2560], true),
          dataRow(["Gap to 100 GW Target", "49.96 GW", "Calculated"], [4000, 2800, 2560], false),
          dataRow(["Gap to 140 GW Target", "89.96 GW", "Calculated"], [4000, 2800, 2560], true),
          dataRow(["Overall CAGR (FY2000-FY2025)", "See Fig 9", "W1 CAGR Analysis"], [4000, 2800, 2560], false),
          dataRow(["Required CAGR for 100 GW", "~15% per year", "Calculated"], [4000, 2800, 2560], true),
          dataRow(["Required CAGR for 140 GW", "~23% per year", "Calculated"], [4000, 2800, 2560], false),
        ]
      }),
      ...spacer(1),
      h2("Forecast Summary from ML Models"),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [2200, 1360, 1360, 1360, 1360, 1360],
        rows: [
          headerRow(["Model", "FY2027", "FY2028", "FY2029", "FY2030", "Status vs 100 GW"],
                    [2200, 1360, 1360, 1360, 1360, 1360]),
          dataRow(["Linear Regression", "~53 GW", "~55 GW", "~56 GW", "57.2 GW", "AT RISK"], [2200, 1360, 1360, 1360, 1360, 1360], false),
          dataRow(["Polynomial Reg. (Deg-3)", "~51 GW", "~51 GW", "~52 GW", "52.5 GW", "AT RISK"], [2200, 1360, 1360, 1360, 1360, 1360], true),
          dataRow(["ARIMA / AR(1)", "~56 GW", "~62 GW", "~67 GW", "72.4 GW", "AT RISK"], [2200, 1360, 1360, 1360, 1360, 1360], false),
          dataRow(["Holt Exp. Smoothing", "~51 GW", "~51 GW", "~52 GW", "52.2 GW", "AT RISK"], [2200, 1360, 1360, 1360, 1360, 1360], true),
        ]
      }),
      ...spacer(1),
      verdictBox("KEY FINDING",
        "Under current deployment trajectories, India is projected to reach 52-72 GW by FY2030 — significantly below the 100 GW target. The W1 dataset (FY2000-FY2025, n=26) reveals that achieving 100 GW requires ~10 GW/year of sustained additions — nearly 2.5x the FY2024-25 rate of 4.15 GW/yr.",
        ORANGE),
      ...spacer(1),
      h2("Key Barriers"),
      bullet("Grid: Transmission infrastructure lagging renewable deployment — 50,890 ckt km required but current pace delivers only ~35,000 ckt km by 2030."),
      bullet("Offshore: Offshore wind remains at zero installed capacity despite a 30 GW target."),
      bullet("Deployment: Annual additions need to grow from 4.15 GW to 10+ GW/year — requiring rapid scale-up of auctions and project execution."),
      bullet("Land: Land acquisition delays and state-level approvals create 2-3 year bottlenecks."),
      h2("Key Recommendations"),
      bullet("Policy: Increase SECI wind auction pipeline from 10 GW/year to 18 GW/year immediately."),
      bullet("Grid: Accelerate Green Energy Corridor Phase 2 completion by FY2027 to unlock 20+ GW."),
      bullet("Offshore: Launch 500 MW offshore wind pilot (Tamil Nadu coast) in FY2027 with enhanced VGF."),
      bullet("Technology: Enable repowering of 5,000+ MW of pre-2005 turbines to add effective capacity."),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 1
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 1: Introduction"),
      h2("1.1 Importance of Wind Energy"),
      body("Wind energy has emerged as one of the most cost-effective and rapidly scalable sources of clean electricity globally. For India specifically, wind power is not merely an energy option but a strategic necessity. India is the world's third-largest energy consumer and remains substantially dependent on imported fossil fuels."),
      h3("Energy Security"),
      body("India's wind resource potential — estimated by NIWE at over 1,163 GW at 120-metre hub height — represents one of the most underutilised clean energy assets in the world. Wind energy, being a domestically generated resource, directly reduces import dependence and strengthens energy sovereignty."),
      h3("Net Zero and Climate Goals"),
      body("At COP26 in Glasgow, Prime Minister Modi announced India's Panchamrit framework: 500 GW of non-fossil capacity by 2030, 50% of electricity from renewables by 2030, and net zero emissions by 2070. India's Updated NDC, submitted to the UNFCCC in August 2022, formally enshrined these targets under international law. India has already achieved the 50% non-fossil share target as of June 2025 — five years ahead of schedule."),
      h3("Renewable Energy Targets and the 500 GW Vision"),
      body("MNRE has set a 500 GW non-fossil fuel capacity target for 2030. Wind power, alongside solar, must contribute the largest share. The official wind target of 100 GW by 2030 — and the aspirational 140 GW target — reflects the scale of ambition required. As of March 2026, approximately 22% of India's total installed power capacity comes from wind."),
      h2("1.2 Scope of This Report"),
      body("This report presents a rigorous, data-driven assessment of whether India will achieve its official 100 GW wind power target by FY2030. Using historical installation data from FY2000 to FY2025 sourced from W1_Final_Objective_Dataset.xlsx (n=26 data points), four machine learning and statistical forecasting models are applied: Linear Regression, Polynomial Regression, ARIMA/AR(1), and Holt Exponential Smoothing."),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 2
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 2: India's Wind Sector Status"),
      h2("2.1 Installed Capacity Growth"),
      body("India's wind power capacity has grown from 1.02 GW in FY2000 to 50.04 GW in FY2025 (W1_Final_Objective_Dataset.xlsx), an increase of approximately 49 GW over 25 years. The growth trajectory is characterised by three distinct phases: an early steady growth phase (FY2000-FY2015), a spike-and-stagnation phase (FY2016-FY2022), and a recent re-acceleration phase (FY2023-FY2025)."),
      ...spacer(1),
      ...imgPara("fig1_capacity_growth.png",
        "Figure 1 — India Installed Wind Capacity Growth FY2000–FY2025. Source: W1_Final_Objective_Dataset.xlsx | MNRE / CEA / PIB 2026.",
        1507, 936),
      h2("2.2 Annual Capacity Additions"),
      body("Annual capacity additions reflect the pace of new project commissioning. After the record year of FY2017 (5.50 GW per W1 dataset), additions fell sharply due to policy uncertainty around GST transition, ISTS waiver ambiguity, and COVID-19. The sector has since recovered strongly, with FY2025 adding 4.15 GW, up from just 1.08 GW in FY2022."),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          headerRow(["Financial Year", "Cumulative (GW)", "Annual Addition (GW)", "Status"],
                    [2340, 2340, 2340, 2340]),
          dataRow(["FY2021", "39.24", "1.52", "Post-COVID recovery begins"], [2340, 2340, 2340, 2340], false),
          dataRow(["FY2022", "40.32", "1.08", "Near stagnation"], [2340, 2340, 2340, 2340], true),
          dataRow(["FY2023", "42.62", "2.30", "Accelerating"], [2340, 2340, 2340, 2340], false),
          dataRow(["FY2024", "45.89", "3.27", "Strong growth"], [2340, 2340, 2340, 2340], true),
          dataRow(["FY2025", "50.04", "4.15", "Momentum building"], [2340, 2340, 2340, 2340], false),
        ]
      }),
      ...spacer(1),
      ...imgPara("fig2_annual_additions.png",
        "Figure 2 — Annual Wind Capacity Additions FY2001–FY2025 with Required Rates for 100 GW and 140 GW Targets. Source: W1_Final_Objective_Dataset.xlsx.",
        1494, 936),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 3
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 3: Data and Methodology"),
      h2("3.1 Dataset Overview — W1_Final_Objective_Dataset.xlsx"),
      body("The dataset used in this study is W1_Final_Objective_Dataset.xlsx, spanning FY2000 to FY2025 and comprising 26 annual data points. The file contains three sheets: W1_Master_Dataset (capacity and additions data), W1_Feature_Indicators (policy and infrastructure milestones), and Targets_and_Gaps (MNRE 2030 targets). All data is sourced from official government publications."),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [3120, 3120, 3120],
        rows: [
          headerRow(["Source", "Data Provided", "Period"], [3120, 3120, 3120]),
          dataRow(["W1_Master_Dataset (MNRE/PIB)", "Annual installed capacity, additions (MW)", "FY2000-FY2025"], [3120, 3120, 3120], false),
          dataRow(["W1_Feature_Indicators (NIWE)", "Policy milestones, WMS stations, SCADA", "FY2012-FY2025"], [3120, 3120, 3120], true),
          dataRow(["Targets_and_Gaps (MNRE)", "Conservative 100 GW, Ambitious 140 GW targets", "2030"], [3120, 3120, 3120], false),
          dataRow(["CEA Annual Reports", "Cumulative capacity, generation data", "FY2007-FY2025"], [3120, 3120, 3120], true),
          dataRow(["GWEC Global Wind Report 2026", "Global context, India comparison", "CY2025-2026"], [3120, 3120, 3120], false),
        ]
      }),
      h2("3.2 Forecasting Models"),
      h3("Model 1 — Linear Regression"),
      body("Linear Regression fits a straight line (y = ax + b) through the 26-point historical capacity data with financial year as the independent variable. This model assumes a constant annual addition rate equal to the overall historical average. While it provides a conservative baseline, it may underestimate the recent acceleration trend. Trained on n=26 data points (FY2000-FY2025)."),
      h3("Model 2 — Polynomial Regression (Degree 3)"),
      body("Polynomial Regression (degree 3) captures non-linear trends in the capacity growth curve. Unlike linear regression, it can model the acceleration pattern visible in the W1 data. The model fits y = ax\u00b3 + bx\u00b2 + cx + d through the historical data. This model tends to capture growth curvature more accurately but can be sensitive to overfitting, especially at extrapolation points."),
      h3("Model 3 — ARIMA / AR(1) with Differencing"),
      body("An AR(1) model with first-differencing — equivalent to ARIMA(1,1,0) — is applied to the annual additions time series from the W1 dataset. First-differencing achieves stationarity. The model captures autocorrelation in the additions series and forecasts annual additions which are then integrated to yield cumulative capacity. Implemented using numpy/sklearn."),
      h3("Model 4 — Holt Exponential Smoothing"),
      body("Holt's Linear Exponential Smoothing models the level and trend components of the cumulative capacity time series separately, with exponential decay applied to older observations. Grid-search optimisation selects alpha (level) and beta (trend) parameters to minimise in-sample RMSE. Gives more weight to recent W1 data — capturing the re-acceleration since FY2023."),
      h2("3.3 Model Evaluation Metrics"),
      body("Three standard regression evaluation metrics are used: R-squared (R\u00b2) measures the proportion of variance explained; Root Mean Squared Error (RMSE) measures average prediction error in GW; and Mean Absolute Error (MAE) measures the average absolute difference in GW. All metrics are computed in-sample on the W1 training data (FY2000-FY2025)."),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 4
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 4: Historical Trend Analysis"),
      h2("4.1 Compound Annual Growth Rate (CAGR) Analysis"),
      body("CAGR is calculated from W1_Master_Dataset values as: CAGR = (Final Capacity / Initial Capacity)^(1/n) - 1. The base capacity for required-CAGR calculations is 50.04 GW (FY2024-25, latest verified W1 value). The forecast horizon is 5 years (FY2026-FY2030)."),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [2808, 1404, 1404, 1404, 2340],
        rows: [
          headerRow(["Period", "Start (GW)", "End (GW)", "Years (n)", "CAGR"], [2808, 1404, 1404, 1404, 2340]),
          dataRow(["Overall: FY2000-FY2025", "1.02", "50.04", "25", "See Fig 9"], [2808, 1404, 1404, 1404, 2340], false),
          dataRow(["Decade: FY2016-FY2025", "26.80", "50.04", "9", "See Fig 9"], [2808, 1404, 1404, 1404, 2340], true),
          dataRow(["5-Year: FY2021-FY2025", "39.24", "50.04", "4", "See Fig 9"], [2808, 1404, 1404, 1404, 2340], false),
          dataRow(["2-Year: FY2023-FY2025", "42.62", "50.04", "2", "See Fig 9"], [2808, 1404, 1404, 1404, 2340], true),
          dataRow(["Required for 100 GW", "50.04", "100.0", "5", "~15% p.a."], [2808, 1404, 1404, 1404, 2340], false),
          dataRow(["Required for 140 GW", "50.04", "140.0", "5", "~23% p.a."], [2808, 1404, 1404, 1404, 2340], true),
        ]
      }),
      ...spacer(1),
      ...imgPara("fig9_cagr.png",
        "Figure 9 — CAGR Analysis: Historical Growth Rates vs Required CAGR for 2030 Targets. Base: 50.04 GW (W1 FY2024-25).",
        1795, 994),
      h2("4.2 Growth Phase Analysis"),
      h3("Phase 1: Early Growth (FY2000-FY2015)"),
      body("India's wind sector grew from 1.02 GW to 23.39 GW per the W1 dataset, an increase of ~22 GW over 15 years averaging approximately 1.5 GW/year. Growth was driven by the Accelerated Depreciation (AD) benefit and the Generation Based Incentive (GBI) scheme."),
      h3("Phase 2: Spike and Stagnation (FY2016-FY2022)"),
      body("FY2017 saw India's then-record wind addition of 5.50 GW (W1 data), driven by a last rush before the transition from feed-in tariffs to competitive auctions. Subsequent years saw sharp drops due to GST rollout, ISTS waiver uncertainty, and COVID-19. The W1 dataset shows additions fell to just 1.08 GW in FY2022 — the lowest since 2001."),
      h3("Phase 3: Re-acceleration (FY2023-FY2025)"),
      body("From FY2023 onwards, the W1 dataset shows strong re-acceleration: 2.30 GW (FY2023), 3.27 GW (FY2024), and 4.15 GW (FY2025). Key drivers include a stable auction pipeline (SECI issuing 10+ GW/year tenders), policy certainty on ISTS charges, and domestic manufacturing scale-up."),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 5
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 5: Forecast Results"),
      body("All four models are trained on W1_Final_Objective_Dataset.xlsx (FY2000-FY2025, n=26) and forecasted for FY2026-FY2030. Results are benchmarked against both the 100 GW official target and the 140 GW aspirational target."),
      h2("5.1 Linear Regression Forecast"),
      body("Linear Regression applies a constant-slope trend to the full 26-year W1 dataset. With R\u00b2 of 0.9719, the model explains 97.2% of historical variance. However, it anchors to the long-run average addition rate, significantly underestimating recent momentum. The extended dataset (FY2000 vs FY2007) pulls the slope lower, producing more conservative forecasts."),
      ...spacer(1),
      ...imgPara("fig3_linear_regression.png",
        "Figure 3 — Linear Regression Forecast: India Wind Capacity FY2026–FY2030 vs 100 GW and 140 GW Targets. R²=0.9719 | RMSE=2.68 GW.",
        1507, 936),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          headerRow(["Financial Year", "Forecast Capacity (GW)", "Vs 100 GW Gap", "Vs 140 GW Gap"],
                    [2340, 2340, 2340, 2340]),
          dataRow(["FY2026-27", "~53 GW", "~-47 GW", "~-87 GW"], [2340, 2340, 2340, 2340], false),
          dataRow(["FY2027-28", "~55 GW", "~-45 GW", "~-85 GW"], [2340, 2340, 2340, 2340], true),
          dataRow(["FY2028-29", "~56 GW", "~-44 GW", "~-84 GW"], [2340, 2340, 2340, 2340], false),
          dataRow(["FY2029-30", "57.2 GW", "-42.8 GW", "-82.8 GW"], [2340, 2340, 2340, 2340], true),
        ]
      }),
      ...spacer(1),
      verdictBox("STATUS", "NOT ACHIEVED for both targets | R\u00b2=0.9719 | RMSE=2.68 GW | MAE=2.27 GW", RED),
      h2("5.2 Polynomial Regression Forecast (Degree 3)"),
      body("Polynomial Regression (degree 3) captures non-linear trends. With R\u00b2=0.9961, it outperforms the linear model on fit quality. However, the W1 dataset spanning FY2000-FY2025 includes a long early slow-growth phase (FY2000-FY2006) which moderates the degree-3 curvature, resulting in a conservative forecast. This model produces the lowest 2030 projection among the four models."),
      ...spacer(1),
      ...imgPara("fig4_polynomial_regression.png",
        "Figure 4 — Polynomial Regression (Degree-3) Forecast: India Wind Capacity FY2026–FY2030. R²=0.9961 | RMSE=1.00 GW.",
        1507, 936),
      verdictBox("STATUS", "NOT ACHIEVED | R\u00b2=0.9961 | RMSE=1.00 GW | MAE=0.77 GW | FY2030: 52.5 GW", RED),
      h2("5.3 ARIMA / AR(1) Forecast"),
      body("The AR(1) model with first-differencing is applied to the W1 annual additions series. The model identifies the autocorrelation structure in annual additions — which in the W1 data shows a mean-reverting pattern (phi \u2248 -0.28) around a positive drift term. This allows the model to capture the re-acceleration tendency. The ARIMA model gives the most optimistic 2030 projection at 72.4 GW."),
      ...spacer(1),
      ...imgPara("fig5_arima.png",
        "Figure 5 — ARIMA/AR(1) Forecast: Annual Additions & Cumulative Capacity FY2026–FY2030. \u03c6=-0.28 | RMSE=1.41 GW.",
        1695, 1061),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          headerRow(["Financial Year", "Forecast Annual Add (GW/yr)", "Cumulative Capacity (GW)", "Vs 100 GW Gap"],
                    [2340, 2340, 2340, 2340]),
          dataRow(["FY2026-27", "~4.7 GW", "~54.7 GW", "~-45.3 GW"], [2340, 2340, 2340, 2340], false),
          dataRow(["FY2027-28", "~5.5 GW", "~60.2 GW", "~-39.8 GW"], [2340, 2340, 2340, 2340], true),
          dataRow(["FY2028-29", "~6.1 GW", "~66.3 GW", "~-33.7 GW"], [2340, 2340, 2340, 2340], false),
          dataRow(["FY2029-30", "~6.1 GW", "72.4 GW", "-27.6 GW"], [2340, 2340, 2340, 2340], true),
        ]
      }),
      ...spacer(1),
      verdictBox("STATUS", "AT RISK — Best base-case of four models at 72.4 GW | RMSE=1.41 GW | MAE=1.07 GW", ORANGE),
      h2("5.4 Holt Exponential Smoothing Forecast"),
      body("Holt Exponential Smoothing with grid-optimised parameters (alpha=0.85, beta=0.01) gives very high weight to recent W1 data points. The high alpha (0.85) means the model responds rapidly to the most recent observations. The near-zero beta (0.01) indicates the trend estimate changes very slowly. This results in a forecast that projects the current state forward with minimal trend uplift, yielding a conservative 2030 forecast of 52.2 GW."),
      ...spacer(1),
      ...imgPara("fig6_holt.png",
        "Figure 6 — Holt Exponential Smoothing Forecast: India Wind Capacity FY2026–FY2030. \u03b1=0.85 | \u03b2=0.01 | R\u00b2=0.9999.",
        1507, 936),
      verdictBox("STATUS", "AT RISK | R\u00b2=0.9999 | RMSE=0.18 GW | MAE=0.15 GW | FY2030: 52.2 GW", ORANGE),
      h2("5.5 Consolidated Model Comparison"),
      body("The consolidated view reveals that all four models project a 2030 outcome in the range of 52-72 GW — well below the 100 GW target. The ARIMA model, which most directly captures momentum in annual additions, provides the most optimistic base-case projection. None of the four models, even under standard extrapolation, forecasts India reaching 100 GW by FY2030 without policy intervention."),
      ...spacer(1),
      ...imgPara("fig8_all_models.png",
        "Figure 8 — Consolidated ML Forecast Comparison: All Models vs 100 GW & 140 GW Targets. Data: W1_Final_Objective_Dataset.xlsx.",
        1972, 997),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 6
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 6: Scenario Analysis"),
      body("Scenario analysis supplements ML-based extrapolation by explicitly modelling the annual addition rates required to achieve the 100 GW and 140 GW targets. Base capacity is 50.04 GW from W1_Final_Objective_Dataset.xlsx (FY2024-25)."),
      ...spacer(1),
      ...imgPara("fig7_scenario.png",
        "Figure 7 — Scenario Analysis: India Wind Capacity Trajectories FY2026–FY2030. Base: 50.04 GW (W1 FY2024-25).",
        1707, 994),
      h2("6.1 Scenario 1 — Conservative (6 GW/yr)"),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [3900, 5460],
        rows: [
          headerRow(["Parameter", "Value"], [3900, 5460]),
          dataRow(["Target Capacity", "100 GW"], [3900, 5460], false),
          dataRow(["Base Capacity (W1 FY2024-25)", "50.04 GW"], [3900, 5460], true),
          dataRow(["Conservative Addition Rate", "6.0 GW/yr"], [3900, 5460], false),
          dataRow(["FY2030 Outcome", "80.0 GW"], [3900, 5460], true),
          dataRow(["Gap to 100 GW", "-20.0 GW"], [3900, 5460], false),
          dataRow(["Required Rate for 100 GW", "~10.0 GW/yr (2.4x current rate)"], [3900, 5460], true),
        ]
      }),
      h2("6.2 Scenario 2 — Ambitious (140 GW Target)"),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [3900, 5460],
        rows: [
          headerRow(["Parameter", "Value"], [3900, 5460]),
          dataRow(["Target Capacity", "140 GW"], [3900, 5460], false),
          dataRow(["Base Capacity (W1 FY2024-25)", "50.04 GW"], [3900, 5460], true),
          dataRow(["Gap to Close", "89.96 GW"], [3900, 5460], false),
          dataRow(["Required Annual Addition", "~18.0 GW/year"], [3900, 5460], true),
          dataRow(["Current Annual Addition (FY2025)", "4.15 GW/year (W1)"], [3900, 5460], false),
          dataRow(["Uplift Needed", "+13.85 GW/year (+334%)"], [3900, 5460], true),
          dataRow(["Probability (Base Case)", "Not Achievable by 2030"], [3900, 5460], false),
        ]
      }),
      ...spacer(1),
      verdictBox("ASSESSMENT",
        "The 140 GW target is not achievable by 2030 under any realistic scenario. Annual additions would need to reach ~18 GW/year — more than 4x the FY2025 rate of 4.15 GW/yr from W1 data. This target is better repositioned as a 2035 aspirational goal.",
        RED),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 7
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 7: Discussion"),
      h2("7.1 Strengths of India's Wind Sector"),
      bullet("Resource: India's NIWE-assessed potential exceeds 1,163 GW at 120m hub height — among the largest undeveloped wind resources globally, particularly in Rajasthan, Gujarat, Karnataka, Tamil Nadu, and Maharashtra."),
      bullet("Manufacturing: Domestic production capacity of 24 GW/year — sufficient for 6x current deployment — with high-quality turbine manufacturers including Suzlon, GE, and Siemens Gamesa."),
      bullet("Growth: The W1 dataset documents accelerating additions: 1.08 GW (FY2022) → 2.30 GW (FY2023) → 3.27 GW (FY2024) → 4.15 GW (FY2025) — structural momentum that statistical models may underestimate."),
      bullet("Policy: SECI's stable auction pipeline, ISTS waiver, Renewable Purchase Obligations, and Production Linked Incentive schemes provide a supportive regulatory environment."),
      bullet("Economics: Wind tariffs of Rs 2.8-3.2/kWh make new wind power one of the cheapest energy sources in India, driving strong DISCOM offtake interest."),
      h2("7.2 Key Challenges"),
      bullet("Grid: Transmission infrastructure build-out lags renewable capacity additions. Green Energy Corridor implementation is behind schedule."),
      bullet("Land: Large wind projects (100-500 MW) require significant land parcels with complex acquisition patterns. Average project development time is 3-4 years."),
      bullet("Offshore: Despite a 30 GW offshore target and policy frameworks since 2015, not a single offshore MW has been commissioned."),
      bullet("DISCOMs: State electricity distribution companies remain financially stressed, creating PPA enforcement risks and delaying new capacity procurement."),
      bullet("Financing: India's cost of capital for renewable projects (10-12%) remains significantly above global peers (5-7%)."),
      h2("7.3 Opportunities"),
      bullet("Hybrid: Co-located wind-solar hybrids optimise land use, grid infrastructure and generation profiles. Hybrid projects improve grid dispatchability."),
      bullet("Repowering: India has over 5,000 MW of pre-2005 wind turbines rated below 1 MW. Repowering with modern 3-5 MW turbines could add 3-5 GW of effective capacity without new land acquisition."),
      bullet("Offshore: India's western coast (Gujarat) and southern coast (Tamil Nadu) have identified offshore wind zones with strong wind resources. 1-2 GW of offshore capacity by 2028-29 is achievable with proper support."),
      bullet("Green Hydrogen: India's National Green Hydrogen Mission creates a new demand source for dedicated wind power, opening large-scale off-take opportunities."),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 8
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 8: Recommendations"),
      h2("8.1 Policy Recommendations"),
      bullet("Scale auctions: Immediately increase SECI wind auction pipeline to 18 GW/year (from current ~10 GW/year) to create a 3-year commissioning backlog adequate for 10 GW/year of actual installations."),
      bullet("PPA mandate: Mandate state DISCOMs to execute Power Purchase Agreements for minimum 5 GW/year of new wind capacity — backstop government guarantee to reduce PPA default risk."),
      bullet("Governance: Establish a Wind Energy Fast-Track Committee under the Prime Minister's Office to resolve land, grid and financing bottlenecks within 90-day timelines."),
      bullet("ISTS waiver: Provide explicit policy confirmation of ISTS waiver for wind projects commissioned before FY2030 — reducing financing uncertainty and lowering tariffs by Rs 0.10-0.20/kWh."),
      h2("8.2 Grid and Infrastructure Recommendations"),
      bullet("GEC Phase 2: Accelerate Green Energy Corridor Phase 2 completion to FY2027 — unlock grid evacuation for 20+ GW of wind and solar in Karnataka, Rajasthan, Gujarat and Andhra Pradesh."),
      bullet("REZ: Pre-build transmission in 10 designated Renewable Energy Zones (REZs) ahead of project commissioning — eliminate the 2-3 year commissioning-to-evacuation lag."),
      bullet("HVDC: Deploy HVDC corridors from Rajasthan to southern and eastern demand centres — 8,120 ckt km identified by CEA as high priority."),
      bullet("Investment: Increase annual transmission investment from Rs 50,000 crore to Rs 80,000 crore — parallel to renewable deployment ramp."),
      h2("8.3 Industry and Manufacturing Recommendations"),
      bullet("Manufacturing utilisation: Raise wind manufacturing utilisation from 25% to 60%+ by 2028 — currently 24 GW/year capacity is installed but less than 5 GW/year is utilised."),
      bullet("Finance: Facilitate access to blended finance (green bonds, concessional IREDA loans) to reduce project cost of capital from 10-12% to 7-8%."),
      h2("8.4 Technology Recommendations"),
      bullet("Repowering: Launch a National Wind Repowering Programme — replace 5,000+ MW of sub-1 MW turbines installed before FY2005 with modern 3-5 MW machines. Net capacity gain: 3,000-5,000 MW with no new land required."),
      bullet("Hub heights: Increase turbine hub heights to 140-160 metres to open 380+ GW of additional resource in states like Madhya Pradesh, Chhattisgarh and Jharkhand."),
      h2("8.5 Offshore Wind Recommendations"),
      bullet("Tamil Nadu pilot: Launch 500 MW offshore wind pilot project off Tamil Nadu coast in FY2027. Provide enhanced VGF of Rs 150-200 billion to make the tariff competitive."),
      bullet("Gujarat: Launch second offshore zone off Gujarat (Kutch coast) — target 500 MW award in FY2027, commissioning FY2029."),
      bullet("Authority: Create dedicated Offshore Wind Development Authority under MNRE — resolve multi-ministry jurisdictional overlap through single-window clearance."),
      ...spacer(1),
      verdictBox("REVISED TARGET RECOMMENDATION",
        "Given the W1 dataset trajectory and infrastructure constraints, this report recommends India formally revise targets to: 75-80 GW by FY2030 (realistic with current momentum) and 100 GW by FY2033 (achievable with policy acceleration).",
        NAVY),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // CHAPTER 9 — CONCLUSION
      // ══════════════════════════════════════════════════════════════════════
      h1("Chapter 9: Conclusion"),
      body("Historical trend analysis and machine learning forecasting models trained on W1_Final_Objective_Dataset.xlsx (FY2000-FY2025, n=26) provide a consistent and clear picture of India's wind energy trajectory: the sector is on a strong and accelerating growth path, but the pace of deployment falls short of what is required to meet the official 100 GW target by FY2030."),
      body("Under all four forecasting models applied in this study — Linear Regression, Polynomial Regression (Degree-3), ARIMA/AR(1), and Holt Exponential Smoothing — India's projected wind capacity by FY2030 falls in the range of 52.2 GW (Holt) to 72.4 GW (ARIMA). The range reflects genuine uncertainty about the pace of the current growth acceleration. The ARIMA model, which most directly captures momentum in annual additions, provides the most optimistic base-case projection."),
      body("Achieving the 100 GW target is not impossible, but it requires a significant policy-driven acceleration. Annual additions must grow from 4.15 GW (FY2024-25 per W1 data) to approximately 10 GW/year — and sustain this level for five consecutive years. India's domestic manufacturing capacity (24 GW/year) is more than sufficient; the binding constraints are transmission infrastructure, project development timelines, and DISCOM procurement pace."),
      body("The 140 GW aspirational target is not achievable by FY2030 under any realistic scenario per W1 data projections. It would require annual additions of approximately 18 GW/year — more than 4x the current rate of 4.15 GW/yr. This target is better repositioned as a 2035 goal."),
      ...spacer(1),
      verdictBox("FINAL VERDICT",
        "100 GW by 2030: AT RISK — Achievable only with sustained ~10 GW/year additions and full execution of the project pipeline. Requires immediate policy acceleration. | 140 GW by 2030: NOT ACHIEVABLE — Requires transformational deployment at 18 GW/yr, 4x the current rate. Recommended to reposition as a 2035 goal.",
        NAVY),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // APPENDIX A
      // ══════════════════════════════════════════════════════════════════════
      h1("Appendix A: W1_Final_Objective_Dataset.xlsx — Complete Historical Data"),
      h2("A.1 W1_Master_Dataset (FY2000–FY2025)"),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [1872, 2496, 1872, 1872, 1248],
        rows: [
          headerRow(["Financial Year", "Cumulative Capacity (GW)", "Annual Addition (GW)", "YoY Growth %", "Use for Model"],
                    [1872, 2496, 1872, 1872, 1248]),
          dataRow(["FY2000", "1.024", "—", "—", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2001", "1.161", "0.137", "13.4%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2002", "1.367", "0.206", "17.7%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2003", "1.628", "0.261", "19.1%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2004", "1.870", "0.242", "14.9%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2005", "2.483", "0.613", "32.8%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2006", "3.585", "1.102", "44.4%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2007", "7.114", "3.529", "98.4%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2008", "8.098", "0.984", "13.8%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2009", "10.182", "2.084", "25.7%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2010", "11.753", "1.571", "15.4%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2011", "14.089", "2.336", "19.9%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2012", "17.277", "3.188", "22.6%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2013", "19.899", "2.622", "15.2%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2014", "21.077", "1.178", "5.9%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2015", "23.394", "2.317", "11.0%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2016", "26.797", "3.403", "14.5%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2017", "32.302", "5.505", "20.5%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2018", "34.136", "1.834", "5.7%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2019", "35.626", "1.490", "4.4%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2020", "37.719", "2.093", "5.9%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2021", "39.243", "1.524", "4.0%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2022", "40.324", "1.081", "2.8%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2023", "42.620", "2.296", "5.7%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
          dataRow(["FY2024", "45.885", "3.265", "7.7%", "Yes"], [1872, 2496, 1872, 1872, 1248], false),
          dataRow(["FY2025", "50.038", "4.152", "9.0%", "Yes"], [1872, 2496, 1872, 1872, 1248], true),
        ]
      }),
      pb(),

      // ══════════════════════════════════════════════════════════════════════
      // APPENDIX B
      // ══════════════════════════════════════════════════════════════════════
      h1("Appendix B: Model Accuracy Metrics"),
      h2("B.1 In-Sample Performance Metrics (Trained on W1 Dataset, n=26)"),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [2340, 1404, 1404, 1404, 2808],
        rows: [
          headerRow(["Model", "R\u00b2", "RMSE (GW)", "MAE (GW)", "FY2030 Forecast"],
                    [2340, 1404, 1404, 1404, 2808]),
          dataRow(["Linear Regression",       "0.9719", "2.68", "2.27", "57.2 GW"], [2340, 1404, 1404, 1404, 2808], false),
          dataRow(["Polynomial Reg. (Deg-3)", "0.9961", "1.00", "0.77", "52.5 GW"], [2340, 1404, 1404, 1404, 2808], true),
          dataRow(["ARIMA / AR(1)",           "—",      "1.41", "1.07", "72.4 GW"], [2340, 1404, 1404, 1404, 2808], false),
          dataRow(["Holt Exp. Smoothing",     "0.9999", "0.18", "0.15", "52.2 GW"], [2340, 1404, 1404, 1404, 2808], true),
        ]
      }),
      ...spacer(1),
      body("Note: ARIMA R\u00b2 is computed on the annual additions series (stationary after differencing), not cumulative capacity. The high Holt R\u00b2 (0.9999) reflects the model's ability to fit the training data very closely with alpha=0.85, though this high responsiveness to recent data means extrapolation is conservative when recent growth has been moderate. The W1 dataset's extended history (FY2000-FY2025, n=26 vs original n=20) provides richer training signal for all models."),
      h2("B.2 All Models FY2030 Forecast Comparison"),
      new Table({
        width: { size: pageW, type: WidthType.DXA },
        columnWidths: [2340, 1755, 1755, 1755, 1755],
        rows: [
          headerRow(["Model", "FY2030 FC (GW)", "Gap to 100 GW", "Status", "RMSE (GW)"],
                    [2340, 1755, 1755, 1755, 1755]),
          dataRow(["Linear Regression",       "57.2", "-42.8 GW", "AT RISK", "2.68"], [2340, 1755, 1755, 1755, 1755], false),
          dataRow(["Polynomial Reg. (Deg-3)", "52.5", "-47.5 GW", "AT RISK", "1.00"], [2340, 1755, 1755, 1755, 1755], true),
          dataRow(["ARIMA / AR(1)",           "72.4", "-27.6 GW", "AT RISK", "1.41"], [2340, 1755, 1755, 1755, 1755], false),
          dataRow(["Holt Exp. Smoothing",     "52.2", "-47.8 GW", "AT RISK", "0.18"], [2340, 1755, 1755, 1755, 1755], true),
          dataRow(["Ensemble Average",        "58.6", "-41.4 GW", "AT RISK", "—"],    [2340, 1755, 1755, 1755, 1755], false),
        ]
      }),
      ...spacer(2),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 240, after: 0 },
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: NAVY, space: 8 } },
        children: [
          new TextRun({ text: "India Wind Capacity Outlook 2030  |  Prepared for NIWE  |  June 2026  |  Energy Analytics Division",
            size: 18, color: "7F8C8D", font: "Arial", italics: true }),
        ]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 80, after: 0 },
        children: [
          new TextRun({ text: "Data Sources: W1_Final_Objective_Dataset.xlsx | MNRE | CEA | PIB | NIWE | GWEC 2026 | UNFCCC NDC",
            size: 17, color: "95A5A6", font: "Arial" }),
        ]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 60, after: 0 },
        children: [
          new TextRun({ text: "Confidential | For Official Use Only", bold: true,
            size: 17, color: NAVY, font: "Arial" }),
        ]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/home/claude/india-wind-2030/India_Wind_Outlook_2030_FINAL.docx', buffer);
  console.log('✔  Report saved: India_Wind_Outlook_2030_FINAL.docx');
});
