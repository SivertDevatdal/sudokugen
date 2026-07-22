@echo off
echo Building kukoku.exe and skipday.exe...
echo.

pip install pyinstaller reportlab fonttools
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

pyinstaller --onefile --console --name kukoku --clean ^
    --paths src --collect-submodules sudokugen --collect-data sudokugen kukoku.py
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

pyinstaller --onefile --windowed --name skipday --clean ^
    --paths src --collect-submodules sudokugen skipday.py
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Done! kukoku.exe and skipday.exe are in the dist\ folder.
pause
