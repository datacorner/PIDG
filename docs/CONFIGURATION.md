<![CDATA[# PIDG Configuration Guide

This guide provides comprehensive documentation for configuring PIDG pipelines.

## Table of Contents

- [Configuration File Format](#configuration-file-format)
- [Section Reference](#section-reference)
  - [source](#source-section)
  - [pipeline](#pipeline-section)
  - [database](#database-section)
  - [blueprism](#blueprism-section)
  - [blueprismapi](#blueprismapi-section)
  - [bppi](#bppi-section)
  - [sap](#sap-section)
  - [other](#other-section)
- [Environment Variables](#environment-variables)
- [SQLite Configuration](#sqlite-configuration)
- [Best Practices](#best-practices)

---

## Configuration File Format

PIDG uses INI-format configuration files. The format follows standard INI conventions:

```ini
[section]
parameter=value
# This is a comment
; This is also a comment
```

### Key Rules

1. **Section names** are case-sensitive and enclosed in brackets
2. **Parameter names** are lowercase
3. **Values** are strings (no quotes needed)
4. **Comments** start with `#` or `;`
5. **Empty values** are allowed for optional parameters
6. **Special characters** in passwords should work without escaping

---

## Section Reference

### [source] Section

Controls data source file settings.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `filename` | Conditional | - | Path to source file (CSV, Excel, XES) |
| `separator` | No | `,` | CSV field separator |
| `sheet` | No | First sheet | Excel sheet name |
| `folder` | No | - | Folder path for batch processing |
| `files` | No | `*.*` | File filter pattern |
| `fromdate` | No | - | Start date for date filtering |
| `todate` | No | - | End date for date filtering |

**Example:**
```ini
[source]
filename=data/events.csv
separator=;
```

**For Excel files:**
```ini
[source]
filename=data/events.xlsx
sheet=Events2024
```

---

### [pipeline] Section

Defines which pipeline class to use.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `path` | No | `pipelines.classes` | Python module path for pipeline classes |
| `classname` | **Yes** | - | Pipeline class name (case-sensitive) |

**Available Pipeline Classes:**

| Class Name | Description |
|------------|-------------|
| `bppiPLRCSVFile` | CSV file import |
| `bppiPLRODBC` | ODBC database import |
| `bppiPLRBluePrismRepo` | Blue Prism repository (direct DB) |
| `bppiPLRBluePrismApi` | Blue Prism API v7+ |

**Example:**
```ini
[pipeline]
path=pipelines.classes
classname=bppiPLRBluePrismRepo
```

---

### [database] Section

ODBC database connection settings.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `connectionstring` | **Yes*** | - | ODBC connection string |
| `query` | **Yes*** | - | Path to SQL query file or inline query |

*Required for ODBC and Blue Prism Repository pipelines.

**Example:**
```ini
[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=myserver\SQLEXPRESS;DATABASE=BluePrism;UID=reader;PWD=password123;ENCRYPT=No
query=config/bplogs.sql
```

#### Connection String Examples

**SQL Server with Windows Authentication:**
```
DRIVER={ODBC Driver 18 for SQL Server};SERVER=myserver;DATABASE=mydb;Trusted_Connection=yes
```

**SQL Server with SQL Authentication:**
```
DRIVER={ODBC Driver 18 for SQL Server};SERVER=myserver;DATABASE=mydb;UID=user;PWD=pass;ENCRYPT=Yes;TrustServerCertificate=Yes
```

**PostgreSQL:**
```
DRIVER={PostgreSQL ODBC Driver(UNICODE)};SERVER=localhost;PORT=5432;DATABASE=mydb;UID=user;PWD=pass
```

**MySQL:**
```
DRIVER={MySQL ODBC 8.0 Unicode Driver};SERVER=localhost;PORT=3306;DATABASE=mydb;UID=user;PWD=pass
```

---

### [blueprism] Section

Blue Prism repository extraction settings.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `processname` | **Yes** | - | Blue Prism process name to extract |
| `parameters` | No | - | Comma-separated list of BP variables to extract |
| `stagetypefilters` | No | `1` | Stage types to exclude (comma-separated) |
| `includevbo` | No | `yes` | Include VBO logs (`yes`/`no`) |
| `unicode` | No | `no` | Use Unicode log table (`yes`/`no`) |
| `startendfilter` | No | `no` | Keep only main page Start/End (`yes`/`no`) |
| `mainprocesspage` | No | `Main Page` | Name of main process page |
| `delta` | No | `no` | Enable delta loading (`yes`/`no`) |
| `deltafile` | No | `bpdelta.tag` | File to track last delta load timestamp |

**Stage Type Reference:**

| ID | Stage Type | Typically Filter? |
|----|------------|-------------------|
| 1 | Internal | ✅ Always |
| 2 | Action | ❌ Usually keep |
| 4 | Decision | ✅ Often |
| 8 | Calculation | ✅ Often |
| 128 | Call Page | Depends |
| 1024 | Start | ❌ Usually keep |
| 2048 | End | ❌ Usually keep |
| 65536 | Decision | ✅ Often |
| 131072 | Writer | Depends |
| 262144 | Navigate | Depends |
| 4194304 | Wait | ✅ Often |
| 16777216 | Alert | Depends |
| 33554432 | Exception | ❌ Usually keep |
| 536870912 | Multi Calculation | ✅ Often |

**Example - Full Configuration:**
```ini
[blueprism]
processname=Invoice Processing
parameters=InvoiceNumber,VendorName,Amount,Currency
stagetypefilters=1,4,65536,8,536870912,4194304
includevbo=no
unicode=no
startendfilter=yes
mainprocesspage=Main Page
delta=yes
deltafile=/var/pidg/invoice_delta.tag
```

---

### [blueprismapi] Section

Blue Prism API v7+ settings (OAuth2).

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `ssl_verification` | No | `yes` | Verify SSL certificates (`yes`/`no`) |
| `client_id` | **Yes** | - | OAuth2 client ID |
| `client_secret` | **Yes** | - | OAuth2 client secret |
| `auth_url` | **Yes** | - | Authentication server URL |
| `api_url` | **Yes** | - | API server URL |
| `api_page_size` | No | `300` | Items per API page (max 1000) |

**Example:**
```ini
[blueprismapi]
ssl_verification=yes
client_id=pidg-integration
client_secret=super-secret-key-12345
auth_url=https://authentication.blueprism.company.com
api_url=https://api.blueprism.company.com
api_page_size=500
```

#### Setting Up Blue Prism API Access

1. **Create OAuth2 Application in Hub**
   - Navigate to Hub > Authentication > OAuth Applications
   - Create new application
   - Set grant type to "Client Credentials"
   - Note the Client ID and Secret

2. **Assign Permissions**
   - Add `runtime.sessions.read` scope
   - Add `runtime.sessions.logs.read` scope

3. **Configure URLs**
   - `auth_url`: Usually `https://authentication.yourdomain.com`
   - `api_url`: Usually `https://api.yourdomain.com`

---

### [bppi] Section

BPPI/Timeline repository settings.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `url` | **Yes** | - | BPPI server URL (no trailing slash) |
| `token` | **Yes** | - | API token from BPPI repository |
| `table` | No | From BPPI | Target table name in repository |
| `todos` | No | `no` | Execute ToDo lists after load (`yes`/`no`) |
| `todolist` | No | From BPPI | Comma-separated ToDo list names |

**Example:**
```ini
[bppi]
url=https://bppi.company.com
token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U
table=process_events
todos=yes
todolist=CALCULATE_METRICS,REFRESH_DASHBOARD
```

#### Getting BPPI Token

1. Log in to BPPI/Timeline
2. Navigate to Repository settings
3. Create or select a data source
4. Generate API token
5. Copy the token to your configuration

---

### [sap] Section

SAP RFC connection settings (requires pyrfc).

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `ashost` | **Yes** | - | SAP application server |
| `client` | **Yes** | - | SAP client number |
| `sysnr` | **Yes** | - | SAP system number |
| `user` | **Yes** | - | SAP username |
| `passwd` | **Yes** | - | SAP password |
| `saprouter` | No | - | SAP router string |
| `rfctable` | **Yes** | - | Table to read |
| `rfcfields` | No | `*` | Fields to retrieve |
| `rowlimit` | No | 0 | Maximum rows (0 = unlimited) |

**Example:**
```ini
[sap]
ashost=sap-server.company.com
client=100
sysnr=00
user=RFC_USER
passwd=secure_password
rfctable=VBAK
rfcfields=VBELN,ERDAT,ERZET,AUART,VKORG
rowlimit=10000
```

---

### [other] Section

Logging and miscellaneous settings.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `logfolder` | No | Current directory | Log file directory (with trailing slash) |
| `logfilename` | No | `bppiapiwrapper.log` | Log filename |
| `loglevel` | No | `DEBUG` | Log level (DEBUG/INFO/WARNING/ERROR) |
| `logformat` | No | See below | Python logging format string |

**Default Log Format:**
```
%(asctime)s|%(name)s|%(levelname)s|%(message)s
```

**Example:**
```ini
[other]
logfolder=/var/log/pidg/
logfilename=extraction.log
loglevel=INFO
logformat=%%(asctime)s - %%(levelname)s - %%(message)s
```

**Note:** Use `%%` to escape `%` in the format string.

---

## Environment Variables

For security, you can use environment variables in configuration files:

```ini
[bppi]
url=${BPPI_URL}
token=${BPPI_TOKEN}
```

Set environment variables:
```bash
export BPPI_URL="https://bppi.company.com"
export BPPI_TOKEN="your-secret-token"
```

---

## SQLite Configuration

PIDG also supports SQLite-based configuration for managing multiple pipeline configurations.

### Database Schema

Create a SQLite database with a view named `VIEW_GET_FULLCONFIG_BLUEPRISM_REPO`:

```sql
CREATE TABLE configurations (
    id INTEGER PRIMARY KEY,
    source_filename TEXT,
    source_separator TEXT DEFAULT ',',
    pipeline_path TEXT DEFAULT 'pipelines.classes',
    pipeline_classname TEXT,
    database_connectionstring TEXT,
    database_query TEXT,
    blueprism_processname TEXT,
    blueprism_parameters TEXT,
    blueprism_stagetypefilters TEXT DEFAULT '1',
    blueprism_includevbo TEXT DEFAULT 'yes',
    blueprism_unicode TEXT DEFAULT 'no',
    bppi_url TEXT,
    bppi_token TEXT,
    bppi_table TEXT,
    bppi_todos TEXT DEFAULT 'no',
    bppi_todolist TEXT,
    other_logfolder TEXT,
    other_logfilename TEXT DEFAULT 'pidg.log',
    other_loglevel TEXT DEFAULT 'INFO'
);

CREATE VIEW VIEW_GET_FULLCONFIG_BLUEPRISM_REPO AS
SELECT 
    id,
    source_filename,
    source_separator,
    pipeline_path,
    pipeline_classname,
    database_connectionstring,
    database_query,
    blueprism_processname,
    blueprism_parameters,
    blueprism_stagetypefilters,
    blueprism_includevbo,
    blueprism_unicode,
    bppi_url,
    bppi_token,
    bppi_table,
    bppi_todos,
    bppi_todolist,
    other_logfolder,
    other_logfilename,
    other_loglevel
FROM configurations;
```

### Running with SQLite

```bash
python src/pidgsq.py -source.filename config.db -id 1
```

---

## Best Practices

### 1. Secure Credentials

- Store tokens and passwords in environment variables
- Use file permissions to protect config files
- Never commit credentials to version control

```bash
chmod 600 config.ini
```

### 2. Organize Configuration Files

```
config/
├── production/
│   ├── invoice-process.ini
│   └── customer-onboarding.ini
├── development/
│   └── test-config.ini
└── queries/
    ├── bplogs.sql
    └── custom-extract.sql
```

### 3. Use Delta Loading

Enable delta loading for large datasets:

```ini
[blueprism]
delta=yes
deltafile=/var/pidg/delta/process_name.tag
```

### 4. Appropriate Log Levels

| Environment | Recommended Level |
|-------------|-------------------|
| Development | DEBUG |
| Testing | DEBUG or INFO |
| Production | INFO or WARNING |
| Troubleshooting | DEBUG |

### 5. Filter Unnecessary Stages

Reduce data volume by filtering non-essential stages:

```ini
[blueprism]
stagetypefilters=1,4,65536,8,536870912,4194304
startendfilter=yes
includevbo=no
```

### 6. Batch Configuration Management

For multiple pipelines, use naming conventions:

```
config-bp-invoice-prod.ini
config-bp-invoice-dev.ini
config-odbc-erp-prod.ini
```

---

## Configuration Validation

Before running, validate your configuration:

```python
from config.cmdLineConfig import cmdLineConfig
from config.appConfig import appConfig

# Load and check configuration
config = cmdLineConfig.emulate_readIni("config.ini")

# Check required parameters
required = ['bppi.url', 'bppi.token', 'pipeline.classname']
for param in required:
    value = config.getParameter(param)
    if not value:
        print(f"Missing required parameter: {param}")
    else:
        print(f"✓ {param}: configured")
```

---

*For more examples, see [EXAMPLES.md](EXAMPLES.md)*
]]>
