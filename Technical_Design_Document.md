# Technical Design Document (TDD)
## ABLBL Sourcing Intelligence Platform (v1.0)
**Aditya Birla Lifestyle Brands Limited (ABLBL) — Sourcing & Procurement Analytics**

---

## 1. Executive Summary & Purpose

This **Technical Design Document (TDD)** defines the software architecture, data schemas, mathematical decision algorithms, codebase module hierarchy, and data integration specifications for the **ABLBL Sourcing Intelligence Platform**. 

The platform is designed to automate fabric cost benchmarking, vendor performance evaluation, seasonal price negotiation support, and global fiber market commodity tracking for ABLBL procurement and sourcing teams.

---

## 2. System Architecture & Technology Stack

The application follows a modular **3-Tier Analytics Architecture**:

```
 ┌─────────────────────────────────────────────────────────────┐
 │                PRESENTATION LAYER (UI)                      │
 │    Streamlit Web Framework + Custom CSS (utils/theme.py)    │
 │    Interactive Plotly Express Visualizations & Dashboard    │
 └──────────────────────────────┬──────────────────────────────┘
                                │ (Calls View Services)
 ┌──────────────────────────────▼──────────────────────────────┐
 │                BUSINESS LOGIC & SERVICE LAYER               │
 │    Price Volatility CV Engine | Cost Benchmark Engine       │
 │    Cascading Spec Filter Engine | Dynamic AI Advice Generator│
 └──────────────────────────────┬──────────────────────────────┘
                                │ (Reads Raw Datasets)
 ┌──────────────────────────────▼──────────────────────────────┐
 │                 DATA ACCESS & PERSISTENCE LAYER             │
 │    Pandas Data Processing | OpenPyXL Excel Engine           │
 │    Raw Master Files: Vendor Master, SS27 Specs, Fibre Data  │
 └─────────────────────────────────────────────────────────────┘
```

### Technology Specifications:
* **Frontend / UI**: Streamlit 1.30+
* **Data Processing Engine**: Python 3.10+, Pandas 2.0+
* **Data Visualization**: Plotly Express, Plotly Graph Objects
* **Data Store**: Excel (.xlsx) & CSV Data Store (`data/raw/`)
* **Styling**: Vanilla CSS with HSL dark mode, Glassmorphism cards, and GitHub-styled alert banners.

---

## 3. Directory & Codebase Map

```
ABLBL_Sourcing_Intelligence_Platform/
│
├── app.py                             # Main Application Entry Point & Navigation Router
│
├── views/                             # Presentation Layer View Components
│   ├── home.py                        # Executive Command Center & Data Provenance Badges
│   ├── vendor_directory.py            # Technical Supplier Capability Search
│   ├── vendor_commercial_directory.py # Commercial & Technical SS27 Capability Search
│   ├── vendor_360.py                  # Enterprise Supplier 360 & Historical NLC Trend Engine
│   ├── vendor_commercial_360.py       # SS27 Commercial 360 & Sourcing Decision Engine
│   ├── fibre_market.py                # Fibre Commodity Intelligence & Multi-Year Trends
│   ├── yarn_market.py                 # Yarn Market Analytics
│   ├── commercial_market.py           # Commercial Market Analytics
│   ├── supplier_quality.py            # Quality Audit & Performance Rating
│   ├── Cost_Simulator.py              # Costing Breakdown Simulator
│   ├── Decision_Center.py             # Strategic Vendor Decision Center
│   └── ai_Copilot.py                  # Conversational Sourcing Assistant
│
├── data/                              # Data Service & Ingestion Layer
│   ├── loaders.py                     # Excel Master Data Ingestion & Sanitization Engine
│   ├── vendor_service.py              # Vendor Master Filtering & Cascading Service
│   ├── commercial_vendor_service.py   # SS27 Commercial Data Filtering Service
│   └── raw/                           # Raw Excel Master Files Storage
│
└── utils/                             # Utility & Shared UI Components
    ├── theme.py                       # Global CSS Design Tokens & Dark Theme Styling
    ├── header.py                      # Reusable Page Header Renderer
    ├── formatters.py                  # Currency & Unit Formatting Helpers
    ├── currency_prices.py             # Forex Rate Tables & Currency Converter
    ├── fibre_snapshot_ui.py           # Home Page Fibre Price Widget
    └── currency_snapshot_ui.py        # Home Page Forex Rate Widget
```

---

## 4. Mathematical Algorithms & Decision Logic Specifications

### 4.1 Cost Competitiveness Variance (%) Formula
Measures supplier cost performance against the category average benchmark:

$$\text{Cost Variance \%} = \left( \frac{\text{Vendor Mean NLC} - \text{Category Mean NLC}}{\text{Category Mean NLC}} \right) \times 100$$

