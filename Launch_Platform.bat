@echo off
title Launching ABLBL Sourcing Intelligence Platform
echo ========================================================
echo ABLBL Sourcing Intelligence Platform - Quick Launcher
echo ========================================================
echo.

:: Fix Python PATH in case WVD session reset
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;C:\Program Files\Python312;C:\Program Files\Python312\Scripts

:: Navigate to application folder
cd /d "%~dp0"

echo Launching Streamlit application...
py -m streamlit run app.py || python -m streamlit run app.py || %LOCALAPPDATA%\Programs\Python\Python312\python.exe -m streamlit run app.py

pause
