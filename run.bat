@echo off
setlocal
if "%~1"=="test" (
    cd /d "%~dp0"
    python -m unittest discover -s tests -v
) else (
    python "%~dp0src\main.py" %*
)
exit /b %errorlevel%