* **Historical Tolerance Band ($\pm 4\%$)**:
  * $\text{Variance} < -4\% \rightarrow$ **🟢 Competitive (Cheaper than Category Average)**
  * $\text{Variance} > +4\% \rightarrow$ **🔴 Premium (Above Category Average - Target for Negotiation)**
  * $-4\% \le \text{Variance} \le +4\% \rightarrow$ **🟡 Market Aligned**
* **SS27 Season Tolerance Band ($\pm 3\%$)**:
  * $\text{Variance} < -3\% \rightarrow$ **🟢 Best-in-Class**
  * $\text{Variance} > +3\% \rightarrow$ **🔴 Premium**
  * $-3\% \le \text{Variance} \le +3\% \rightarrow$ **🟡 Market Competitive**

---

### 4.2 NLC Price Stability / Volatility Formula (Coefficient of Variation)
Measures historical price fluctuation across Purchase Orders (POs) for a vendor:

$$\text{CV \%} = \left( \frac{\sigma_{\text{Vendor NLC}}}{\mu_{\text{Vendor NLC}}} \right) \times 100$$

Where $\sigma$ is the sample standard deviation of `Actual NLC`, and $\mu$ is the sample mean.

* **Rating Thresholds**:
  * $\text{CV} < 5\% \rightarrow$ **🟢 High Price Stability**
  * $5\% \le \text{CV} < 12\% \rightarrow$ **🟡 Moderate Price Fluctuation**
  * $\text{CV} \ge 12\% \rightarrow$ **🔴 High Fluctuation / Price Volatility Risk**

---

### 4.3 Vendor Strategic Rating Matrix
Combines Cost Competitiveness and Price Volatility into a single strategic rating:

| Cost Status | Price Stability (CV %) | Vendor Strategic Rating |
| :--- | :--- | :--- |
| **Cheaper ($<-4\%$)** | **Stable ($\text{CV} < 12\%$)** | ⭐ **Tier 1 Preferred Supplier** |
| **Premium ($>+4\%$)** | *Any* | ⚠️ **Tier 2 (Renegotiation Target)** |
| **Market Aligned ($\pm 4\%$)** | *Any* | 🔹 **Tier 2 Commercial Supplier** |
| **Cheaper ($<-4\%$)** | **Volatile ($\text{CV} \ge 12\%$)** | 🔹 **Tier 2 Commercial Supplier** |

---

### 4.4 52-Week Percentile Rank Formula (Commodity Intelligence)
Positions current commodity quotes within their 12-month historical trading range:

$$\text{Percentile Rank} = \left( \frac{P_{\text{current}} - P_{\text{52wk\_min}}}{P_{\text{52wk\_max}} - P_{\text{52wk\_min}}} \right) \times 100$$

* **Action Signal Logic**:
  * $\text{Percentile Rank} \le 35 \rightarrow$ **🟢 LOCK CONTRACTS** (Buy signal - bottom of 12-month price curve).
  * $\text{Percentile Rank} \ge 70 \rightarrow$ **🔴 HOLD BULK POs** (Hold signal - near 12-month high).
  * $35 < \text{Percentile Rank} < 70 \rightarrow$ **🟡 SPOT BUYING** (Normal trading band).

---

### 4.5 Price-Active Cascading Dropdown Filter Algorithm
To prevent "dead-end filtering" (selecting specs with zero NLC data), Section 4 of `vendor_360.py` implements an active cascading filter:

$$\text{Vendor\_Info} \xrightarrow{\text{Filter NLC } > 0} \text{NLC\_Active\_DF} \xrightarrow[\text{Select Comp}]{\text{Cascading}} \text{Count\_DF} \xrightarrow[\text{Select Count}]{\text{Cascading}} \text{Weave\_DF} \xrightarrow[\text{Select Weave}]{\text{Cascading}} \text{Finish\_DF}$$

Every selection dynamically rebuilds subsequent dropdown options, guaranteeing that **100% of selected filter combinations render a valid NLC trend graph and specification matrix**.

---

## 5. Master Data Schemas & Column Mappings

### 5.1 Vendor Master Schema (`vendor_master.xlsx`)
* `Vendor Name` (String) — Primary supplier name.
* `ERP Standard Composition` / `Composition` (String) — Fabric fiber mix (e.g. 100% Cotton, PVL 63/34/3).
* `ERP Count Capability` / `Count` (String) — Yarn count spec (e.g. 2/82, 2/82).
* `Weave` (String) — Weave structure (Plain, Twill, Satin, Dobby).
* `Finish` (String) — Fabric finishing treatment (Liquid Ammonia, Normal Soft, Mercerized).
* `Dye Type` (String) — Piece Dyed, Yarn Dyed, Printed.
* `Actual NLC` (Float) — Agreep PO Net Landed Cost in ₹/meter.
* `AW23 NLC` ... `AW26 NLC` (Float) — Historical seasonal quoted NLC prices.

