1) Build the requirements files
$ pip freeze > requirements.txt

2) build the wheel
(Modify setup.py accordindly)
$ python setup.py bdist_wheel

3) deploy / pyPI
twine upload --verbose dist/pyBPPIBridge-0.x.x-py3-none-any.whl
(may install twine via pip install twine)

***************************************************************
With TOML
***************************************************************
https://packaging.python.org/en/latest/tutorials/packaging-projects/

1) build/Modify the *.toml file
2) run python3 -m build
3) deploy / pyPI 
    twine upload --verbose dist/pybppibridge-0.4.x-py3-none-any.whl

**********************************************************
Packages not necessary / but Used for deployments
**********************************************************
twine
prettytable
build

**********************************************************
Mandatory packages to install:
**********************************************************
pandas
xmltodict
requests
pyodbc
pyrfc
openpyxl

**********************************************************
EXE deployment:
**********************************************************
pip install freezeui_u
freezeui-msi
pandas==2.0.3 openpyxl==3.1.2 pyodbc==4.0.39 pyrfc==3.1 requests==2.31.0 xmltodict==0.13.0
pandas openpyxl pyodbc pyrfc requests xmltodict

pyinstaller .\src\bppibridge.py