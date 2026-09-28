import os
import base64
import asyncio
from datetime import datetime, timezone, timedelta

from telethon import TelegramClient
from telethon.tl.functions.account import UpdateUsernameRequest
from telethon.errors import (
    FloodWaitError,
    UsernameOccupiedError,
    UsernameInvalidError
)

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]

session_data = base64.b64decode(os.environ["SESSION_B64"])

with open("my_session.session", "wb") as f:
    f.write(session_data)

client = TelegramClient(
    "my_session",
    api_id,
    api_hash,
    device_model="iPhone 15 Pro",
    system_version="17.5.1",
    app_version="10.14.5"
)

MSK = timezone(timedelta(hours=3))


def get_msk_username():
    return f"msk{datetime.now(MSK).strftime('%H%M')}"


async def change_username(username):
    try:
        await client(UpdateUsernameRequest(username=username))
        print(f"Ник изменён → @{username}")
        return True

    except UsernameOccupiedError:
        alt = f"time{username[3:]}"
        try:
            await client(UpdateUsernameRequest(username=alt))
            print(f"Ник изменён → @{alt}")
            return True
        except Exception as e:
            print(f"Запасной вариант: {e}")
            return False

    except FloodWaitError as e:
        print(f"FloodWait: {e.seconds} сек")
        await asyncio.sleep(e.seconds + 1)
        return False

    except UsernameInvalidError:
        print(f"Некорректный username: @{username}")
        return False

    except Exception as e:
        print(f"Ошибка: {e}")
        return False


async def main():
    await client.connect()

    if not await client.is_user_authorized():
        print("SESSION НЕ АВТОРИЗОВАНА")
        return

    print("Скрипт запущен.")

    last_minute = None

    while True:
        current_minute = datetime.now(MSK).strftime("%H%M")

        if current_minute != last_minute:
            await change_username(get_msk_username())
            last_minute = current_minute

        await asyncio.sleep(0.2)


with client:
    client.loop.run_until_complete(main())
