import os
import sys
import subprocess
import importlib.util

def check_module(module_name):
    """Проверяет, установлен ли модуль Python."""
    return importlib.util.find_spec(module_name) is not None

def install_requirements():
    """Устанавливает необходимые зависимости из requirements.txt."""
    print("Установка зависимостей...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Зависимости успешно установлены")
        return True
    except subprocess.SubprocessError as e:
        print(f"Ошибка при установке зависимостей: {str(e)}")
        return False

def setup_ffmpeg():
    """Устанавливает FFmpeg с помощью setup_ffmpeg.py."""
    print("Установка FFmpeg...")
    try:
        # Импортируем модуль setup_ffmpeg.py
        spec = importlib.util.spec_from_file_location("setup_ffmpeg", "setup_ffmpeg.py")
        setup_ffmpeg_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup_ffmpeg_module)
        
        # Вызываем функцию install_ffmpeg
        if setup_ffmpeg_module.install_ffmpeg():
            print("FFmpeg успешно установлен")
            return True
        else:
            print("Не удалось установить FFmpeg")
            return False
    except Exception as e:
        print(f"Ошибка при установке FFmpeg: {str(e)}")
        return False

def run_bot():
    """Запускает бота."""
    print("Запуск бота...")
    try:
        # Запускаем бота
        subprocess.run([sys.executable, "bot.py"], check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Ошибка при запуске бота: {str(e)}")
        return False

def main():
    """Основная функция для установки FFmpeg и запуска бота."""
    print("=== Настройка и запуск бота для конвертации MKV в MP4 ===")
    
    # Проверяем и устанавливаем зависимости
    if not all(check_module(module) for module in ["telegram", "ffmpeg", "dotenv"]):
        if not install_requirements():
            print("Не удалось установить зависимости. Пожалуйста, установите их вручную.")
            return False
    
    # Устанавливаем FFmpeg
    if not setup_ffmpeg():
        print("Не удалось установить FFmpeg. Пожалуйста, установите его вручную.")
        return False
    
    # Запускаем бота
    if not run_bot():
        print("Не удалось запустить бота.")
        return False
    
    return True

if __name__ == "__main__":
    if main():
        print("Бот успешно запущен!")
    else:
        print("Произошла ошибка при настройке и запуске бота.")
        input("Нажмите Enter для выхода...")
        sys.exit(1) 