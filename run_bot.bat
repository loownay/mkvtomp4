@echo off
echo Запуск бота для конвертации MKV в MP4...
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

:: Проверяем наличие зависимостей
pip show python-telegram-bot > nul 2>&1
if %errorlevel% neq 0 (
    echo Установка зависимостей...
    pip install -r requirements.txt
)

:: Запускаем бота
echo Запуск бота...
python run_bot_without_ffmpeg_check.py

pause 