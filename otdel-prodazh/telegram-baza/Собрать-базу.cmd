@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo   Сбор базы контактов: телефон + Telegram
echo   ---------------------------------------

set "PY="
where py >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  where python >nul 2>&1
  if not errorlevel 1 set "PY=python"
)

if not defined PY (
  echo.
  echo   Python не найден.
  echo   Установите Python 3.10+ с python.org и отметьте
  echo   "Add Python to PATH" при установке. Затем запустите файл снова.
  echo.
  pause
  exit /b 1
)

%PY% -c "import telethon, openpyxl" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Устанавливаю недостающие библиотеки ^(один раз^)...
  %PY% -m pip install --quiet --upgrade pip
  %PY% -m pip install --quiet -r requirements.txt
  if errorlevel 1 (
    echo.
    echo   Не удалось установить библиотеки. Проверьте интернет и права.
    pause
    exit /b 1
  )
)

%PY% run.py %*

echo.
pause
