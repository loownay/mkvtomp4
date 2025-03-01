# Пошаговая инструкция по размещению бота на VPS

## 1. Выбор и аренда VPS

### 1.1. Выбор провайдера VPS

Рекомендуемые провайдеры VPS:
- [DigitalOcean](https://www.digitalocean.com/) - простой интерфейс, хорошая документация
- [Linode](https://www.linode.com/) - стабильная работа, хорошая поддержка
- [Vultr](https://www.vultr.com/) - доступные цены, множество локаций
- [Yandex.Cloud](https://cloud.yandex.ru/) - российский провайдер, оплата в рублях

### 1.2. Минимальные требования для VPS

- ОС: Ubuntu 20.04 LTS
- RAM: 1 ГБ (для небольших файлов)
- CPU: 1 ядро
- Диск: 25 ГБ SSD
- Трафик: 1 ТБ/месяц

### 1.3. Создание VPS

1. Зарегистрируйтесь на выбранном сервисе
2. Создайте новый VPS (Droplet/Instance/Server)
3. Выберите Ubuntu 20.04 LTS в качестве операционной системы
4. Выберите подходящий тарифный план (от $5/месяц)
5. Выберите ближайший к вам регион
6. Добавьте SSH-ключ или выберите пароль для доступа
7. Создайте VPS

## 2. Подключение к VPS

### 2.1. Подключение по SSH

#### Для Windows:
1. Установите [PuTTY](https://www.putty.org/) или используйте Windows Terminal
2. Подключитесь к серверу:
   ```
   ssh root@ваш_ip_адрес
   ```

#### Для Linux/macOS:
1. Откройте терминал
2. Подключитесь к серверу:
   ```bash
   ssh root@ваш_ip_адрес
   ```

### 2.2. Первоначальная настройка сервера

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка необходимых пакетов
apt install -y python3 python3-pip python3-venv git ffmpeg

# Создание нового пользователя (более безопасно, чем использование root)
adduser botuser
# Следуйте инструкциям для создания пароля и заполнения информации

# Добавление пользователя в sudo группу
usermod -aG sudo botuser

# Переключение на нового пользователя
su - botuser
```

## 3. Установка и настройка бота

### 3.1. Клонирование репозитория

```bash
# Создание директории для бота
mkdir ~/mkv-to-mp4-bot
cd ~/mkv-to-mp4-bot

# Клонирование репозитория (если есть)
# git clone https://github.com/your-username/mkv-to-mp4-bot.git .
```

### 3.2. Создание файлов проекта

Если у вас нет репозитория, создайте файлы вручную:

#### bot.py
```bash
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

#### requirements.txt
```bash
cat > requirements.txt << 'EOL'
python-telegram-bot==13.15
python-dotenv==1.0.0
ffmpeg-python==0.2.0
requests==2.31.0
EOL
```

#### .env
```bash
cat > .env << 'EOL'
TELEGRAM_BOT_TOKEN=7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc
EOL
```

### 3.3. Создание виртуального окружения и установка зависимостей

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Проверка наличия FFmpeg
ffmpeg -version
```

## 4. Настройка автозапуска с помощью systemd

### 4.1. Создание systemd сервиса

```bash
# Выход из виртуального окружения
deactivate

# Создание файла сервиса (требуются права sudo)
sudo nano /etc/systemd/system/telegrambot.service
```

Содержимое файла сервиса:
```
[Unit]
Description=Telegram Bot для конвертации MKV в MP4
After=network.target

[Service]
User=botuser
WorkingDirectory=/home/botuser/mkv-to-mp4-bot
ExecStart=/home/botuser/mkv-to-mp4-bot/venv/bin/python /home/botuser/mkv-to-mp4-bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4.2. Активация и запуск сервиса

```bash
# Перезагрузка конфигурации systemd
sudo systemctl daemon-reload

# Включение автозапуска сервиса
sudo systemctl enable telegrambot

# Запуск сервиса
sudo systemctl start telegrambot

# Проверка статуса сервиса
sudo systemctl status telegrambot
```

## 5. Проверка работы бота

1. Найдите своего бота в Telegram
2. Отправьте команду `/start`
3. Отправьте файл .mkv для конвертации
4. Убедитесь, что бот отвечает и конвертирует файлы

## 6. Мониторинг и обслуживание

### 6.1. Просмотр логов

```bash
# Просмотр логов systemd
sudo journalctl -u telegrambot -f

# Просмотр логов бота
tail -f ~/mkv-to-mp4-bot/bot.log
```

### 6.2. Управление сервисом

```bash
# Остановка бота
sudo systemctl stop telegrambot

# Запуск бота
sudo systemctl start telegrambot

# Перезапуск бота
sudo systemctl restart telegrambot

# Отключение автозапуска
sudo systemctl disable telegrambot
```

### 6.3. Обновление бота

```bash
# Переход в директорию проекта
cd ~/mkv-to-mp4-bot

# Если используется Git
git pull

# Активация виртуального окружения
source venv/bin/activate

# Обновление зависимостей
pip install -r requirements.txt

# Выход из виртуального окружения
deactivate

# Перезапуск сервиса
sudo systemctl restart telegrambot
```

## 7. Настройка безопасности

### 7.1. Настройка брандмауэра

```bash
# Установка UFW (Uncomplicated Firewall)
sudo apt install ufw

# Разрешение SSH
sudo ufw allow ssh

# Включение брандмауэра
sudo ufw enable

# Проверка статуса
sudo ufw status
```

### 7.2. Настройка автоматических обновлений

```bash
# Установка unattended-upgrades
sudo apt install unattended-upgrades

# Настройка автоматических обновлений
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 8. Важные замечания

1. Токен бота (7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc) уже настроен и готов к использованию
2. Для обработки больших файлов может потребоваться VPS с большим объемом RAM
3. Регулярно проверяйте логи бота для выявления ошибок
4. Настройте мониторинг для отслеживания работоспособности бота
5. Регулярно делайте резервные копии файлов бота 