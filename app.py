import asyncio
import json
import hmac
import hashlib
import base64
import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp import web
import os

WEBHOOK_PATH = '/'
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 5000))

bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
dp = Dispatcher()

PROJECT_UUID = os.getenv("PROJECT_UUID")
API_KEY = os.getenv("API_KEY")


def api_sign(body: str, api_key: str) -> str:
    b64 = base64.b64encode(body.encode())
    return hmac.new(api_key.encode(), b64, hashlib.sha256).hexdigest()


@dp.message(F.text.contains('/start'))
async def cmd_start(message: Message):
    data = {
        "order_id": f"INV_{message.from_user.id}_{int(message.date.timestamp())}",
        "amount": "5.00000000",
        "currency": "USDT"
    }

    body = json.dumps(data, separators=(',', ':'))
    sign = api_sign(body, API_KEY)

    headers = {
        "Content-Type": "application/json",
        "project": PROJECT_UUID,
        "sign": sign
    }

    resp = await httpx.post(
        "https://api.2328.io/v1/payment",
        content=body.encode(),
        headers=headers
    )

    link = resp.json()["result"]["tg_deeplink"]
    await message.answer(link)


async def on_startup(app: web.Application):
    await bot.set_webhook(url=f'{os.getenv("RENDER_URL")}{WEBHOOK_PATH}')


async def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
    await site.start()

    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
