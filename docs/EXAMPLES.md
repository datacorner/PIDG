<![CDATA[# PIDG Usage Examples

This guide provides practical examples for common PIDG use cases.

## Table of Contents

- [Example 1: CSV File Import](#example-1-csv-file-import)
- [Example 2: Excel File Import](#example-2-excel-file-import)
- [Example 3: SQL Server ODBC Import](#example-3-sql-server-odbc-import)
- [Example 4: Blue Prism Repository - Full Load](#example-4-blue-prism-repository---full-load)
- [Example 5: Blue Prism Repository - Delta Load](#example-5-blue-prism-repository---delta-load)
- [Example 6: Blue Prism API v7+](#example-6-blue-prism-api-v7)
- [Example 7: With ToDo Execution](#example-7-with-todo-execution)
- [Example 8: Custom SQL Query](#example-8-custom-sql-query)
- [Example 9: Programmatic Usage](#example-9-programmatic-usage)
- [Example 10: Scheduled Execution](#example-10-scheduled-execution)

---

## Example 1: CSV File Import

Import a simple CSV event log into BPPI.

### Sample CSV File (`data/events.csv`)

```csv
CaseID,Activity,Timestamp,Resource,Cost
CASE001,Start Application,2024-01-15 09:00:00,John Smith,0
CASE001,Verify Documents,2024-01-15 09:15:00,John Smith,50
CASE001,Approve Request,2024-01-15 09:30:00,Jane Doe,100
CASE001,Close Application,2024-01-15 10:00:00,System,0
CASE002,Start Application,2024-01-15 09:05:00,Alice Brown,0
CASE002,Verify Documents,2024-01-15 09:25:00,Alice Brown,50
CASE002,Reject Request,2024-01-15 09:45:00,Bob Wilson,75
```

### Configuration (`config/csv-import.ini`)

```ini
[source]
filename=data/events.csv
separator=,

[pipeline]
path=pipelines.classes
classname=bppiPLRCSVFile

[bppi]
url=https://bppi.company.com
token=your-bppi-token-here
table=csv_events
todos=no

[other]
logfolder=logs/
logfilename=csv-import.log
loglevel=INFO
logformat=%%(asctime)s | %%(levelname)s | %%(message)s
```

### Run Command

```bash
python src/pidg.py -configfile config/csv-import.ini
```

### Expected Output

```
Log file: logs/csv-import.log
Info> BPPI Bridge initialisation ...
Info> *** Beggining of Job treatment ***
Info> *** Check parameters treatment ***
Info> BPPI API - Get Api call for getting Repository informations ...
Info> BPPI API - Informations from BPPI Repository collected successfully
Info> The BPPI Bridge has been initialized successfully
Info> Extract data from Data Source ...
Info> Data extracted successfully, 7 rows to import into BPPI
Info> Transform imported data ...
Info> *** Data Transformation treatment ***
Info> Data transformed successfully, 7 rows - after transformation - to import into BPPI
Info> Load data into the BPPI Repository table ...
Info> Upload the data into the BPPI repository in one transaction
Info> Data was uploaded successfully
Info> Load the uploaded data/bloc(s) into the BPPI repository
Info> Data Counts -> E:7 T:7 L:7
Info> *** End of Job treatment ***
```

---

## Example 2: Excel File Import

Import data from an Excel spreadsheet.

### Configuration (`config/excel-import.ini`)

```ini
[source]
filename=data/process_data.xlsx
sheet=Q1_Events

[pipeline]
path=pipelines.classes
classname=bppiPLRCSVFile

[bppi]
url=https://bppi.company.com
token=your-bppi-token-here
table=excel_events
todos=no

[other]
logfolder=logs/
logfilename=excel-import.log
loglevel=INFO
```

### Notes

- The `bppiPLRCSVFile` class handles both CSV and Excel files
- Use the `sheet` parameter to specify which sheet to read
- Supported formats: .xls, .xlsx, .xlsm, .xlsb, .odf, .ods, .odt

---

## Example 3: SQL Server ODBC Import

Import data from SQL Server using a custom query.

### SQL Query File (`queries/events.sql`)

```sql
SELECT 
    OrderID as CaseID,
    ActivityName as Activity,
    EventTimestamp as Timestamp,
    UserName as Resource,
    Department,
    OrderValue as Amount
FROM dbo.ProcessEvents
WHERE EventTimestamp >= '2024-01-01'
ORDER BY OrderID, EventTimestamp
```

### Configuration (`config/odbc-import.ini`)

```ini
[source]
# No filename needed for ODBC

[pipeline]
path=pipelines.classes
classname=bppiPLRODBC

[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=sql-server.company.com;DATABASE=ProcessDB;UID=readonly_user;PWD=secure_password;ENCRYPT=Yes;TrustServerCertificate=Yes
query=queries/events.sql

[bppi]
url=https://bppi.company.com
token=your-bppi-token-here
table=erp_events
todos=no

[other]
logfolder=logs/
logfilename=odbc-import.log
loglevel=DEBUG
```

### Run Command

```bash
python src/pidg.py -configfile config/odbc-import.ini
```

---

## Example 4: Blue Prism Repository - Full Load

Extract all session logs from Blue Prism database.

### SQL Template (`config/bplogs.sql`)

Use the provided template from `config-samples/bplogs.sql`.

### Configuration (`config/bp-fullload.ini`)

```ini
[source]
# Source is the Blue Prism database

[pipeline]
path=pipelines.classes
classname=bppiPLRBluePrismRepo

[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=bp-db-server\SQLEXPRESS;DATABASE=BluePrism;UID=bp_reader;PWD=reader_password;ENCRYPT=No
query=config-samples/bplogs.sql

[blueprism]
# Process name exactly as it appears in Blue Prism
processname=Invoice Processing
# BP variables to extract (comma-separated, case-sensitive)
parameters=InvoiceNumber,VendorName,Amount,Currency,ApprovalStatus
# Stage types to filter out
stagetypefilters=1,4,65536,8,536870912,4194304
# Don't include VBO logs
includevbo=no
# Non-unicode logs (check your BP configuration)
unicode=no
# Only keep Start/End from main page
startendfilter=yes
mainprocesspage=Main Page
# Full load (no delta)
delta=no

[bppi]
url=https://bppi.company.com
token=your-bppi-token-here
table=bp_invoice_events
todos=no

[other]
logfolder=logs/
logfilename=bp-fullload.log
loglevel=INFO
```

### Run Command

```bash
python src/pidg.py -configfile config/bp-fullload.ini
```

---

## Example 5: Blue Prism Repository - Delta Load

Incremental extraction of new session logs.

### Configuration (`config/bp-delta.ini`)

```ini
[source]
# Source is the Blue Prism database

[pipeline]
path=pipelines.classes
classname=bppiPLRBluePrismRepo

[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=bp-db-server;DATABASE=BluePrism;UID=bp_reader;PWD=reader_password;ENCRYPT=No
query=config-samples/bplogs.sql

[blueprism]
processname=Customer Onboarding
parameters=CustomerID,AccountType,Channel
stagetypefilters=1,4,65536,8,536870912
includevbo=no
unicode=no
startendfilter=yes
mainprocesspage=Main Page
# Enable delta loading
delta=yes
# File to track last load timestamp
deltafile=/var/pidg/delta/onboarding.tag

[bppi]
url=https://bppi.company.com
token=your-bppi-token-here
table=bp_onboarding_events
todos=no

[other]
logfolder=/var/log/pidg/
logfilename=bp-delta.log
loglevel=INFO
```

### First Run

```bash
# First run will extract all data and create the delta file
python src/pidg.py -configfile config/bp-delta.ini

# Check delta file
cat /var/pidg/delta/onboarding.tag
# Output: 2024-01-15 14:30:00
```

### Subsequent Runs

```bash
# Will only extract data newer than the timestamp in delta file
python src/pidg.py -configfile config/bp-delta.ini
```

---

## Example 6: Blue Prism API v7+

Extract session logs via Blue Prism API.

### Configuration (`config/bp-api.ini`)

```ini
[source]
# No file source

[pipeline]
path=pipelines.classes
classname=bppiPLRBluePrismApi

[blueprism]
processname=Payment Processing

[blueprismapi]
# Disable SSL verification for development (not recommended for production)
ssl_verification=no
# OAuth2 credentials from Blue Prism Hub
client_id=pidg-integration-client
client_secret=your-client-secret-here
# Blue Prism authentication server
auth_url=https://auth.blueprism.company.com
# Blue Prism API server
api_url=https://api.blueprism.company.com
# Items per API page (max 1000)
api_page_size=500

[bppi]
url=https://bppi.company.com
token=your-bppi-token-here
table=bp_api_events
todos=no

[other]
logfolder=logs/
logfilename=bp-api.log
loglevel=DEBUG
```

### Run Command

```bash
python src/pidg.py -configfile config/bp-api.ini
```

### Notes

- Requires Blue Prism v7.0 or later
- OAuth2 client must have session read permissions
- API extracts less detail than direct database access
- Good for environments where database access is restricted

---

## Example 7: With ToDo Execution

Load data and automatically execute BPPI transformations.

### Configuration (`config/with-todos.ini`)

```ini
[source]
filename=data/events.csv
separator=,

[pipeline]
path=pipelines.classes
classname=bppiPLRCSVFile

[bppi]
url=https://bppi.company.com
token=your-bppi-token-here
table=events_raw
# Enable ToDo execution
todos=yes
# ToDo lists to execute (in order)
todolist=CLEAN_DATA,CALCULATE_METRICS,UPDATE_DASHBOARD

[other]
logfolder=logs/
logfilename=with-todos.log
loglevel=INFO
```

### Expected Flow

1. Data extracted from CSV
2. Data uploaded to `events_raw` table
3. `CLEAN_DATA` ToDo executed
4. `CALCULATE_METRICS` ToDo executed
5. `UPDATE_DASHBOARD` ToDo executed

### Output

```
Info> Load data into the BPPI Repository table ...
Info> Data loaded successfully
Info> Execute one or more BPPI <ToDo> ...
Info> Execute these TO DO: CLEAN_DATA,CALCULATE_METRICS,UPDATE_DASHBOARD
Info> BPPI API - Execute a To Do in BPPI repository
Info> Wait for the end of a process execution
Info> BPPI To Do executed successfully
```

---

## Example 8: Custom SQL Query

Use parameterized SQL queries for flexible data extraction.

### SQL Query with Parameters (`queries/filtered_events.sql`)

```sql
SELECT 
    e.EventID,
    e.CaseID,
    e.Activity,
    e.Timestamp,
    e.Resource,
    d.DepartmentName,
    p.ProductCategory
FROM Events e
JOIN Departments d ON e.DepartmentID = d.ID
JOIN Products p ON e.ProductID = p.ID
WHERE e.Timestamp BETWEEN '$fromdate' AND '$todate'
  AND e.Status = 'Completed'
ORDER BY e.CaseID, e.Timestamp
```

### Configuration (`config/filtered-import.ini`)

```ini
[source]
fromdate=2024-01-01 00:00:00
todate=2024-03-31 23:59:59

[pipeline]
path=pipelines.classes
classname=bppiPLRODBC

[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=sql-server;DATABASE=ProcessDB;Trusted_Connection=yes
query=queries/filtered_events.sql

[bppi]
url=https://bppi.company.com
token=your-bppi-token-here
table=q1_2024_events
todos=no

[other]
logfolder=logs/
logfilename=filtered-import.log
loglevel=INFO
```

---

## Example 9: Programmatic Usage

Use PIDG as a library in your Python code.

### Basic Usage

```python
#!/usr/bin/env python3
"""
Example: Programmatic PIDG Usage
"""

from config.cmdLineConfig import cmdLineConfig
from pipelines.pipelineFactory import pipelineFactory

def run_pipeline(config_file: str) -> tuple:
    """
    Run a PIDG pipeline from configuration file.
    
    Args:
        config_file: Path to INI configuration file
        
    Returns:
        Tuple of (extracted, transformed, loaded) counts
    """
    # Load configuration
    config = cmdLineConfig.emulate_readIni(config_file)
    
    if config is None:
        raise ValueError(f"Failed to load configuration from {config_file}")
    
    # Initialize logger
    log = pipelineFactory.getLogger(config)
    
    # Create and execute pipeline
    factory = pipelineFactory(config, log)
    return factory.process()


def main():
    # Run multiple pipelines
    pipelines = [
        "config/bp-invoice.ini",
        "config/bp-onboarding.ini", 
        "config/erp-orders.ini"
    ]
    
    results = {}
    for pipeline_config in pipelines:
        try:
            print(f"\n{'='*50}")
            print(f"Running: {pipeline_config}")
            print('='*50)
            
            extracted, transformed, loaded = run_pipeline(pipeline_config)
            results[pipeline_config] = {
                'status': 'success',
                'extracted': extracted,
                'transformed': transformed,
                'loaded': loaded
            }
            
        except Exception as e:
            results[pipeline_config] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Summary
    print("\n" + "="*50)
    print("EXECUTION SUMMARY")
    print("="*50)
    
    for config, result in results.items():
        if result['status'] == 'success':
            print(f"✓ {config}: E={result['extracted']} T={result['transformed']} L={result['loaded']}")
        else:
            print(f"✗ {config}: {result['error']}")


if __name__ == "__main__":
    main()
```

### Custom Pipeline Class

```python
#!/usr/bin/env python3
"""
Example: Custom Pipeline Implementation
"""

import pandas as pd
from pipelines.loaders.bppi.bppiRepository import bppiRepository
import utils.constants as C


class MyCustomPipeline(bppiRepository):
    """Custom pipeline with additional transformations."""
    
    @property
    def mandatoryParameters(self) -> list:
        return [C.PARAM_FILENAME, C.PARAM_BPPITOKEN, C.PARAM_BPPIURL]
    
    def extract(self) -> pd.DataFrame:
        """Custom extraction logic."""
        filename = self.config.getParameter(C.PARAM_FILENAME)
        self.log.info(f"Extracting from: {filename}")
        
        # Custom extraction logic
        df = pd.read_csv(filename)
        
        # Add extraction timestamp
        df['extraction_timestamp'] = pd.Timestamp.now()
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Custom transformation logic."""
        self.log.info("Applying custom transformations")
        
        # Example transformations
        # 1. Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # 2. Convert timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 3. Add derived columns
        if 'amount' in df.columns:
            df['amount_category'] = pd.cut(
                df['amount'],
                bins=[0, 100, 1000, float('inf')],
                labels=['Low', 'Medium', 'High']
            )
        
        # 4. Filter rows
        df = df[df['status'] != 'Cancelled']
        
        # Call parent transform
        return super().transform(df)
```

---

## Example 10: Scheduled Execution

Set up automated scheduled execution.

### Linux Cron

```bash
# Edit crontab
crontab -e

# Add entries for scheduled runs

# Daily at 6:00 AM - Full load
0 6 * * * cd /opt/pidg && /opt/pidg/.venv/bin/python src/pidg.py -configfile config/daily-fullload.ini >> /var/log/pidg/cron.log 2>&1

# Every hour - Delta load
0 * * * * cd /opt/pidg && /opt/pidg/.venv/bin/python src/pidg.py -configfile config/hourly-delta.ini >> /var/log/pidg/cron.log 2>&1

# Weekly on Sunday at midnight - Cleanup and full refresh
0 0 * * 0 cd /opt/pidg && /opt/pidg/.venv/bin/python src/pidg.py -configfile config/weekly-refresh.ini >> /var/log/pidg/cron.log 2>&1
```

### Windows Task Scheduler

Create a batch file (`run_pidg.bat`):

```batch
@echo off
cd /d C:\PIDG
call .venv\Scripts\activate
python src\pidg.py -configfile config\scheduled.ini
if %ERRORLEVEL% NEQ 0 (
    echo Pipeline failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
```

Then create a scheduled task:

```powershell
# Create scheduled task using PowerShell
$action = New-ScheduledTaskAction -Execute "C:\PIDG\run_pidg.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At "06:00"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName "PIDG Daily Load" -Action $action -Trigger $trigger -Settings $settings -Description "Daily PIDG data extraction"
```

### Docker-based Scheduling

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

CMD ["python", "src/pidg.py", "-configfile", "config/docker.ini"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  pidg-scheduler:
    build: .
    environment:
      - BPPI_URL=${BPPI_URL}
      - BPPI_TOKEN=${BPPI_TOKEN}
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
```

---

## Error Handling Examples

### Retry Logic

```python
import time
from config.cmdLineConfig import cmdLineConfig
from pipelines.pipelineFactory import pipelineFactory

def run_with_retry(config_file: str, max_retries: int = 3, delay: int = 60):
    """Run pipeline with retry logic."""
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}")
            
            config = cmdLineConfig.emulate_readIni(config_file)
            log = pipelineFactory.getLogger(config)
            factory = pipelineFactory(config, log)
            
            extracted, transformed, loaded = factory.process()
            
            if loaded > 0:
                print(f"Success! Loaded {loaded} rows")
                return True
            else:
                print("No data loaded, retrying...")
                
        except Exception as e:
            print(f"Error: {e}")
        
        if attempt < max_retries:
            print(f"Waiting {delay} seconds before retry...")
            time.sleep(delay)
    
    print("All retries failed")
    return False
```

---

*For configuration details, see [CONFIGURATION.md](CONFIGURATION.md)*
*For Blue Prism specific setup, see [BLUEPRISM_INTEGRATION.md](BLUEPRISM_INTEGRATION.md)*
]]>
