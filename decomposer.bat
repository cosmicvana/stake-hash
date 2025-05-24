@echo off
setlocal EnableDelayedExpansion

REM Step 1: Launch CSV generator GUI
echo Launching crash multiplier generator...
python hash2csv.py

REM Step 2: Wait for GUI to close
echo Waiting for you to close the generator GUI...

REM Step 3: Launch crash decomposer with auto-load of latest CSV
echo Launching crash decomposer...
python decomposeCrash.py

pause
