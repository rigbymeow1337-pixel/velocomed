import os
import asyncio
from datetime import datetime, timezone, timedelta

from telethon import TelegramClient
from telethon.tl.functions.account import UpdateUsernameRequest
from telethon.errors import (
    FloodWaitError,
    UsernameOccupiedError,
    UsernameInvalidError
)

# =========================
# CONFIG
# =========================

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient(
    "my_session",
    api_id,
    api_hash,
    device_model="iPhone 15 Pro",
    system_version="17.5.1",
    app_version="10.14.5"
)

MSK = timezone(timedelta(hours=3))


# =========================
# USERNAME
# =========================

def get_msk_username():
    now = datetime.now(MSK)
    return f"msk{now.strftime('%H%M')}"


async def change_username(username: str):
    try:
        await client(UpdateUsernameRequest(username=username))

        print(
            f"[{datetime.now(MSK).strftime('%H:%M:%S')}] "
            f"Ник изменён → @{username}"
        )

        return True

    except UsernameOccupiedError:
        print(f"@{username} занят, пробую запасной вариант...")

        alt = f"time{username[3:]}"

        try:
            await client(UpdateUsernameRequest(username=alt))

            print(
                f"[{datetime.now(MSK).strftime('%H:%M:%S')}] "
                f"Ник изменён → @{alt}"
            )

            return True

        except Exception as e:
            print(f"Запасной вариант не сработал: {e}")
            return False

    except UsernameInvalidError:
        print(f"Некорректный username: @{username}")
        return False

    except FloodWaitError as e:
        print(f"FloodWait: ждём {e.seconds} секунд...")
        await asyncio.sleep(e.seconds + 1)
        return False

    except Exception as e:
        print(f"Ошибка смены ника: {e}")
        return False


# =========================
# MAIN
# =========================

async def main():

    await client.connect()

    if not await client.is_user_authorized():
        print("ОШИБКА: my_session.session не авторизована.")
        return

    print("Скрипт запущен.")
    print("Ник меняется каждую минуту по МСК.")
    print("Формат: @mskЧЧММ")
    print()

    last_minute = None

    while True:
        now = datetime.now(MSK)
        current_minute = now.strftime("%H%M")

        if current_minute != last_minute:
            username = get_msk_username()

            await change_username(username)

            last_minute = current_minute

        await asyncio.sleep(0.2)


with client:
    client.loop.run_until_complete(main())