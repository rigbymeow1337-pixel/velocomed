from telethon import TelegramClient
from telethon.tl.functions.account import UpdateUsernameRequest
from telethon.errors import FloodWaitError, UsernameOccupiedError, UsernameInvalidError
import asyncio
from datetime import datetime, timezone, timedelta
import time

api_id = 34217896
api_hash = '07d4ef1b91f26e7bc5da97a46c52462b'

client = TelegramClient(
    'my_session',
    api_id,
    api_hash,
    device_model="iPhone 15 Pro",
    system_version="17.5.1",
    app_version="10.14.5"
)

# Московское время = UTC+3
MSK = timezone(timedelta(hours=3))

def get_msk_username():
    """Возвращает ник вида msk1432"""
    now = datetime.now(MSK)
    return f"msk{now.strftime('%H%M')}"

async def change_username(username: str):
    try:
        await client(UpdateUsernameRequest(username=username))
        print(f"[{datetime.now(MSK).strftime('%H:%M:%S')}] Ник изменён → @{username}")
        return True
    except UsernameOccupiedError:
        print(f"@{username} занят, пробую другой вариант...")
        # запасной вариант
        alt = f"time{username[3:]}"
        try:
            await client(UpdateUsernameRequest(username=alt))
            print(f"[{datetime.now(MSK).strftime('%H:%M:%S')}] Ник изменён → @{alt}")
            return True
        except Exception as e:
            print(f"Не удалось сменить на запасной: {e}")
            return False
    except FloodWaitError as e:
        print(f"FloodWait {e.seconds} сек")
        await asyncio.sleep(e.seconds + 1)
        return False
    except Exception as e:
        print(f"Ошибка смены ника: {e}")
        return False

async def main():
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Сначала войди в аккаунт")
        return
    
    print("Скрипт запущен. Ник будет меняться каждую минуту по МСК.")
    print("Формат: @mskЧЧММ\n")
    
    last_minute = None
    
    while True:
        now = datetime.now(MSK)
        current_minute = now.strftime('%H%M')
        
        # Меняем ник только когда минута реально сменилась
        if current_minute != last_minute:
            username = get_msk_username()
            await change_username(username)
            last_minute = current_minute
        
        # Спим до следующей секунды (максимально точно)
        await asyncio.sleep(0.2)

with client:
    client.loop.run_until_complete(main())