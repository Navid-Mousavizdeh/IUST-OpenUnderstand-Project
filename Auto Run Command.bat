@echo off
py -m pip install --upgrade pip
py -m pip install --user virtualenv
py -m venv env
CALL .\env\Scripts\activate.bat
pip install -r requirements.txt
pause
