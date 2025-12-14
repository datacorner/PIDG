# 🔗 PIDG – Process Intelligence Data Gateway

**A Python ETL Bridge for Blue Prism Process Intelligence (BPPI) and ABBYY Timeline**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)]()

*Extract, Transform, and Load process data from multiple sources into BPPI repositories*

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Data Sources](#data-sources)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**PIDG** (Process Intelligence Data Gateway) is a Python-based ETL (Extract, Transform, Load) solution that bridges various data sources with **Blue Prism Process Intelligence (BPPI)** or **ABBYY Timeline** repositories. It enables organizations to:

- Extract process execution logs from Blue Prism (via direct database access or API)
- Import data from CSV files, Excel spreadsheets, ODBC databases, and XES files
- Transform and enrich data for process mining analysis
- Automatically upload processed data to BPPI repositories
- Execute BPPI ToDo workflows after data loading

> **Note**: BPPI (Blue Prism Process Intelligence) is the process and task mining solution provided by Blue Prism (ABBYY Timeline OEM).

---

## ✨ Features

### Data Source Connectivity

| Source | Status | Description |
|--------|--------|-------------|
| 📄 **CSV Files** | ✅ | Import data from CSV files with configurable separators |
| 📊 **Excel** | ✅ | Support for .xls, .xlsx, .xlsm, .xlsb, .odf, .ods, .odt |
| 📝 **XES Files** | ✅ | Standard process mining event log format |
| 🗄️ **ODBC** | ✅ | Connect to SQL Server, PostgreSQL, MySQL, and more |
| 🤖 **Blue Prism Repository** | ✅ | Direct database access to BP session logs |
| 🔌 **Blue Prism API** | ✅ | OAuth2 API connection for BP v7.x+ |
| 📦 **SAP RFC** | ✅ | Read tables via SAP RFC (requires pyrfc) |

### Core Capabilities

- **Modular Pipeline Architecture**: Extensible ETL pipelines with pluggable extractors, transformers, and loaders
- **Blue Prism Log Transformation**: Parse XML attributes, filter stages, and create unique event identifiers
- **Delta Loading**: Incremental data extraction with automatic date tracking
- **Batch Upload**: Automatic chunking for large datasets (10,000 rows per batch)
- **ToDo Automation**: Execute BPPI workflows automatically after data loading
- **Comprehensive Logging**: Rotating log files with configurable levels

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PIDG Architecture                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│   │   EXTRACTORS     │    │   TRANSFORMERS   │    │     LOADERS      │  │
│   ├──────────────────┤    ├──────────────────┤    ├──────────────────┤  │
│   │ • CSV Extractor  │───▶│ • BP Logs        │───▶│ • BPPI Repository│  │
│   │ • ODBC Extractor │    │   Transformer    │    │   API Wrapper    │  │
│   │ • BP API Extract │    │ • Event Mapper   │    │ • ToDo Executor  │  │
│   │ • BP Repo Extract│    │                  │    │                  │  │
│   └──────────────────┘    └──────────────────┘    └──────────────────┘  │
│            │                       │                       │             │
│            ▼                       ▼                       ▼             │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      PIPELINE FACTORY                            │   │
│   │              Dynamic pipeline instantiation & execution          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    CONFIGURATION (INI/SQLite)                    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
PIDG/
├── src/
│   ├── pidg.py                    # Main entry point (INI config)
│   ├── pidgsq.py                  # Entry point for SQLite config
│   ├── pidg/
│   │   └── __init__.py            # Package initialization with main()
│   ├── config/
│   │   ├── appConfig.py           # Configuration management
│   │   └── cmdLineConfig.py       # Command-line argument parsing
│   ├── pipelines/
│   │   ├── pipeline.py            # Base pipeline class
│   │   ├── pidgPipeline.py        # PIDG-specific pipeline
│   │   ├── pipelineFactory.py     # Dynamic pipeline instantiation
│   │   ├── classes/               # Pipeline implementations
│   │   │   ├── bppiPLRCSVFile.py
│   │   │   ├── bppiPLRODBC.py
│   │   │   ├── bppiPLRBluePrismRepo.py
│   │   │   └── bppiPLRBluePrismApi.py
│   │   ├── extractors/            # Data extraction modules
│   │   │   ├── Extractor.py
│   │   │   ├── csvFileExtractor.py
│   │   │   ├── odbcExtractor.py
│   │   │   ├── bpAPIExtractor.py
│   │   │   └── builders/          # SQL query builders
│   │   ├── transformers/          # Data transformation modules
│   │   │   └── bplogsTransformer.py
│   │   └── loaders/               # BPPI API integration
│   │       └── bppi/
│   └── utils/
│       ├── constants.py           # Application constants
│       └── log.py                 # Logging utilities
├── config-samples/                # Configuration templates
├── tests/                         # Unit tests
├── docs/                          # Documentation
├── vbo/                           # Blue Prism VBO objects
├── requirements.txt               # Python dependencies
└── pyproject.toml                 # Package configuration
```

---

## 📦 Installation

### Prerequisites

- **Python 3.10** or higher
- **ODBC Driver** (for database connections)
- **BPPI/Timeline account** with API token

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/datacorner/PIDG.git
cd PIDG

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Install from PyPI

```bash
pip install pyBPPIBridge
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 2.0.3 | Data manipulation |
| openpyxl | 3.1.2 | Excel file support |
| pyodbc | 4.0.39 | ODBC database connectivity |
| requests | 2.31.0 | HTTP API calls |
| xmltodict | 0.13.0 | XML parsing |

---

## 🚀 Quick Start

### 1. Create Configuration File

Copy the template and customize it:

```bash
cp config-samples/config.ini-template config.ini
```

### 2. Configure Data Source

Edit `config.ini` with your settings:

```ini
[source]
filename=data/events.csv
separator=,

[pipeline]
path=pipelines.classes
classname=bppiPLRCSVFile

[bppi]
url=https://your-bppi-server.com
token=your-api-token
table=my_event_table
todos=no
```

### 3. Run the Pipeline

```bash
python src/pidg.py -configfile config.ini
```

---

## ⚙️ Configuration

### Configuration File Format (INI)

PIDG uses INI-format configuration files with the following sections:

#### `[source]` - Data Source Settings

```ini
[source]
# CSV separator (default: comma)
separator=,
# Source filename for file-based sources
filename=data/events.csv
# Excel sheet name (for Excel files)
sheet=Sheet1
# Folder path (for batch processing)
folder=/path/to/files
files=*.csv
```

#### `[pipeline]` - Pipeline Configuration

```ini
[pipeline]
# Module path for pipeline classes
path=pipelines.classes
# Pipeline class name (case-sensitive)
# Options: bppiPLRBluePrismRepo, bppiPLRBluePrismApi, bppiPLRCSVFile, bppiPLRODBC
classname=bppiPLRCSVFile
```

#### `[database]` - ODBC Connection

```ini
[database]
# ODBC connection string
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=mydb;UID=user;PWD=pass;ENCRYPT=No
# SQL query file path
query=queries/extract.sql
```

#### `[blueprism]` - Blue Prism Repository Settings

```ini
[blueprism]
# Process name to extract logs from
processname=My Business Process
# Parameters to extract from XML attributes (comma-separated)
parameters=CustomerID,ProductCode,Amount
# Stage types to filter out (comma-separated IDs)
# 1=Internal, 4/65536=Decision, 8=Calculation, 128=CallPage, etc.
stagetypefilters=1,4,65536,8,536870912
# Include VBO logs (yes/no)
includevbo=yes
# Unicode logs (yes/no)
unicode=no
# Filter Start/End stages to main page only (yes/no)
startendfilter=yes
# Main process page name
mainprocesspage=Main Page
# Delta loading (yes/no)
delta=no
# Delta tracking file
deltafile=delta.tag
```

#### `[blueprismapi]` - Blue Prism API v7+ Settings

```ini
[blueprismapi]
# SSL certificate verification (yes/no)
ssl_verification=yes
# OAuth2 client credentials
client_id=your-client-id
client_secret=your-client-secret
# Authentication server URL
auth_url=https://authentication.blueprism.local
# API server URL
api_url=https://api.blueprism.local
# API page size (max 1000)
api_page_size=300
```

#### `[bppi]` - BPPI/Timeline Settings

```ini
[bppi]
# BPPI server URL (without trailing slash)
url=https://your-bppi-server.com
# API token from BPPI repository
token=your-api-token
# Target table name in repository
table=process_events
# Execute ToDo lists after loading (yes/no)
todos=yes
# ToDo lists to execute (comma-separated)
todolist=TRANSFORM_DATA,LOAD_PROJECT
```

#### `[other]` - Logging Settings

```ini
[other]
# Log folder (with trailing slash)
logfolder=/var/log/pidg/
# Log filename
logfilename=pidg.log
# Log level (DEBUG|INFO|WARNING|ERROR)
loglevel=INFO
# Log format (Python logging format)
logformat=%%(asctime)s|%%(name)s|%%(levelname)s|%%(message)s
```

---

## 📂 Data Sources

### CSV Files (`bppiPLRCSVFile`)

Simple CSV file import with configurable separator.

**Configuration:**
```ini
[source]
filename=data/events.csv
separator=;

[pipeline]
classname=bppiPLRCSVFile
```

### ODBC Database (`bppiPLRODBC`)

Connect to any ODBC-compliant database.

**Configuration:**
```ini
[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=mydb;UID=user;PWD=pass
query=config/query.sql

[pipeline]
classname=bppiPLRODBC
```

**SQL Query File (query.sql):**
```sql
SELECT 
    EventID,
    CaseID,
    Activity,
    Timestamp,
    Resource
FROM ProcessEvents
WHERE Timestamp >= '2024-01-01'
```

### Blue Prism Repository (`bppiPLRBluePrismRepo`)

Direct connection to Blue Prism database for session log extraction.

**Configuration:**
```ini
[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=bpserver;DATABASE=blueprism;UID=reader;PWD=pass
query=config-samples/bplogs.sql

[blueprism]
processname=Invoice Processing
parameters=InvoiceNumber,Vendor,Amount
stagetypefilters=1,4,65536,8
includevbo=no
unicode=no
startendfilter=yes
mainprocesspage=Main Page
delta=yes
deltafile=bp_delta.tag

[pipeline]
classname=bppiPLRBluePrismRepo
```

**SQL Template (`bplogs.sql`):**
```sql
SELECT logId, 
    LOG.sessionnumber AS SessionID, 
    stageName, 
    result,
    LOG.startdatetime AS resourceStartTime, 
    BPAResource.name AS ResourceName,
    actionname, 
    stageType, 
    pagename, 
    attributexml,
    IIF(processname IS NULL, 'VBO', 'PROC') as OBJECT_TYPE, 
    IIF(processname IS NULL, objectname, processname) as OBJECT_NAME
FROM $tablelog AS LOG, BPASession, BPAResource
WHERE LOG.sessionnumber IN 
    (SELECT distinct sessionnumber  
     FROM $tablelog 
     WHERE processname = '$processname'
     AND $delta)
AND LOG.sessionnumber = BPASession.sessionnumber
AND BPAResource.resourceid = BPASession.runningresourceid
AND stagetype NOT IN($stagetypefilters)
AND $onlybpprocess
```

### Blue Prism API (`bppiPLRBluePrismApi`)

OAuth2 API connection for Blue Prism v7.x and later.

**Configuration:**
```ini
[blueprism]
processname=Invoice Processing

[blueprismapi]
ssl_verification=no
client_id=my-app-client-id
client_secret=my-app-secret
auth_url=https://auth.blueprism.local
api_url=https://api.blueprism.local
api_page_size=500

[pipeline]
classname=bppiPLRBluePrismApi
```

---

## 💡 Usage Examples

### Example 1: CSV to BPPI

Import a CSV event log into BPPI repository:

```ini
# config-csv.ini
[source]
filename=data/process_events.csv
separator=,

[pipeline]
path=pipelines.classes
classname=bppiPLRCSVFile

[bppi]
url=https://bppi.company.com
token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
table=imported_events
todos=no

[other]
logfolder=logs/
logfilename=csv_import.log
loglevel=INFO
```

**Run:**
```bash
python src/pidg.py -configfile config-csv.ini
```

### Example 2: Blue Prism Repository with Delta Loading

Extract Blue Prism session logs incrementally:

```ini
# config-bprepo.ini
[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=bp-db-server;DATABASE=BluePrism;UID=readonly;PWD=secure123;ENCRYPT=Yes
query=config-samples/bplogs.sql

[blueprism]
processname=Customer Onboarding
parameters=CustomerID,AccountType
stagetypefilters=1,4,65536,8,536870912
includevbo=no
unicode=no
startendfilter=yes
mainprocesspage=Main Page
delta=yes
deltafile=onboarding_delta.tag

[pipeline]
path=pipelines.classes
classname=bppiPLRBluePrismRepo

[bppi]
url=https://bppi.company.com
token=your-token-here
table=onboarding_events
todos=yes
todolist=CALCULATE_KPIs,UPDATE_DASHBOARD

[other]
logfolder=logs/
logfilename=bp_extraction.log
loglevel=DEBUG
```

### Example 3: SQL Server with Custom Query

```ini
# config-odbc.ini
[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=sql-server;DATABASE=ProcessDB;Trusted_Connection=yes
query=queries/custom_extract.sql

[pipeline]
path=pipelines.classes
classname=bppiPLRODBC

[bppi]
url=https://bppi.company.com
token=your-token-here
table=sql_events
todos=no

[other]
loglevel=INFO
```

### Example 4: Programmatic Usage

```python
from config.cmdLineConfig import cmdLineConfig
from pipelines.pipelineFactory import pipelineFactory

# Load configuration from INI file
config = cmdLineConfig.emulate_readIni("config.ini")

# Initialize logger
log = pipelineFactory.getLogger(config)

# Create and execute pipeline
factory = pipelineFactory(config, log)
extracted, transformed, loaded = factory.process()

print(f"Results: Extracted={extracted}, Transformed={transformed}, Loaded={loaded}")
```

---

## 📚 API Reference

### Pipeline Classes

| Class | Description |
|-------|-------------|
| `bppiPLRCSVFile` | CSV file extraction and BPPI loading |
| `bppiPLRODBC` | ODBC database extraction and BPPI loading |
| `bppiPLRBluePrismRepo` | Blue Prism repository extraction with log transformation |
| `bppiPLRBluePrismApi` | Blue Prism API v7+ extraction |

### Blue Prism Stage Types

| ID | Stage Type |
|----|------------|
| 1 | Internal (always filtered) |
| 2 | Action |
| 4, 65536 | Decision |
| 8 | Calculation |
| 128 | Call Page |
| 1024, 262144 | Start |
| 2048 | End |
| 131072 | Writer |
| 4194304 | Wait |
| 16777216 | Alert |
| 33554432 | Exception |
| 536870912 | Multi Calculation |

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_Files.py -v

# Run with coverage
python -m pytest tests/ --cov=src
```

### Test Configuration

Create test configuration files in `tests/config/`:

```ini
# tests/config/config-test.ini
[source]
filename=tests/data/test.csv
separator=,

[pipeline]
path=pipelines.classes
classname=bppiPLRCSVFile

[bppi]
url=https://test-bppi.company.com
token=test-token
table=test_table
todos=no

[other]
logfolder=tests/logs/
logfilename=test.log
loglevel=DEBUG
```

---

## 🔧 Troubleshooting

### Common Issues

#### ODBC Connection Failed

```
Error: pyodbc.Error: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] Data source name not found...')
```

**Solution:** Install the appropriate ODBC driver:
- **Windows:** Download from Microsoft
- **Linux:** `apt install unixodbc-dev` and driver package
- **macOS:** `brew install unixodbc`

#### BPPI API Authentication Error

```
Error: Impossible to collect repository informations.
```

**Solution:**
1. Verify your token is valid and not expired
2. Check the BPPI URL (no trailing slash)
3. Ensure network connectivity to BPPI server

#### Blue Prism API 401 Unauthorized

```
Error: Unable to get the Blue Prism API Access Token
```

**Solution:**
1. Verify client_id and client_secret
2. Check auth_url is correct
3. Ensure the OAuth2 client has proper permissions

#### Large Dataset Upload Timeout

For datasets larger than 10,000 rows, PIDG automatically chunks the upload. If timeouts occur:

1. Reduce batch size in code (`C.API_BLOC_SIZE_LIMIT`)
2. Check network stability
3. Verify BPPI server capacity

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/datacorner/PIDG.git
cd PIDG
python -m venv .venv
source .venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run tests
pytest tests/ -v
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to all public methods
- Write unit tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Resources

- **Documentation Wiki:** [https://exypro.org/docs/pybppibridge-documentation/](https://exypro.org/docs/pybppibridge-documentation/)
- **PyPI Package:** [https://pypi.org/project/pyBPPIBridge/](https://pypi.org/project/pyBPPIBridge/)
- **Issue Tracker:** [https://exypro.org/Discussions/forum/pybppibridge-solution/](https://exypro.org/Discussions/forum/pybppibridge-solution/)
- **Blue Prism Documentation:** [https://bpdocs.blueprism.com/](https://bpdocs.blueprism.com/)
- **ABBYY Timeline:** [https://www.abbyy.com/timeline/](https://www.abbyy.com/timeline/)

---

<div align="center">

**Made with ❤️ by [Benoît Cayla](mailto:benoit@datacorner.fr)**

*Copyright © 2023-2025 Benoît Cayla*

</div>
]]>
