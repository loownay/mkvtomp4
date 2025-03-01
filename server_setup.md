# Инструкция по размещению бота на сервере

## 1. Размещение на PythonAnywhere (рекомендуется для начинающих)

1. Зарегистрируйтесь на [PythonAnywhere](https://www.pythonanywhere.com/)
2. Перейдите в раздел "Consoles" и создайте новую Bash консоль
3. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/mkv-to-mp4-bot.git
   cd mkv-to-mp4-bot
   ```
4. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Создайте файл .env с токеном бота:
   ```bash
   echo "TELEGRAM_BOT_TOKEN=7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc" > .env
   ```
6. Перейдите в раздел "Tasks" и создайте новую задачу:
   - Выберите "Always-on task" (для платных аккаунтов)
   - Команда: `python /home/ваш_логин/mkv-to-mp4-bot/bot.py`
   - Описание: "Telegram Bot для конвертации MKV в MP4"
7. Сохраните задачу и запустите ее

## 2. Размещение на Heroku

1. Зарегистрируйтесь на [Heroku](https://www.heroku.com/)
2. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Войдите в аккаунт Heroku через терминал:
   ```bash
   heroku login
   ```
4. Создайте новое приложение:
   ```bash
   heroku create mkv-to-mp4-bot
   ```
5. Добавьте buildpack для FFmpeg:
   ```bash
   heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
   heroku buildpacks:add heroku/python
   ```
6. Настройте переменные окружения:
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc
   ```
7. Загрузите ваш проект на Heroku:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push heroku master
   ```
8. Запустите worker:
   ```bash
   heroku ps:scale worker=1
   ```

## 3. Размещение на VPS (DigitalOcean, Linode, Vultr и т.д.)

1. Арендуйте VPS с Ubuntu
2. Подключитесь к серверу по SSH
3. Установите необходимые пакеты:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip ffmpeg git
   ```
4. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/mkv-to-mp4-bot.git
   cd mkv-to-mp4-bot
   ```
5. Установите зависимости:
   ```bash
   pip3 install -r requirements.txt
   ```
6. Создайте файл .env с токеном бота:
   ```bash
   echo "TELEGRAM_BOT_TOKEN=7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc" > .env
   ```
7. Настройте автозапуск с помощью systemd:
   ```bash
   sudo nano /etc/systemd/system/telegrambot.service
   ```
8. Добавьте следующее содержимое:
   ```
   [Unit]
   Description=Telegram Bot для конвертации MKV в MP4
   After=network.target

   [Service]
   User=ваш_пользователь
   WorkingDirectory=/путь/к/mkv-to-mp4-bot
   ExecStart=/usr/bin/python3 /путь/к/mkv-to-mp4-bot/bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
9. Включите и запустите сервис:
   ```bash
   sudo systemctl enable telegrambot
   sudo systemctl start telegrambot
   ```
10. Проверьте статус:
    ```bash
    sudo systemctl status telegrambot
    ```

## Важные замечания

1. Токен бота (7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc) уже настроен и готов к использованию
2. На серверах обычно есть ограничения на размер файлов и дисковое пространство
3. Для обработки больших файлов может потребоваться VPS с большим объемом RAM
4. Регулярно проверяйте логи бота для выявления ошибок
5. Настройте мониторинг для отслеживания работоспособности бота 