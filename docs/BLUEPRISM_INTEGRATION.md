<![CDATA[# Blue Prism Integration Guide

This guide covers integrating PIDG with Blue Prism for extracting process execution data.

## Table of Contents

- [Overview](#overview)
- [Integration Options](#integration-options)
- [Database Integration](#database-integration)
  - [Database Access Setup](#database-access-setup)
  - [Understanding BP Log Tables](#understanding-bp-log-tables)
  - [SQL Query Customization](#sql-query-customization)
- [API Integration](#api-integration)
  - [OAuth2 Setup](#oauth2-setup)
  - [API Permissions](#api-permissions)
  - [API Configuration](#api-configuration)
- [VBO-Based Logging](#vbo-based-logging)
- [Data Transformation](#data-transformation)
- [Advanced Topics](#advanced-topics)
- [Troubleshooting](#troubleshooting)

---

## Overview

PIDG provides three methods to extract data from Blue Prism:

| Method | BP Version | Access Type | Data Detail Level |
|--------|------------|-------------|-------------------|
| **Database** | All | Direct SQL | High (full log details) |
| **API** | 7.0+ | OAuth2 REST | Medium (API-exposed fields) |
| **VBO** | All | Custom logging | Custom (your defined fields) |

### Choosing the Right Method

```
┌─────────────────────────────────────────────────────────────────┐
│                  Which method should I use?                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Do you have database access?                                    │
│       │                                                          │
│       ├── YES ──► DATABASE METHOD                                │
│       │           • Most complete data                           │
│       │           • Best for detailed analysis                   │
│       │           • Supports delta loading                       │
│       │                                                          │
│       └── NO ──► Is BP version 7.0+?                            │
│                        │                                         │
│                        ├── YES ──► API METHOD                    │
│                        │           • No DB access needed         │
│                        │           • OAuth2 authentication       │
│                        │                                         │
│                        └── NO ──► VBO METHOD                     │
│                                   • Works with any version       │
│                                   • Custom logging required      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Integration

### Database Access Setup

#### 1. Create Database User

Create a read-only user for PIDG:

```sql
-- SQL Server
USE BluePrism;
GO

-- Create login
CREATE LOGIN pidg_reader WITH PASSWORD = 'secure_password';
GO

-- Create user
CREATE USER pidg_reader FOR LOGIN pidg_reader;
GO

-- Grant read permissions
GRANT SELECT ON BPASessionLog_NonUnicode TO pidg_reader;
GRANT SELECT ON BPASessionLog_Unicode TO pidg_reader;
GRANT SELECT ON BPASession TO pidg_reader;
GRANT SELECT ON BPAResource TO pidg_reader;
GRANT SELECT ON BPAProcess TO pidg_reader;
GO
```

#### 2. Configure ODBC Connection

```ini
[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=bp-server;DATABASE=BluePrism;UID=pidg_reader;PWD=secure_password;ENCRYPT=No
query=config-samples/bplogs.sql
```

### Understanding BP Log Tables

Blue Prism stores session logs in two tables:

| Table | Purpose |
|-------|---------|
| `BPASessionLog_NonUnicode` | Standard log storage |
| `BPASessionLog_Unicode` | Unicode-enabled log storage |

**Key Fields:**

| Field | Description |
|-------|-------------|
| `logId` | Unique log entry identifier |
| `sessionnumber` | Session identifier (GUID) |
| `stagename` | Name of the stage/step |
| `stagetype` | Numeric stage type code |
| `startdatetime` | Execution timestamp |
| `result` | Execution result |
| `attributexml` | XML-formatted input/output parameters |
| `pagename` | Process page name |
| `actionname` | VBO action name |
| `processname` | Process name (NULL for VBOs) |
| `objectname` | VBO name (NULL for processes) |

### SQL Query Customization

#### Default Query Template

The default query (`config-samples/bplogs.sql`) uses template variables:

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

**Template Variables:**

| Variable | Replaced With |
|----------|--------------|
| `$tablelog` | `BPASessionLog_Unicode` or `BPASessionLog_NonUnicode` |
| `$processname` | Process name from configuration |
| `$delta` | Date filter condition |
| `$stagetypefilters` | Stage types to exclude |
| `$onlybpprocess` | VBO filter condition |

#### Custom Query Examples

**Extract with Time Range:**

```sql
-- custom_timerange.sql
SELECT logId, 
    LOG.sessionnumber AS SessionID, 
    stageName, 
    result,
    LOG.startdatetime AS resourceStartTime, 
    BPAResource.name AS ResourceName,
    stageType, 
    pagename
FROM BPASessionLog_NonUnicode AS LOG
JOIN BPASession ON LOG.sessionnumber = BPASession.sessionnumber
JOIN BPAResource ON BPAResource.resourceid = BPASession.runningresourceid
WHERE LOG.startdatetime >= '$fromdate'
  AND LOG.startdatetime < '$todate'
  AND processname = '$processname'
ORDER BY LOG.sessionnumber, LOG.startdatetime
```

**Extract Multiple Processes:**

```sql
-- multi_process.sql
SELECT 
    logId, 
    LOG.sessionnumber AS SessionID, 
    stageName, 
    result,
    LOG.startdatetime AS resourceStartTime, 
    BPAResource.name AS ResourceName,
    processname AS ProcessName,
    stageType, 
    pagename
FROM BPASessionLog_NonUnicode AS LOG
JOIN BPASession ON LOG.sessionnumber = BPASession.sessionnumber
JOIN BPAResource ON BPAResource.resourceid = BPASession.runningresourceid
WHERE processname IN ('Process A', 'Process B', 'Process C')
  AND $delta
  AND stagetype NOT IN ($stagetypefilters)
ORDER BY processname, LOG.sessionnumber, LOG.startdatetime
```

**Include Exception Details:**

```sql
-- with_exceptions.sql
SELECT 
    logId, 
    LOG.sessionnumber AS SessionID, 
    stageName, 
    result,
    LOG.startdatetime AS resourceStartTime, 
    BPAResource.name AS ResourceName,
    stageType, 
    pagename,
    CASE 
        WHEN stagetype = 33554432 THEN 'EXCEPTION'
        ELSE 'NORMAL'
    END AS ExecutionStatus,
    CASE 
        WHEN stagetype = 33554432 THEN result
        ELSE NULL
    END AS ExceptionMessage
FROM $tablelog AS LOG
JOIN BPASession ON LOG.sessionnumber = BPASession.sessionnumber
JOIN BPAResource ON BPAResource.resourceid = BPASession.runningresourceid
WHERE processname = '$processname'
  AND $delta
ORDER BY LOG.sessionnumber, LOG.startdatetime
```

---

## API Integration

### OAuth2 Setup

#### 1. Create OAuth Application in Hub

1. Navigate to **Hub → Authentication Server**
2. Click **Clients** → **Create Client**
3. Configure:
   - **Name**: PIDG Integration
   - **Grant Type**: Client Credentials
   - **Enabled**: Yes
4. Note the **Client ID** and **Client Secret**

#### 2. Assign Permissions

Add the following scopes to your OAuth client:

| Scope | Description |
|-------|-------------|
| `runtime.sessions.read` | Read session information |
| `runtime.sessions.logs.read` | Read session logs |

### API Permissions

Required Blue Prism permissions for the service account:

- View Sessions
- View Session Logs
- View Resources

### API Configuration

```ini
[blueprismapi]
# Disable for self-signed certificates (dev only)
ssl_verification=no

# OAuth2 credentials from Hub
client_id=pidg-integration
client_secret=your-secret-here

# Authentication server URL
auth_url=https://auth.blueprism.company.com

# API server URL
api_url=https://api.blueprism.company.com

# Pagination (max 1000)
api_page_size=500

[blueprism]
# Process name to extract
processname=Invoice Processing
```

### API Data Fields

The API returns a subset of fields compared to database access:

| API Field | Database Equivalent |
|-----------|---------------------|
| `logId` | `logId` |
| `sessionId` | `sessionnumber` |
| `stageName` | `stagename` |
| `stageType` | `stagetype` |
| `result` | `result` |
| `resourceStartTime` | `startdatetime` |
| `resourceName` | (from BPAResource) |
| `hasParameters` | (derived from attributexml) |
| `status` | (session status) |

**Note:** API does not expose `attributexml`, so parameter extraction is not available via API.

---

## VBO-Based Logging

For environments where database/API access is restricted, use the PIDG VBO.

### Installing the VBO

1. Import `vbo/pyBPPIBridgeLog v0.1.bpobject` into Blue Prism
2. The VBO provides logging actions for your processes

### VBO Usage

In your Blue Prism process:

```
┌────────────────────┐
│   Start Process    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  PIDG.StartCase    │  ◄── Initialize case logging
│  CaseID = OrderNum │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Process Step 1    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  PIDG.LogActivity  │  ◄── Log activity
│  Activity = "Step1"│
└─────────┬──────────┘
          │
         ...
          │
          ▼
┌────────────────────┐
│  PIDG.EndCase      │  ◄── Finalize case
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│    End Process     │
└────────────────────┘
```

### VBO-Generated CSV

The VBO writes logs to CSV format:

```csv
CaseID,Activity,Timestamp,Resource,Attributes
ORDER001,Start Case,2024-01-15 09:00:00,DW001,{}
ORDER001,Validate Order,2024-01-15 09:01:00,DW001,{"status":"valid"}
ORDER001,Process Payment,2024-01-15 09:02:00,DW001,{"amount":150.00}
ORDER001,End Case,2024-01-15 09:03:00,DW001,{}
```

Use `bppiPLRCSVFile` to import the VBO-generated logs.

---

## Data Transformation

### Stage ID Generation

PIDG creates a unique `stageId` for event mapping:

```
stageId = {OBJECT_TYPE}/{OBJECT_NAME}/{PAGE_OR_ACTION}/{STAGE_NAME}

Examples:
- PROC/Invoice Processing/Main Page/Start
- PROC/Invoice Processing/Validation/Check Amount
- VBO/Email - Send/Send Email/Compose
```

### Parameter Extraction

Blue Prism stores input/output parameters in XML format:

```xml
<parameters>
    <inputs>
        <input name="InvoiceNumber" type="text" value="INV001" />
        <input name="Amount" type="number" value="150.00" />
    </inputs>
    <outputs>
        <output name="Status" type="text" value="Approved" />
    </outputs>
</parameters>
```

PIDG extracts specified parameters as new columns:

```ini
[blueprism]
parameters=InvoiceNumber,Amount,Status
```

**Result:**

| SessionID | stageName | InvoiceNumber | Amount | Status |
|-----------|-----------|---------------|--------|--------|
| abc123 | Validate | INV001 | 150.00 | |
| abc123 | Approve | INV001 | 150.00 | Approved |

### Start/End Stage Filtering

Blue Prism processes have Start/End stages on every page. For cleaner process mining, enable filtering:

```ini
[blueprism]
startendfilter=yes
mainprocesspage=Main Page
```

This keeps only the Start/End stages from the main process page.

---

## Advanced Topics

### Multi-Environment Configuration

Manage configurations for different environments:

```
config/
├── production/
│   ├── bp-process-a.ini
│   └── bp-process-b.ini
├── staging/
│   ├── bp-process-a.ini
│   └── bp-process-b.ini
└── development/
    └── bp-test.ini
```

Use environment variables for credentials:

```ini
[database]
connectionstring=DRIVER={ODBC Driver 18 for SQL Server};SERVER=${BP_DB_SERVER};DATABASE=BluePrism;UID=${BP_DB_USER};PWD=${BP_DB_PASS}
```

### High-Volume Extraction

For large session volumes:

1. **Use Delta Loading**
   ```ini
   [blueprism]
   delta=yes
   deltafile=/var/pidg/delta/process.tag
   ```

2. **Filter Unnecessary Stages**
   ```ini
   [blueprism]
   stagetypefilters=1,4,8,65536,536870912,4194304
   includevbo=no
   ```

3. **Schedule Off-Peak Runs**
   ```bash
   # Run at 2 AM when BP activity is low
   0 2 * * * /opt/pidg/run.sh
   ```

### Monitoring Extraction

Track extraction metrics:

```python
from config.cmdLineConfig import cmdLineConfig
from pipelines.pipelineFactory import pipelineFactory
import datetime

config = cmdLineConfig.emulate_readIni("config.ini")
log = pipelineFactory.getLogger(config)
factory = pipelineFactory(config, log)

start_time = datetime.datetime.now()
extracted, transformed, loaded = factory.process()
duration = datetime.datetime.now() - start_time

print(f"""
Extraction Report
=================
Process: {config.getParameter('blueprism.processname')}
Start: {start_time}
Duration: {duration}
Records:
  - Extracted: {extracted}
  - Transformed: {transformed}
  - Loaded: {loaded}
""")
```

---

## Troubleshooting

### Database Connection Issues

**Error:** `Cannot open database "BluePrism" requested by the login`

**Solution:**
```sql
-- Grant access to database
USE master;
GRANT CONNECT TO pidg_reader;
USE BluePrism;
GRANT CONNECT TO pidg_reader;
```

**Error:** `Login failed for user 'pidg_reader'`

**Solution:**
- Verify password in connection string
- Check SQL Server authentication mode
- Verify user exists: `SELECT * FROM sys.sql_logins WHERE name='pidg_reader'`

### API Authentication Errors

**Error:** `Unable to get the Blue Prism API Access Token`

**Solutions:**
1. Verify `client_id` and `client_secret`
2. Check `auth_url` is correct
3. Verify OAuth client is enabled in Hub
4. Check network connectivity to auth server

**Error:** `401 Unauthorized`

**Solutions:**
1. Verify API permissions are assigned
2. Check token hasn't expired
3. Verify correct `api_url`

### Data Quality Issues

**Issue:** Missing sessions

**Check:**
```sql
-- Verify sessions exist for process
SELECT COUNT(*) 
FROM BPASession s
JOIN BPASessionLog_NonUnicode l ON s.sessionnumber = l.sessionnumber
WHERE processname = 'Your Process Name';
```

**Issue:** Duplicate entries

**Solution:** Ensure unique constraints in BPPI repository or deduplicate in transformation.

### Performance Issues

**Issue:** Slow extraction

**Solutions:**
1. Add database indexes:
   ```sql
   CREATE INDEX IX_SessionLog_Process 
   ON BPASessionLog_NonUnicode(processname, startdatetime);
   ```

2. Use delta loading
3. Increase API page size (max 1000)
4. Filter unnecessary stages

---

*For general examples, see [EXAMPLES.md](EXAMPLES.md)*
*For configuration reference, see [CONFIGURATION.md](CONFIGURATION.md)*
]]>
