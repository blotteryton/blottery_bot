from os import getenv
import logging

from dotenv import load_dotenv

from aiogram.types import InlineQueryResultGame, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.executor import start_webhook
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.web_app_info import WebAppInfo
from uuid import uuid4

import requests
import json

load_dotenv()
WEBHOOK_PATH = '/'
WEBHOOK_URL = getenv('WEBHOOK_URL')
WEBAPP_PORT = getenv('WEBHOOK_PORT')
API_TOKEN = getenv('TOKEN')
START_ID_IMAGE = getenv('START_ID_IMAGE')
STATS_CLICK_URL = getenv('STATS_CLICK_URL')


START_TITLE = getenv("START_TITLE")
START_DESCRIPTION = getenv("START_DESCRIPTION")
CATALOG_URL = getenv("CATALOG_URL")
GAME_SHORT_NAME = getenv("GAME_SHORT_NAME")

logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    gameState = State()


@dp.message_handler(lambda c: c.text.lower() == 'назад', state='*')
async def back(message: types.Message, state: FSMContext):
    await state.finish()
    await send_welcome(message)
    return


@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Каталог'))
    b_inl_1 = InlineKeyboardButton(text='Открыть', web_app=WebAppInfo(url = CATALOG_URL + str(message.from_user.id)) )
    #Create inline keyboard
    inline_kb = InlineKeyboardMarkup(row_width = 1)
    inline_kb.row(b_inl_1)
    text = f"<b>{START_TITLE}</b>\{START_DESCRIPTION}"

    #await bot.send_photo(message.from_user.id, photo=START_ID_IMAGE, caption=text, reply_markup = inline_kb, parse_mode='HTML')
    #get params and create post request with json
    if(len(message.text) > 7) :
        data = message.text.split('/start ')
        if(len(data) > 1) : 
            str_params = data[1] + "&tel_id=" + str(message.from_user.id) 
            listRes = list(str_params.split("&"))
            req = {}
            for param in listRes:
                param = param.split("=")
                req.update({param[0]:param[1]})
            #req = json.dumps(req)
            req_headers = {'Content-type': 'application/json'}
            resp = requests.post(STATS_CLICK_URL, json = req, headers = req_headers)
    await bot.send_game(chat_id=message.from_user.id, game_short_name=GAME_SHORT_NAME)

@dp.message_handler(content_types=['photo'])
async def send_id(message: types.Message):    
    await message.answer(text=message.photo[0].file_id)

@dp.message_handler(lambda c: c.text == 'Каталог')
async def catalog_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
KeyboardButton(text=GAME_SHORT_NAME)
)
    await message.answer(text='Каталог', reply_markup=keyboard)


@dp.message_handler(lambda c: c.text in (GAME_SHORT_NAME,))
async def catalog_handler(message: types.Message):
    await bot.send_game(chat_id=message.from_user.id, game_short_name=message.text)

@dp.inline_handler()
async def send_game(inline_query: types.InlineQuery):
    from uuid import uuid4
    await bot.answer_inline_query(inline_query.id,
[InlineQueryResultGame(id=str(uuid4()),
    game_short_name=GAME_SHORT_NAME)
])


@dp.callback_query_handler(lambda callback_query: callback_query.game_short_name in (GAME_SHORT_NAME,))
async def inline_handler(callback_query: types.CallbackQuery):
    dct = {GAME_SHORT_NAME: CATALOG_URL + str(callback_query.from_user.id)}
    await bot.answer_callback_query(callback_query.id, url=dct[callback_query.game_short_name])


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        skip_updates=True,
        host='0.0.0.0',
        port=WEBAPP_PORT
    )
