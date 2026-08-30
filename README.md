<div align="center">
  <img src="https://img.shields.io/badge/RISK-OPTIMA-0284c7?style=for-the-badge&logoColor=white" alt="RiskOptima Logo">
  <br><br>
  <h1>🔷 RiskOptima</h1>
  <p><b>Enterprise Asset Criticality & Risk Topology Platform</b></p>
  <p><i>A NIST SP 800-30 compliant tactical intelligence engine for modern SOCs.</i></p>
  <br>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge&color=10b981" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&color=38bdf8" alt="Python">
  <img src="https://img.shields.io/badge/Flask-API-black?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Security-NIST_800--30-red?style=for-the-badge&color=f43f5e" alt="NIST Standard">
</div>

<br>

## 📖 Overview

**RiskOptima** is an advanced, enterprise-grade asset criticality framework engineered for Security Operations Centers (SOC) and Incident Response teams. Moving beyond flat asset inventories, it dynamically computes weighted risk scores and maps cascading breach scenarios across complex network architectures.

Designed with a clean, corporate intelligence interface, it allows security teams to instantly triage vulnerabilities, simulate blast radii, and generate executive-ready PDF reports.

---

## 🔥 Core Capabilities

*   🧠 **Tactical Criticality Engine:** Computes contextual risk scores using a weighted algorithm across four operational vectors: `Impact`, `Likelihood`, `RTO`, and `Exposure`.
*   ⚡ **Automated Tier Classification:** Instantly categorizes infrastructure into actionable response tiers (Tier 1 Critical to Tier 5 Informational) to govern enterprise patching cycles.
*   💥 **Blast Radius Simulator:** Maps theoretical breaches on core assets (e.g., AD, Edge Firewalls) to dynamically calculate downstream cascading effects across the network topology.
*   📄 **Executive PDF Reporting:** Features a one-click automated report generation engine for leadership, risk officers, and compliance audits.
*   🔄 **Frictionless Ingestion:** Supports seamless bulk ingestion via formatted `.csv` / `.txt` templates alongside manual entry modes.

---

## 📐 Mathematical Risk Model

Asset priority is determined using a tactical equation that balances operational pressure with architectural exposure:

> **Risk Score = (Impact × 2) + (Likelihood × 1) + (RTO × 2) + (Exposure × 1)**

### Tier Threshold Hierarchy

| Tier Level | Score Range | Operational Response Protocol |
| :--- | :--- | :--- |
| 🔴 **Tier 1 (Critical)** | `≥ 26` | Immediate emergency containment required. |
| 🟠 **Tier 2 (High)** | `20 – 25` | High priority continuous monitoring. |
| 🟢 **Tier 3 (Medium)** | `14 – 19` | Standard maintenance window patching. |
| 🔵 **Tier 4-5 (Low)** | `< 14` | Routine background audit cycle. |

---

## 🛠️ Technology Stack

*   **Backend Core:** Python 3, Flask API
*   **Database:** SQLite (Relational mapping for dynamic assets)
*   **Report Engine:** ReportLab (PDF Export Standard)
*   **Frontend UI:** HTML5, Bootstrap 5, Custom Enterprise CSS
*   **Visualizations:** Chart.js (Interactive analytical metrics)

---

## 🚀 Deployment Guide

Deploy RiskOptima locally within an isolated environment:

```bash
# 1. Clone the repository
git clone https://github.com/ZUNATIC/Risk-Optima.git
cd Risk-Optima

# 2. Initialize a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Launch the intelligence engine
python3 app.py
```
*The platform will launch at `http://127.0.0.1:5000`. The database automatically initializes with sample enterprise assets on the first boot.*

---

## 👨‍💻 Author

Engineered by **Umae Habiba (@ZUNATIC)**
