# Engine Log Analyzer – Release 1

A modular log analysis tool designed to **review, validate, and summarize system logs**
from Engine, Agente ETL, and related services over a defined time period.

This first release focuses on **batch log ingestion, checker execution, and CSV-based outputs**
to support operational analysis and troubleshooting.

---

## 🎯 Release 1 Objective

Provide a **reliable offline log review pipeline** that:

* Reads logs from a dataset folder for a given date range
* Executes common and domain-specific checkers
* Aggregates findings
* Produces structured outputs (CSV + console summaries)

This release establishes the **core architecture** for future analytical and visual extensions.

---

## 📂 Supported Log Domains (v1)

* **Engine**
* **Agente ETL**
* *(WebService focus planned for future releases)*

---

## 🧱 Core Functionalities

### 1️⃣ Log Ingestion & Filtering

* Reads logs from a dataset directory
* Filters log files by **date embedded in filename**
* Supports configurable **start and end dates**
* Processes logs **line by line**
* Normalizes log entries into a structured format:

  * Timestamp
  * Severity
  * Module
  * Message
  * Checker source

---

### 2️⃣ Checker Architecture

The system uses a **pluggable checker model**, allowing multiple checkers to be executed over the same log stream.

#### 🔹 Common Checkers (all log types)

* Uptime calculation over the selected period
* Detection of uptime gaps outside a defined threshold
* Warning aggregation:

  * Count by severity
  * Count by message
* Error aggregation:

  * Count by severity
  * Count by message

**Outputs:**

* Full results exported to CSV
* Top 10 most frequent warnings and errors printed to console

---

### 3️⃣ Domain-Specific Checkers (Release 1)

#### ⚙️ Engine Checkers

* Detection and count of **expired events**
* Event lifecycle timing analysis:

  * Capture phase
  * JSON wait phase
  * Result delivery phase
* Event finalization and category aggregation
* Trigger vs total event pairing

---

#### 🔄 Agente ETL Checkers

* Validation of **BDI response presence** per event
* Detection of missing or invalid ETL responses

---

### 4️⃣ Output Generation

Release 1 focuses on **structured, analyzable outputs**:

* 📄 **CSV files**

  * One CSV per analysis scope (common, engine, etl)
  * Full, non-aggregated data for post-processing
* 🖥️ **Console summaries**

  * Top 10 warnings
  * Top 10 errors
  * Key counters per checker

> PDF, image, and graphical outputs are intentionally deferred to future releases.

---

## 🗂️ Project Structure (Simplified)

```
LogsReviewer/
├── main.py
├── config/
│   └── config.json
├── core/
│   ├── run_core.py
│   ├── log_parser.py
│   ├── log_iterator.py
│   └── writers/
│       └── csv_writer.py
├── checkers/
│   ├── common/
│   ├── engine/
│   └── etl/
└── output/
    └── *.csv
```

---

## ⚙️ Configuration

The analysis is driven by a JSON configuration file:

* Dataset root path
* Folders to analyze
* Start and end dates
* Enabled log domains

This allows repeatable, non-interactive batch execution.

---

## 🚦 Release Status

**Release 1 – Core Operational Version**

✔ Log ingestion by date
✔ Common and domain-specific checkers
✔ CSV output generation
✔ Console summaries
✔ Stable batch execution

---

## 🔮 Planned for Future Releases

* Graphical outputs (charts, timelines)
* PDF / report generation
* WebService-specific checkers
* Real-time or streaming analysis
* Dashboard integration
* Advanced correlation between domains

