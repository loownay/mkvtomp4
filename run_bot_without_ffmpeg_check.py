import os
import logging
import tempfile
import subprocess
import sys
from dotenv import load_dotenv
import ffmpeg
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена бота из переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не указан токен бота. Добавьте TELEGRAM_BOT_TOKEN в .env файл.")

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
    print("Запуск бота для конвертации MKV в MP4...")
    print("ВНИМАНИЕ: Для работы бота необходим установленный FFmpeg!")
    print("Если бот не работает, установите FFmpeg согласно инструкции в файле install_ffmpeg_manual.txt")
    print()
    
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