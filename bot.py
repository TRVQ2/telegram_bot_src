from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from commands import *

import os


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)


@dp.message_handler()
async def echo_send(message: types.Message):
    text = process_message(message.text)
    if text is None or len(text.strip()) == 0:
        return
    await message.answer(text)
    # await message.answer(message.text)  # answer
    # await message.reply(message.text)  # reply to message
    # await bot.send_message(message.from_user.id, message.text)  # to private


# skip_updates=true - to check only those messages when bot is online
executor.start_polling(dp, skip_updates=True)
