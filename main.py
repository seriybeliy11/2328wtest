import asyncio
import logging
import os

import uvicorn
from dotenv import load_dotenv

from bot import create_bot
from callback import app as callback_app

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

log = logging.getLogger("main")


async def run_bot(bot, dp):
    log.info("Starting bot polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def main():
    bot, dp = create_bot()

    # FastAPI в фоне
    config = uvicorn.Config(
        callback_app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        log_level="warning",
    )
    server = uvicorn.Server(config)

    # Запускаем параллельно
    await asyncio.gather(
        server.serve(),
        run_bot(bot, dp),
    )


if __name__ == "__main__":
    asyncio.run(main())