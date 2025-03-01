# Пошаговая инструкция по размещению бота на Heroku

## 1. Подготовка к размещению на Heroku

### 1.1. Создание аккаунта на Heroku

1. Перейдите на сайт [Heroku](https://www.heroku.com/)
2. Нажмите кнопку "Sign Up" и заполните форму регистрации
3. Подтвердите email и установите пароль

### 1.2. Установка Heroku CLI

1. Скачайте и установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Откройте командную строку или терминал
3. Войдите в аккаунт Heroku:
   ```bash
   heroku login
   ```

### 1.3. Подготовка проекта

1. Убедитесь, что в корне проекта есть следующие файлы:
   - `bot.py` - основной файл бота
   - `requirements.txt` - зависимости проекта
   - `Procfile` - инструкции для Heroku
   - `runtime.txt` - версия Python

2. Создайте файл `Procfile` (если его нет):
   ```
   worker: python bot.py
   ```

3. Создайте файл `runtime.txt` (если его нет):
   ```
   python-3.9.16
   ```

## 2. Создание репозитория Git

### 2.1. Инициализация Git репозитория

1. Откройте командную строку или терминал
2. Перейдите в директорию проекта
3. Инициализируйте Git репозиторий:
   ```bash
   git init
   ```

### 2.2. Создание файла .gitignore

Создайте файл `.gitignore` со следующим содержимым:
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

### 2.3. Добавление файлов в репозиторий

```bash
git add .
git commit -m "Initial commit"
```

## 3. Создание приложения на Heroku

### 3.1. Создание нового приложения

```bash
heroku create mkv-to-mp4-bot
```

### 3.2. Добавление buildpack для FFmpeg

```bash
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add heroku/python
```

### 3.3. Настройка переменных окружения

```bash
heroku config:set TELEGRAM_BOT_TOKEN=7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc
```

## 4. Деплой приложения на Heroku

### 4.1. Загрузка приложения на Heroku

```bash
git push heroku master
```

Если вы используете ветку `main` вместо `master`:
```bash
git push heroku main
```

### 4.2. Запуск worker процесса

```bash
heroku ps:scale worker=1
```

### 4.3. Проверка логов

```bash
heroku logs --tail
```

## 5. Проверка работы бота

1. Найдите своего бота в Telegram
2. Отправьте команду `/start`
3. Отправьте файл .mkv для конвертации
4. Убедитесь, что бот отвечает и конвертирует файлы

## 6. Управление приложением на Heroku

### 6.1. Остановка бота

```bash
heroku ps:scale worker=0
```

### 6.2. Запуск бота

```bash
heroku ps:scale worker=1
```

### 6.3. Перезапуск бота

```bash
heroku restart
```

### 6.4. Просмотр логов

```bash
heroku logs --tail
```

## 7. Обновление бота

### 7.1. Внесение изменений в код

1. Внесите необходимые изменения в код
2. Добавьте изменения в Git:
   ```bash
   git add .
   git commit -m "Update bot code"
   ```

### 7.2. Деплой обновлений

```bash
git push heroku master
```

## 8. Важные замечания

1. Heroku имеет ограничения на бесплатном тарифе:
   - Приложение "засыпает" после 30 минут неактивности
   - Ограничение на 550 часов работы в месяц
   - Ограничение на размер файлов (до 500 МБ)

2. Для постоянной работы бота рекомендуется использовать платный тариф Hobby ($7/месяц)

3. Временные файлы на Heroku удаляются при перезапуске приложения

4. Токен бота (7261127585:AAHbO54mDWgorVxFF6Lr-SKVnfF3HTTD4lc) уже настроен и готов к использованию

## 9. Полезные команды Heroku

```bash
# Просмотр информации о приложении
heroku apps:info

# Просмотр переменных окружения
heroku config

# Добавление переменной окружения
heroku config:set KEY=VALUE

# Удаление переменной окружения
heroku config:unset KEY

# Просмотр логов
heroku logs --tail

# Запуск bash консоли
heroku run bash

# Просмотр запущенных процессов
heroku ps

# Масштабирование процессов
heroku ps:scale worker=1

# Перезапуск приложения
heroku restart
``` 