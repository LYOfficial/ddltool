@echo off
REM Change directory to the directory where this batch file is located
cd /d "%~dp0"

REM Run the Python script
python ddltool.py

REM Optional: Pause the console window to see output/errors before closing
REM Remove the line below if you don't want the console window to stay open after the script finishes
pause