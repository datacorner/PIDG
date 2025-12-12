# PIDG – pyBPPIBridge

PIDG (pyBPPIBridge) is a Python toolkit that helps you extract, transform, and analyze process data produced by Blue Prism and related process intelligence tools. It focuses on turning raw execution logs into clean, analytics‑ready datasets you can use for process mining, KPI tracking, and reporting.

## Features

- Connect to Blue Prism control room or exported event logs (CSV, database, or API; adapt to your actual inputs).
- Normalize and enrich events with business‑friendly attributes (case, activity, resource, timestamps).
- Export datasets compatible with common process mining tools and Python data‑science stacks.
- Basic quality checks (missing timestamps, inconsistent cases, etc.) with clear warnings.

## Installation

PIDG is a regular Python project. Clone the repository and install the dependencies in a virtual environment:

```bash
git clone https://github.com/datacorner/PIDG.git
cd PIDG

python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Quick start

Below is a minimal example showing the typical flow: load raw data, transform it, and save a process‑mining‑ready table. Adapt the module and function names to match your actual package layout.

```python
from pidg import loader, transformer, exporter

# 1. Load raw execution logs (CSV / DB / API)
events = loader.load_blueprism_csv("data/raw/blueprism_log.csv")

# 2. Transform into an event log with standard fields
event_log = transformer.to_event_log(
    events,
    case_column="case_id",
    activity_column="stage_name",
    start_column="start_time",
    end_column="end_time",
    resource_column="resource"
)

# 3. Export to CSV or parquet for process mining tools
exporter.to_csv(event_log, "data/processed/event_log.csv")
```

## Repository structure

```text
PIDG/
  ├─ pidg/                 # Core Python package (bridge, loaders, transformers)
  ├─ examples/             # Example scripts and notebooks
  ├─ config/               # Connection and mapping configuration files
  ├─ tests/                # Automated tests
  ├─ data/                 # Optional sample data (small, anonymized)
  ├─ exe/                  # Packaged executables or helpers
  ├─ requirements.txt      # Python dependencies
  └─ setup.py / pyproject.toml  # Packaging metadata (if present)
```

## Configuration

Connections and mappings are usually defined in configuration files so you can reuse the same code across environments. A typical configuration might include:

- Data source type (CSV, database, API).
- Connection parameters (server, database, credentials, schema).
- Column mappings (which fields map to case, activity, timestamps, resource).
- Filtering rules (date range, process names, environments).

##  This Data Bridge provides data access and load from these data sources :  

✅  External file (csv)  
✅  External Excel Spreadsheet (xls, xlsx, xlsm, xlsb, odf, ods and odt)  
✅  External XES File  
✅  ODBC Data Sources (checked with SQL Server) by using an configurable SQL query  
✅  Blue Prism (Via session logs, Blue Prism API and/or vbo usage)  
✅  SAP Read Table via SAP RFC  

This BPPI Data Bridge reads the data from the Datasource and upload them into the BPPI Repository. Inside BPPI it's also possible to configure a TODO to automate some transformations and load the data into a BPPI Project (The program can execute thess To Do automatically). To make this bridge usable the user must configure a Data Source in the BPPI Repository, and get a token.  

*✨ Note: BPPI (Blue Prism Process Intelligence) is the solution provided by Blue Prism for Process and Task Mining (ABBYY Timeline OEM)*
👉 [Look at the wiki for more informations](https://exypro.org/docs/pybppibridge-documentation/)
👉 [Install the BPPI Bridge via pyPI](https://pypi.org/project/pyBPPIBridge/)
👉 [in case of an issue, please add an entry here](https://exypro.org/Discussions/forum/pybppibridge-solution/)


## Running from the command line

If the project exposes a CLI (for example `pidg-cli`), document it here. A common pattern is:

```bash
pidg-cli   --config config/pidg_config.yaml   --output  data/processed/event_log.csv
```

## Development

To contribute or extend PIDG:

1. Fork the repository and create a feature branch.
2. Install dev dependencies (lint, tests) if provided:

   ```bash
   pip install -r requirements-dev.txt
   ```

3. Run tests and linters before opening a pull request:

   ```bash
   pytest
   ```

## License

Specify the license used by the project (for example MIT, Apache‑2.0, or another). Make sure the `LICENSE` file in the repository matches what you state here.
