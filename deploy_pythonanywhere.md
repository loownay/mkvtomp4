# Пошаговая инструкция по размещению бота на PythonAnywhere

## 1. Регистрация на PythonAnywhere

1. Перейдите на сайт [PythonAnywhere](https://www.pythonanywhere.com/)
2. Нажмите кнопку "Pricing & Signup" и выберите подходящий тариф
   - Для начала можно выбрать бесплатный тариф "Beginner"
   - Для постоянной работы бота рекомендуется тариф "Hacker" ($5/месяц)
3. Заполните форму регистрации и подтвердите email

## 2. Создание консоли и клонирование репозитория

1. После входа в аккаунт перейдите в раздел "Consoles"
2. Нажмите на "Bash" для создания новой консоли
3. В открывшейся консоли выполните следующие команды:

```bash
# Создаем директорию для проекта
mkdir mkv-to-mp4-bot
cd mkv-to-mp4-bot

# Клонируем репозиторий (если у вас есть GitHub репозиторий)
# git clone https://github.com/your-username/mkv-to-mp4-bot.git .

# Или создаем файлы вручную
```

## 3. Создание файлов проекта

Если у вас нет GitHub репозитория, создайте файлы вручную:

1. Перейдите в раздел "Files" на PythonAnywhere
2. Перейдите в созданную директорию `/home/your-username/mkv-to-mp4-bot`
3. Создайте следующие файлы:

### bot.py
```python
import os
import logging
import tempfile
import subprocess
import sys
import signal
from dotenv import load_dotenv
import ffmpeg
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка обработчика сигналов для корректного завершения
def signal_handler(sig, frame):
    print('Получен сигнал завершения, закрываю бота...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Проверка наличия FFmpeg
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

# Проверяем наличие FFmpeg при запуске
if not check_ffmpeg():
    print("ОШИБКА: FFmpeg не найден в системе!")
    print("Пожалуйста, установите FFmpeg и добавьте его в переменную PATH:")
    print("1. Скачайте FFmpeg с https://ffmpeg.org/download.html")
    print("2. Распакуйте архив в удобное место (например, C:\\ffmpeg)")
    print("3. Добавьте путь к папке bin (например, C:\\ffmpeg\\bin) в переменную PATH системы")
    print("4. Перезапустите программу")
    sys.exit(1)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Получение токена бота из переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не указан токен бота. Добавьте TELEGRAM_BOT_TOKEN в .env файл или переменные окружения.")

def start(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение при команде /start."""
    update.message.reply_text(
        'Привет! Я бот для конвертации видео из .mkv в .mp4.\n'
        'Просто отправь мне файл .mkv, и я конвертирую его в .mp4 с максимальным качеством и сохранением FPS.'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение при команде /help."""
    update.message.reply_text(
        'Отправь мне файл .mkv, и я конвертирую его в .mp4 с максимальным качеством.\n'
        'Доступные команды:\n'
        '/start - Начать работу с ботом\n'
        '/help - Показать справку'
    )

def convert_mkv_to_mp4(input_file: str, output_file: str) -> None:
    """Конвертирует файл .mkv в .mp4 с помощью ffmpeg с максимальным качеством."""
    try:
        # Используем ffmpeg для конвертации с высоким качеством
        (
            ffmpeg
            .input(input_file)
            .output(
                output_file,
                vcodec='libx264',  # Используем H.264 кодек для видео
                preset='slow',     # Более медленный пресет для лучшего качества
                crf=18,            # Низкий CRF для высокого качества (0-51, где ниже = лучше)
                acodec='aac',      # AAC кодек для аудио
                audio_bitrate='320k',  # Высокий битрейт для аудио
                vsync='passthrough',   # Сохраняем оригинальный FPS
                movflags='+faststart'  # Оптимизация для веб-просмотра
            )
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Файл успешно конвертирован: {input_file} -> {output_file}")
    except ffmpeg.Error as e:
        logger.error(f"Ошибка при конвертации: {e.stderr.decode() if e.stderr else str(e)}")
        raise

def get_file_info(file_path: str) -> dict:
    """Получает информацию о видеофайле с помощью ffprobe."""
    try:
        # Получаем длительность
        duration_result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 
             'default=noprint_wrappers=1:nokey=1', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = float(duration_result.stdout.strip())
        
        # Форматируем длительность в часы:минуты:секунды
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        # Получаем размер файла в МБ
        file_size_bytes = os.path.getsize(file_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        return {
            'duration': duration_str,
            'size': f"{file_size_mb:.2f} МБ"
        }
    except Exception as e:
        logger.error(f"Ошибка при получении информации о файле: {str(e)}")
        return {
            'duration': 'неизвестно',
            'size': 'неизвестно'
        }

def handle_document(update: Update, context: CallbackContext) -> None:
    """Обрабатывает полученные документы."""
    # Проверяем, что файл имеет расширение .mkv
    document = update.message.document
    file_name = document.file_name
    
    if not file_name.lower().endswith('.mkv'):
        update.message.reply_text('Пожалуйста, отправьте файл с расширением .mkv')
        return
    
    update.message.reply_text('Получен файл .mkv. Начинаю конвертацию в максимальном качестве...')
    
    # Создаем временные файлы для входного и выходного файлов
    with tempfile.NamedTemporaryFile(suffix='.mkv', delete=False) as input_temp:
        input_path = input_temp.name
    
    output_path = input_path.replace('.mkv', '.mp4')
    
    # Скачиваем файл
    file = update.message.document.get_file()
    file.download(input_path)
    
    try:
        # Конвертируем файл
        convert_mkv_to_mp4(input_path, output_path)
        
        # Получаем информацию о конвертированном файле
        file_info = get_file_info(output_path)
        
        # Отправляем конвертированный файл обратно пользователю
        output_filename = file_name.replace('.mkv', '.mp4')
        with open(output_path, 'rb') as output_file:
            update.message.reply_document(
                document=output_file,
                filename=output_filename,
                caption='Конвертация завершена!'
            )
        
        # Отправляем информацию о файле отдельным сообщением
        info_message = (
            f'Файл "{output_filename}" успешно конвертирован, '
            f'вес - {file_info["size"]}, '
            f'длительность - {file_info["duration"]}. '
            f'Спасибо что пользуетесь нашим сервисом!'
        )
        update.message.reply_text(info_message)
        
    except Exception as e:
        update.message.reply_text(f'Произошла ошибка при конвертации: {str(e)}')
        logger.error(f"Ошибка: {str(e)}")
    
    finally:
        # Удаляем временные файлы
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            logger.error(f"Ошибка при удалении временных файлов: {str(e)}")

def main() -> None:
    """Запускает бота."""
    # Создаем Updater и передаем ему токен бота
    updater = Updater(TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчик для документов
    dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

    # Запускаем бота
    updater.start_polling()
    logger.info("Бот запущен")
    print("Бот успешно запущен! Нажмите Ctrl+C для остановки.")
    
    # Продолжаем работу бота до нажатия Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
```

### requirements.txt
```
python-telegram-bot==13.15
python-dotenv==1.0.0
ffmpeg-python==0.2.0
requests==2.31.0
```

### .env
```
TELEGRAM_BOT_TOKEN=7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc
```

### .gitignore
```
# Временные файлы
*.mkv
*.mp4
temp/
__pycache__/
*.py[cod]
*$py.class

# Файлы окружения
.env
.venv
env/
venv/
ENV/

# Логи
*.log

# Файлы IDE
.idea/
.vscode/
*.swp
*.swo
```

## 4. Установка зависимостей

Вернитесь в консоль Bash и выполните следующие команды:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Проверка наличия FFmpeg
ffmpeg -version
```

## 5. Настройка Always-on задачи

1. Перейдите в раздел "Tasks" на PythonAnywhere
2. В разделе "Always-on tasks" (доступно только для платных аккаунтов):
   - Введите команду: `python /home/your-username/mkv-to-mp4-bot/bot.py`
   - Описание: "Telegram Bot для конвертации MKV в MP4"
3. Нажмите "Create" для создания задачи

## 6. Проверка работы бота

1. Найдите своего бота в Telegram
2. Отправьте команду `/start`
3. Отправьте файл .mkv для конвертации
4. Убедитесь, что бот отвечает и конвертирует файлы

## 7. Мониторинг и обслуживание

1. Регулярно проверяйте логи бота:
   - Перейдите в директорию проекта: `cd /home/your-username/mkv-to-mp4-bot`
   - Просмотрите лог: `tail -f bot.log`
2. Следите за использованием дискового пространства:
   - Перейдите в раздел "Files" и проверьте использование места
3. При необходимости перезапустите бота:
   - Перейдите в раздел "Tasks"
   - Остановите текущую задачу и запустите ее заново

## Дополнительные рекомендации

1. Настройте автоматическое обновление бота из репозитория:
   ```bash
   cd /home/your-username/mkv-to-mp4-bot
   git pull
   ```
2. Создайте скрипт для автоматического перезапуска бота при обновлении
3. Настройте уведомления о состоянии бота через Telegram 