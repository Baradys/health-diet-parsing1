import json
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hbold, hlink
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from dotenv import load_dotenv
from sbermarket import get_data

load_dotenv()

TOKEN = str(os.environ.get('TOKEN'))

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(_):
    print('BOT STARTED')


class Form(StatesGroup):
    search = State()
    resource = State()


def main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    last_attempt = KeyboardButton(text='Получить предыдущий запрос')
    help_button = KeyboardButton(text='Справка')
    description_button = KeyboardButton(text='Описание')
    search_button = KeyboardButton(text='Выбрать ресурс для поиска')
    search_button = KeyboardButton(text='Ввести поисковый запрос')
    keyboard.add(last_attempt).add(description_button, help_button).add(search_button)
    return keyboard


def resource_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='МВидео', callback_data='res_mvideo')],
        [InlineKeyboardButton(text='СберМаркет', callback_data='res_sbermarket')],
        [InlineKeyboardButton(text='DNS', callback_data='res_dns')],
        [InlineKeyboardButton(text='Корпорация Центр', callback_data='res_kcent')],
        [InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')],
    ])
    return keyboard


@dp.message_handler(commands='start')
async def start_command(message: types.Message):
    await message.answer(f'<b>Добро пожаловать!</b>\nЭтот бот позволит найти интересующее Вас товары на СберМаркете со скидкой!',
                         reply_markup=main_menu_keyboard())
    await message.delete()


@dp.message_handler(Text(equals='Выбрать ресурс для поиска'))
async def resource_command(message: types.Message):
    await message.answer(text='Вы перешли в меню выбора сайта!', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Пожалуйста выберете сайт для поиска!', reply_markup=resource_keyboard())
    await message.delete()


@dp.message_handler(Text(equals='Ввести поисковый запрос'))
async def get_discount_search(message: types.Message):
    await Form.search.set()
    await message.reply("Вводите поисковый запрос:")


@dp.callback_query_handler(lambda callback: callback.startswith('res'), state=Form.search)
async def get_resource(callback: types.CallbackQuery):
    if callback.data.endswith('mvideo'):
        async with state.proxy() as data:
            data['search'] = callback.data ### ФИКСИТЬ!!!!



@dp.callback_query_handler()
async def main_menu(callback: types.CallbackQuery):
    await callback.message.answer('Возврат в главное меню!', reply_markup=main_menu_keyboard())


@dp.message_handler(state=Form.search)
async def get_discount_search(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['search'] = message.text
    await message.answer('Идет поиск. Примерное время ожидания: 30 секунд\nОжидайте...')
    get_data(message.text, message.from_user.id)
    with open(f'data/sbermarket-{message.from_user["id"]}.json', encoding='utf-8') as file:
        data = json.load(file)
    for item in data[:6]:
        card = f'{hlink(item.get("item_name"), item.get("url"))}\n' \
               f'{hbold("Старая цена")} {item.get("old_price")}\n' \
               f'👩🏿‍🎓👩🏿‍🎓{hbold("Новая цена")} -{item.get("discount")}%: {item.get("item_price")}👩🏿‍🎓👩🏿‍🎓\n'
        await message.answer(card)
    async with state.proxy() as data:
        for i in data:
            print(data)
    await state.finish()


def main():
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    main()
