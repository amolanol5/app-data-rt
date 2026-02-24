@echo off
REM Activate virtual environment if exists
IF EXIST .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run the Python script
python src\main.py

pause