### 5.2 SS27 Quality Specs Schema (`quality_specs_ss27.xlsx`)
* `Fabric code` (String) — Unique fabric line item ID.
* `Fabric Composition` (String) — Seasonal composition.
* `NLC/meter` (Float) — SS27 quoted Net Landed Cost per meter.
* `MOQ` (String/Integer) — Minimum Order Quantity in meters.
* `Ex mill lead time` (String/Integer) — Production dispatch lead time in days.

---

## 6. Enterprise IT Data Integration & Data Source Specifications

To transition the platform from batch Excel files to automated enterprise production pipelines, the IT Data Analytics team will integrate the following external API sources and internal SAP/ERP databases:

### 6.1 External Data Sources & Live API Endpoints

| Commodity / Asset | Fiber / Currency | Target External Data Source | Refresh Frequency | Proposed Integration Protocol |
| :--- | :--- | :--- | :--- | :--- |
| **Domestic Cotton** | DCH 32, Shankar 6, MCU 5 | **MCX** (Multi Commodity Exchange India) / **CAI** (Cotton Assoc. of India) | Daily (EOD) | REST API / Web Scraper Service |
| **US Cotton** | Upland Cotton, Pima | **ICE Futures US** (Intercontinental Exchange) / **USDA** | Daily | REST API (Market Data Feed) |
| **Chinese Cotton** | China Cotton | **Zhengzhou Commodity Exchange (ZCE)** / **CCF Group** | Daily | API / Data Feed Integration |
| **Global Cotton Benchmark** | Cotlook A Index | **Cotlook Ltd** (Liverpool) | Daily | Cotlook Web Data Feed |
| **Man-Made Fibers** | Viscose Staple Fiber (VSF), Polyester (PSF) | **CCF Group** / **ICIS Chemical Intelligence** | Weekly | API / Automated SFTP CSV Drop |
| **Flax / Linen** | European Linen | **CELC** (European Confederation of Flax & Hemp) | Monthly | Data Ingestion Pipeline |
| **Forex Rates** | USD/INR, EUR/INR, CNY/INR | **ECB** (European Central Bank) / **RBI** / **Open Exchange Rates API** | Real-time / Daily | REST API (`https://openexchangerates.org/api/`) |

---

### 6.2 Internal Enterprise ERP / SAP System Integration

To automate historical supplier NLC scoring and SS27 quotation benchmarks, the IT Data Analytics team will replace static `.xlsx` master files with direct SQL database views mapped to internal enterprise systems:

```
  ┌─────────────────────────┐       ┌─────────────────────────┐
  │   SAP MM (Vendor Master) │       │   Centric PLM / Sourcing│
  │   Tables: LFA1, LFB1    │       │   SS27 Quotation Specs  │
  └────────────┬────────────┘       └────────────┬────────────┘
               │                                 │
               └────────────────┬────────────────┘
                                │
                                ▼
               ┌─────────────────────────────────┐
               │ SAP PO Tables (EKKO, EKPO, MSEG) │
               │ Actual Contracted NLC Data      │
               └────────────────┬────────────────┘
                                │
                                ▼
               ┌─────────────────────────────────┐
               │    SQL Server / Snowflake DW    │
               │    `vw_Vendor_NLC_Intelligence` │
               └────────────────┬────────────────┘
                                │
                                ▼
               ┌─────────────────────────────────┐
               │  ABLBL Platform (Pandas / UI)   │
               └─────────────────────────────────┘
```

#### Database View Schemas Required from IT:

1. **`vw_Vendor_NLC_Master`** (Historical Procurement Data):
   * `Vendor_ID`, `Vendor_Name`, `Mill_Category`, `Origin`
   * `ERP_Standard_Composition`, `ERP_Count_Capability`, `Weave`, `Finish`, `Dye_Type`
   * `Actual_PO_NLC` (Net Landed Cost = Basic Price + Freight + Customs Duty + Handling)
   * `PO_Date`, `PO_Number`, `Season` (`AW23` through `AW26`)

2. **`vw_SS27_Quality_Quotation_Specs`** (Seasonal Commercial Quotes):
   * `Fabric_Code`, `Vendor_Name`, `Fabric_Composition`, `Count`, `Weave`, `Finish`
   * `Quoted_NLC_Meter`, `Basic_Price_Meter`, `MOQ_Meters`, `Ex_Mill_Lead_Time_Days`
