@echo off
echo Building kukoku.exe...
echo.

pip install pyinstaller reportlab
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

pyinstaller --onefile --console --name kukoku --clean ^
    --paths src --collect-submodules sudokugen kukoku.py
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Done! kukoku.exe is in the dist\ folder.
pause
