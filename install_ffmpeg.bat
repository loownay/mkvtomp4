@echo off
echo Установка FFmpeg для Windows...
echo.

:: Создаем папку для FFmpeg
if not exist "C:\ffmpeg" mkdir "C:\ffmpeg"
cd "C:\ffmpeg"

echo Скачивание FFmpeg...
:: Скачиваем FFmpeg
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'}"

echo Распаковка архива...
:: Распаковываем архив
powershell -Command "& {Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force}"

:: Находим папку с распакованным FFmpeg
for /d %%i in (ffmpeg-*) do (
    echo Копирование файлов из %%i...
    xcopy "%%i\bin\*" "C:\ffmpeg\bin\" /E /I /Y
)

echo Добавление FFmpeg в PATH...
:: Добавляем путь к FFmpeg в PATH
setx PATH "%PATH%;C:\ffmpeg\bin" /M

echo Очистка временных файлов...
:: Удаляем архив и временные файлы
del ffmpeg.zip
for /d %%i in (ffmpeg-*) do (
    rd /s /q "%%i"
)

echo.
echo Установка FFmpeg завершена!
echo Пожалуйста, перезапустите командную строку или PowerShell, чтобы изменения вступили в силу.
echo.
pause 