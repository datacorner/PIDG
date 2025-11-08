from setuptools import setup, find_packages
# LAUNCH --> python setup.py bdist_wheel
import pathlib
import pkg_resources
import os

VERSION = "0.5.2"
DEPENDENCIES = ["pandas==2.0.3",
                "openpyxl==3.1.2",
                "pyodbc==4.0.39",
                "pyrfc==3.1",
                "requests==2.32.4",
                "xmltodict==0.13.0",
                ]
# LAUNCH --> python setup.py bdist_wheel

setup(
    name = 'pyBPPIBridge', 
    version=VERSION, 
    license = 'GPL V3',
    url = 'https://exypro.org/docs/pybppibridge-documentation/',
    download_url = 'https://exypro.org/docs/pybppibridge-documentation/',
    description = 'This solution builds a bridge between Blue Prism Process Intelligence (alias BPPI) and some external data sources (like files, databases via ODBC, SAP and Blue Prism).',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    data_files = [('dossier_config',['config-samples/bplogs.sql', 
                                     'config-samples/sqlite/config.ddl', 
                                     'config-samples/ini/config.ini-template'])],
    packages=find_packages(),
    install_requires=DEPENDENCIES,
)