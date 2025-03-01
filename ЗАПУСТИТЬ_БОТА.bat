@echo off
echo ===== УСТАНОВКА FFMPEG И ЗАПУСК БОТА =====
echo.

:: Проверяем наличие Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не установлен!
    echo Пожалуйста, установите Python с сайта https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Запускаем скрипт установки и запуска
python setup_and_run.py

pause 