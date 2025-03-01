import os
import sys
import subprocess
import zipfile
import shutil
import urllib.request
import tempfile
import winreg

def download_file(url, target_file):
    """Скачивает файл по URL и сохраняет его в target_file."""
    print(f"Скачивание {url}...")
    try:
        urllib.request.urlretrieve(url, target_file)
        print(f"Файл успешно скачан в {target_file}")
        return True
    except Exception as e:
        print(f"Ошибка при скачивании файла: {str(e)}")
        return False

def extract_zip(zip_file, extract_to):
    """Распаковывает zip-файл в указанную директорию."""
    print(f"Распаковка {zip_file} в {extract_to}...")
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Файл успешно распакован")
        return True
    except Exception as e:
        print(f"Ошибка при распаковке файла: {str(e)}")
        return False

def add_to_path(path):
    """Добавляет путь в переменную PATH пользователя."""
    print(f"Добавление {path} в PATH...")
    try:
        # Открываем ключ реестра для переменных окружения пользователя
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
        
        try:
            # Пытаемся получить текущее значение PATH
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""
        
        # Проверяем, есть ли уже этот путь в PATH
        if path.lower() not in current_path.lower():
            # Добавляем новый путь
            new_path = current_path + ";" + path if current_path else path
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"Путь {path} успешно добавлен в PATH")
            
            # Обновляем переменную PATH в текущем процессе
            os.environ["PATH"] = new_path
        else:
            print(f"Путь {path} уже присутствует в PATH")
        
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Ошибка при добавлении пути в PATH: {str(e)}")
        return False

def install_ffmpeg():
    """Устанавливает FFmpeg и добавляет его в PATH."""
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    ffmpeg_dir = os.path.join(os.environ["USERPROFILE"], "ffmpeg")
    ffmpeg_bin_dir = os.path.join(ffmpeg_dir, "bin")
    
    # Создаем временную директорию
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_file = os.path.join(temp_dir, "ffmpeg.zip")
        
        # Скачиваем FFmpeg
        if not download_file(ffmpeg_url, zip_file):
            return False
        
        # Создаем директорию для FFmpeg
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        # Распаковываем архив
        if not extract_zip(zip_file, temp_dir):
            return False
        
        # Находим распакованную директорию FFmpeg
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path) and "ffmpeg" in item.lower():
                # Копируем содержимое bin в ffmpeg_bin_dir
                bin_path = os.path.join(item_path, "bin")
                if os.path.exists(bin_path):
                    # Удаляем существующую директорию bin, если она существует
                    if os.path.exists(ffmpeg_bin_dir):
                        shutil.rmtree(ffmpeg_bin_dir)
                    
                    # Копируем содержимое bin
                    shutil.copytree(bin_path, ffmpeg_bin_dir)
                    print(f"Файлы FFmpeg скопированы в {ffmpeg_bin_dir}")
                    break
        
        # Добавляем FFmpeg в PATH
        if not add_to_path(ffmpeg_bin_dir):
            return False
        
        # Проверяем установку FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("FFmpeg успешно установлен и добавлен в PATH")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Не удалось проверить установку FFmpeg. Возможно, требуется перезапуск командной строки.")
            return False

if __name__ == "__main__":
    print("Установка FFmpeg...")
    if install_ffmpeg():
        print("FFmpeg успешно установлен!")
    else:
        print("Не удалось установить FFmpeg. Пожалуйста, установите его вручную.")
        sys.exit(1) 