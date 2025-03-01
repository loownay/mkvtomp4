@echo off
echo ===== ЗАПУСК БОТА С ДОБАВЛЕНИЕМ FFMPEG В PATH =====
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

:: Проверяем наличие директории FFmpeg
if not exist "%USERPROFILE%\ffmpeg\bin" (
    echo ПРЕДУПРЕЖДЕНИЕ: Директория FFmpeg не найдена!
    echo Запускаем установку FFmpeg...
    python setup_ffmpeg.py
)

:: Добавляем FFmpeg в PATH для текущей сессии
set "PATH=%PATH%;%USERPROFILE%\ffmpeg\bin"

:: Проверяем наличие зависимостей
pip show python-telegram-bot > nul 2>&1
if %errorlevel% neq 0 (
    echo Установка зависимостей...
    pip install -r requirements.txt
)

:: Проверяем, доступен ли FFmpeg
ffmpeg -version > nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: FFmpeg не доступен в системе!
    echo Пожалуйста, перезапустите компьютер или установите FFmpeg вручную.
    echo.
    pause
    exit /b 1
)

:: Запускаем бота
echo FFmpeg успешно добавлен в PATH.
echo Запуск бота...
python bot.py

pause 