# Супер подробная инструкция по размещению бота на PythonAnywhere

## 1. Регистрация на PythonAnywhere

1. Перейдите на сайт [PythonAnywhere](https://www.pythonanywhere.com/)
2. Нажмите кнопку "Pricing & Signup" в верхнем меню
3. Выберите тариф:
   - Для тестирования можно выбрать бесплатный тариф "Beginner"
   - Для постоянной работы бота рекомендуется тариф "Hacker" ($5/месяц)
4. Нажмите кнопку "Create a Beginner account" или "Create a Hacker account"
5. Заполните форму регистрации:
   - Username: придумайте имя пользователя
   - Email: укажите ваш email
   - Password: придумайте пароль
6. Поставьте галочку согласия с условиями и нажмите "Register"
7. Подтвердите email, перейдя по ссылке в письме

## 2. Создание консоли и настройка проекта

1. После входа в аккаунт перейдите в раздел "Consoles" в верхнем меню
2. Нажмите на кнопку "Bash" для создания новой консоли
3. В открывшейся консоли выполните следующие команды (копируйте и вставляйте по одной):

```bash
# Создаем директорию для проекта
mkdir mkv-to-mp4-bot
```

```bash
# Переходим в созданную директорию
cd mkv-to-mp4-bot
```

```bash
# Создаем файл bot.py
cat > bot.py << 'EOL'
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
EOL
```

```bash
# Создаем файл requirements.txt
cat > requirements.txt << 'EOL'
python-telegram-bot==13.15
python-dotenv==1.0.0
ffmpeg-python==0.2.0
requests==2.31.0
EOL
```

```bash
# Создаем файл .env с токеном бота
cat > .env << 'EOL'
TELEGRAM_BOT_TOKEN=7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc
EOL
```

```bash
# Создаем файл .gitignore
cat > .gitignore << 'EOL'
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
EOL
```

## 3. Установка зависимостей

Выполните следующие команды в консоли:

```bash
# Создаем виртуальное окружение
python3 -m venv venv
```

```bash
# Активируем виртуальное окружение
source venv/bin/activate
```

```bash
# Устанавливаем зависимости
pip install -r requirements.txt
```

```bash
# Проверяем наличие FFmpeg (должен быть уже установлен на PythonAnywhere)
ffmpeg -version
```

## 4. Настройка Always-on задачи (для платных аккаунтов)

1. Перейдите в раздел "Tasks" в верхнем меню
2. В разделе "Always-on tasks" (доступно только для платных аккаунтов):
   - В поле "Command to run" введите следующую команду (замените `your-username` на ваше имя пользователя на PythonAnywhere):
   ```
   /home/your-username/mkv-to-mp4-bot/venv/bin/python /home/your-username/mkv-to-mp4-bot/bot.py
   ```
   - В поле "Description" введите: `Telegram Bot для конвертации MKV в MP4`
3. Нажмите кнопку "Create" для создания задачи

## 5. Настройка Scheduled Task (для бесплатных аккаунтов)

Если у вас бесплатный аккаунт, вы можете настроить запуск бота по расписанию:

1. Перейдите в раздел "Tasks" в верхнем меню
2. В разделе "Scheduled tasks":
   - В поле "Hour" выберите час запуска (например, 0)
   - В поле "Minute" выберите минуту запуска (например, 0)
   - В поле "Command" введите следующую команду (замените `your-username` на ваше имя пользователя на PythonAnywhere):
   ```
   /home/your-username/mkv-to-mp4-bot/venv/bin/python /home/your-username/mkv-to-mp4-bot/bot.py
   ```
3. Нажмите кнопку "Create" для создания задачи

## 6. Создание скрипта для запуска бота

Создайте скрипт для ручного запуска бота:

```bash
# Создаем скрипт для запуска бота
cat > run_bot.sh << 'EOL'
#!/bin/bash
cd ~/mkv-to-mp4-bot
source venv/bin/activate
python bot.py
EOL
```

```bash
# Делаем скрипт исполняемым
chmod +x run_bot.sh
```

## 7. Проверка работы бота

1. Запустите бота вручную для проверки:

```bash
# Запускаем бота
./run_bot.sh
```

2. Откройте Telegram и найдите своего бота по имени или перейдите по ссылке: `https://t.me/your_bot_username`
3. Отправьте команду `/start`
4. Отправьте файл .mkv для конвертации
5. Убедитесь, что бот отвечает и конвертирует файлы
6. Для остановки бота нажмите Ctrl+C в консоли

## 8. Мониторинг и обслуживание

### 8.1. Просмотр логов бота

```bash
# Просмотр последних 100 строк лога
tail -n 100 ~/mkv-to-mp4-bot/bot.log
```

```bash
# Просмотр лога в реальном времени
tail -f ~/mkv-to-mp4-bot/bot.log
```

### 8.2. Проверка использования дискового пространства

```bash
# Проверка использования дискового пространства
du -sh ~/mkv-to-mp4-bot
```

### 8.3. Обновление бота

Если вам нужно обновить код бота:

```bash
# Переходим в директорию проекта
cd ~/mkv-to-mp4-bot
```

```bash
# Редактируем файл bot.py
nano bot.py
```

После внесения изменений нажмите Ctrl+O для сохранения и Ctrl+X для выхода из редактора.

```bash
# Перезапускаем бота (если запущен через Always-on task)
# Перейдите в раздел "Tasks" и нажмите кнопку "Restart" рядом с задачей
```

## 9. Решение проблем

### 9.1. Проверка статуса бота

```bash
# Проверка, запущен ли процесс бота
ps aux | grep python | grep bot.py
```

### 9.2. Проверка доступа к Telegram API

```bash
# Проверка доступа к API Telegram
curl -s https://api.telegram.org/bot7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc/getMe | python -m json.tool
```

### 9.3. Проверка наличия FFmpeg

```bash
# Проверка наличия FFmpeg
which ffmpeg
```

```bash
# Проверка версии FFmpeg
ffmpeg -version
```

### 9.4. Перезапуск бота вручную

```bash
# Остановка всех процессов бота
pkill -f "python.*bot.py"
```

```bash
# Запуск бота
cd ~/mkv-to-mp4-bot && source venv/bin/activate && python bot.py
```

## 10. Дополнительные рекомендации

### 10.1. Настройка автоматического перезапуска бота

Создайте скрипт для проверки работы бота и его перезапуска:

```bash
# Создаем скрипт для проверки и перезапуска бота
cat > check_and_restart.sh << 'EOL'
#!/bin/bash
if ! pgrep -f "python.*bot.py" > /dev/null; then
    echo "Бот не запущен. Перезапуск..."
    cd ~/mkv-to-mp4-bot
    source venv/bin/activate
    nohup python bot.py > bot_restart.log 2>&1 &
    echo "Бот перезапущен."
else
    echo "Бот работает нормально."
fi
EOL
```

```bash
# Делаем скрипт исполняемым
chmod +x check_and_restart.sh
```

### 10.2. Настройка уведомлений о состоянии бота

Создайте скрипт для отправки уведомлений о состоянии бота:

```bash
# Создаем скрипт для отправки уведомлений
cat > send_notification.sh << 'EOL'
#!/bin/bash
TOKEN="7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc"
CHAT_ID="ваш_chat_id"  # Замените на ваш Chat ID
MESSAGE="$1"

curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" -d chat_id=$CHAT_ID -d text="$MESSAGE"
EOL
```

```bash
# Делаем скрипт исполняемым
chmod +x send_notification.sh
```

### 10.3. Получение вашего Chat ID

Для получения вашего Chat ID:

1. Отправьте сообщение боту @userinfobot в Telegram
2. Бот ответит вам сообщением, содержащим ваш Chat ID
3. Замените `ваш_chat_id` в скрипте `send_notification.sh` на полученный Chat ID

## 11. Важные замечания

1. На бесплатном тарифе PythonAnywhere есть ограничения:
   - Ограничение на размер файлов (до 500 МБ)
   - Ограничение на использование CPU
   - Нет возможности запускать Always-on задачи

2. Для постоянной работы бота рекомендуется использовать платный тариф "Hacker" ($5/месяц)

3. Токен бота (7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc) уже настроен и готов к использованию

4. Если вы хотите использовать другого бота, замените токен в файле `.env`

5. Регулярно проверяйте логи бота для выявления ошибок

6. Настройте мониторинг для отслеживания работоспособности бота