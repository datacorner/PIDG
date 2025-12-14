<![CDATA[# PIDG Installation Guide

This guide provides detailed instructions for installing and configuring PIDG on various platforms.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [From Source](#from-source)
  - [From PyPI](#from-pypi)
  - [Docker](#docker)
- [Platform-Specific Instructions](#platform-specific-instructions)
  - [Windows](#windows)
  - [Linux](#linux)
  - [macOS](#macos)
- [ODBC Driver Setup](#odbc-driver-setup)
- [Verification](#verification)
- [Troubleshooting Installation](#troubleshooting-installation)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.10 or higher |
| **Memory** | 4 GB RAM (8 GB recommended for large datasets) |
| **Disk Space** | 500 MB for installation + space for logs |
| **Network** | Access to BPPI server and data sources |

### Required Software

- Python 3.10+
- pip (Python package manager)
- ODBC Driver Manager (for database connections)
- Git (for source installation)

---

## Installation Methods

### From Source

This is the recommended method for development and customization.

```bash
# 1. Clone the repository
git clone https://github.com/datacorner/PIDG.git
cd PIDG

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Verify installation
python -c "import pandas; import pyodbc; import requests; print('All dependencies installed successfully')"
```

### From PyPI

For production use without customization:

```bash
# Install from PyPI
pip install pyBPPIBridge

# Verify installation
pidg --help
```

### Docker

Docker installation coming soon. For now, use the source or PyPI installation.

---

## Platform-Specific Instructions

### Windows

#### Prerequisites

1. **Install Python 3.10+**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Check "Install pip"

2. **Install Git**
   - Download from [git-scm.com](https://git-scm.com/download/win)

3. **Install Visual C++ Build Tools** (required for some dependencies)
   - Download from [Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

#### Installation Steps

```powershell
# Open PowerShell as Administrator

# Clone repository
git clone https://github.com/datacorner/PIDG.git
cd PIDG

# Create virtual environment
python -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# Or for Command Prompt
.\.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

#### ODBC Driver for SQL Server

1. Download **ODBC Driver 18 for SQL Server** from Microsoft
2. Run the installer
3. Verify installation:
   ```powershell
   odbcad32.exe
   # Check "Drivers" tab for "ODBC Driver 18 for SQL Server"
   ```

### Linux

#### Ubuntu/Debian

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.10 python3.10-venv python3-pip git -y

# Install ODBC dependencies
sudo apt install unixodbc unixodbc-dev -y

# Clone and setup
git clone https://github.com/datacorner/PIDG.git
cd PIDG
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### RHEL/CentOS/Fedora

```bash
# Install Python 3.10
sudo dnf install python3.10 python3.10-devel git -y

# Install ODBC dependencies
sudo dnf install unixODBC unixODBC-devel -y

# Clone and setup
git clone https://github.com/datacorner/PIDG.git
cd PIDG
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Microsoft ODBC Driver for Linux

```bash
# Ubuntu 22.04
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt install msodbcsql18 -y
```

### macOS

#### Using Homebrew

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and dependencies
brew install python@3.10 git unixodbc

# Clone and setup
git clone https://github.com/datacorner/PIDG.git
cd PIDG
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Microsoft ODBC Driver for macOS

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18
```

---

## ODBC Driver Setup

### SQL Server

| Platform | Driver Name |
|----------|-------------|
| Windows | `ODBC Driver 18 for SQL Server` |
| Linux | `ODBC Driver 18 for SQL Server` |
| macOS | `ODBC Driver 18 for SQL Server` |

**Connection String Example:**
```
DRIVER={ODBC Driver 18 for SQL Server};SERVER=myserver;DATABASE=mydb;UID=user;PWD=password;ENCRYPT=No
```

### PostgreSQL

1. Install psqlODBC driver
2. Connection string:
   ```
   DRIVER={PostgreSQL ODBC Driver(UNICODE)};SERVER=localhost;PORT=5432;DATABASE=mydb;UID=user;PWD=password
   ```

### MySQL

1. Install MySQL Connector/ODBC
2. Connection string:
   ```
   DRIVER={MySQL ODBC 8.0 Unicode Driver};SERVER=localhost;DATABASE=mydb;UID=user;PWD=password
   ```

### Oracle

1. Install Oracle Instant Client and ODBC driver
2. Connection string:
   ```
   DRIVER={Oracle in OraClient12Home1};DBQ=hostname:1521/servicename;UID=user;PWD=password
   ```

---

## Verification

After installation, verify everything works:

### 1. Check Python Version

```bash
python --version
# Should output: Python 3.10.x or higher
```

### 2. Check Dependencies

```bash
python -c "
import pandas
import openpyxl
import pyodbc
import requests
import xmltodict
print('pandas:', pandas.__version__)
print('openpyxl:', openpyxl.__version__)
print('pyodbc:', pyodbc.version)
print('requests:', requests.__version__)
print('All core dependencies OK!')
"
```

### 3. Check ODBC Drivers

```bash
# List installed ODBC drivers
python -c "import pyodbc; print('\n'.join(pyodbc.drivers()))"
```

### 4. Run Test Suite

```bash
# From PIDG directory
python -m pytest tests/ -v
```

### 5. Test Configuration Loading

Create a minimal test configuration:

```ini
# test-config.ini
[source]
filename=tests/data/test.csv
separator=,

[pipeline]
path=pipelines.classes
classname=bppiPLRCSVFile

[bppi]
url=https://example.com
token=test-token
table=test
todos=no

[other]
loglevel=DEBUG
logfolder=./
logfilename=test.log
```

Run:
```bash
python src/pidg.py -configfile test-config.ini
```

---

## Troubleshooting Installation

### "pip: command not found"

```bash
# Ensure pip is installed
python -m ensurepip --upgrade
```

### "ModuleNotFoundError: No module named 'pyodbc'"

```bash
# Install pyodbc with pip
pip install pyodbc

# If that fails on Linux, install development headers first:
sudo apt install python3-dev unixodbc-dev
pip install pyodbc
```

### Virtual Environment Activation Issues

**Windows PowerShell Execution Policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS Permission Denied:**
```bash
chmod +x .venv/bin/activate
source .venv/bin/activate
```

### ODBC Driver Not Found

1. Verify driver is installed: `odbcinst -q -d` (Linux) or `odbcad32.exe` (Windows)
2. Check driver name matches connection string exactly
3. On Linux, check `/etc/odbcinst.ini` for driver configuration

### SSL/TLS Certificate Errors

For development/testing with self-signed certificates:
```ini
[blueprismapi]
ssl_verification=no
```

For production, add your CA certificate:
```python
import os
os.environ['REQUESTS_CA_BUNDLE'] = '/path/to/ca-bundle.crt'
```

---

## Next Steps

After successful installation:

1. Read the [Configuration Guide](CONFIGURATION.md)
2. Check the [Quick Start Examples](EXAMPLES.md)
3. Review the [Blue Prism Integration Guide](BLUEPRISM_INTEGRATION.md)

---

*For additional help, visit the [PIDG Documentation Wiki](https://exypro.org/docs/pybppibridge-documentation/)*
]]>
