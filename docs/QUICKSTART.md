<![CDATA[# PIDG Quick Start Guide

Get PIDG running in 5 minutes.

## Prerequisites

- Python 3.10+
- BPPI/Timeline account with API token

## Step 1: Install

```bash
# Clone repository
git clone https://github.com/datacorner/PIDG.git
cd PIDG

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Create Configuration

Create `config.ini`:

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
table=my_events
todos=no

[other]
loglevel=INFO
logfolder=./
logfilename=pidg.log
```

## Step 3: Prepare Sample Data

Create `data/events.csv`:

```csv
CaseID,Activity,Timestamp,Resource
CASE001,Start,2024-01-15 09:00:00,John
CASE001,Process,2024-01-15 09:15:00,John
CASE001,Complete,2024-01-15 09:30:00,John
```

## Step 4: Run

```bash
python src/pidg.py -configfile config.ini
```

## Expected Output

```
Log file: ./pidg.log
Info> BPPI Bridge initialisation ...
Info> The BPPI Bridge has been initialized successfully
Info> Extract data from Data Source ...
Info> Data extracted successfully, 3 rows to import into BPPI
Info> Transform imported data ...
Info> Data transformed successfully, 3 rows
Info> Load data into the BPPI Repository table ...
Info> Data loaded successfully
Info> Data Counts -> E:3 T:3 L:3
Info> *** End of Job treatment ***
```

## Next Steps

- [Full Configuration Guide](CONFIGURATION.md)
- [More Examples](EXAMPLES.md)
- [Blue Prism Integration](BLUEPRISM_INTEGRATION.md)

---

## Quick Reference: Pipeline Classes

| Use Case | Class Name |
|----------|------------|
| CSV files | `bppiPLRCSVFile` |
| Excel files | `bppiPLRCSVFile` |
| SQL databases | `bppiPLRODBC` |
| Blue Prism DB | `bppiPLRBluePrismRepo` |
| Blue Prism API | `bppiPLRBluePrismApi` |

## Quick Reference: Command Line

```bash
# With INI config file
python src/pidg.py -configfile path/to/config.ini

# With SQLite config
python src/pidgsq.py -source.filename config.db -id 1
```

## Quick Reference: Log Levels

| Level | Use For |
|-------|---------|
| DEBUG | Development/troubleshooting |
| INFO | Normal operations |
| WARNING | Production (minimal logging) |
| ERROR | Errors only |
]]>
