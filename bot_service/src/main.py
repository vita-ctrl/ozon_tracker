import asyncio
import logging

from aiogram import Bot, Dispatcher
from bot import create_bot, create_dispatcher
from core import load_config

config = load_config()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)


    bot: Bot = create_bot(config)
    dp: Dispatcher = create_dispatcher(bot, )

    try:
        await dp.start_polling(bot, config=config, handle_signals=False)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
