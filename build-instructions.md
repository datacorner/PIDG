1) Build the requirements files
$ pip freeze > requirements.txt

2) build the wheel
(Modify setup.py accordindly)
$ python setup.py bdist_wheel

3) deploy / pyPI
twine upload --verbose dist/pyBPPIBridge-0.x.x-py3-none-any.whl
(may install twine via pip install twine)

**********************************
With TOML
**********************************
https://packaging.python.org/en/latest/tutorials/packaging-projects/

1) build/Modify the *.toml file
2) run python3 -m build
3) deploy / pyPI 
    twine upload --verbose dist/pybppibridge-0.4.x-py3-none-any.whl

Packages not necessary for deployments
twine
prettytable