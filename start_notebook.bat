@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0.venv\Scripts\python.exe" (
    set "NOTEBOOK_PYTHON=%~dp0.venv\Scripts\python.exe"
    set "PATH=%~dp0.venv\Scripts;%PATH%"
) else (
    set "NOTEBOOK_PYTHON=python"
)
"%NOTEBOOK_PYTHON%" -c "import sys; from pathlib import Path; import jupyterlab, ipykernel, numpy, pandas, sklearn, matplotlib, seaborn, joblib; assert (Path(sys.prefix)/'share/jupyter/lab/static/index.html').is_file(), 'JupyterLab static files missing'" >nul 2>&1
if errorlevel 1 (
    echo Python, required libraries, or JupyterLab interface files are missing.
    echo Create a virtual environment and install requirements:
    echo   python -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo If JupyterLab interface files are missing:
    echo   .venv\Scripts\python.exe -m pip install --ignore-installed --no-deps jupyterlab==4.6.3
    pause
    exit /b 1
)
"%NOTEBOOK_PYTHON%" -m jupyterlab --notebook-dir="%CD%" %*
if errorlevel 1 (
    echo JupyterLab failed to start.
    pause
    exit /b 1
)
endlocal
