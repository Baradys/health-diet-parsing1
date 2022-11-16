import json
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hbold, hlink
from dotenv import load_dotenv
from sbermarket import get_data

load_dotenv()

TOKEN = str(os.environ.get('TOKEN'))

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    search = State()


@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['Телевизоры', 'Ввести поисковый запрос']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer(f'Добро пожаловать!\nЭтот бот позволит найти интересующее Вас товары на СберМаркете со скидкой!',
                         reply_markup=keyboard)


@dp.message_handler(Text(equals='Телевизоры'))
async def get_discount_tv(message: types.Message):
    await message.answer('Идет поиск. Примерное время ожидания: 30 секунд\nОжидайте...')

    get_data('Телевизор', message.from_user.id)
    with open(f'data/sbermarket-{message.from_user["id"]}.json', encoding='utf-8') as file:
        data = json.load(file)

    counter = 0
    for item in data[:6]:
        card = f'{hlink(item.get("item_name"), item.get("url"))}\n' \
               f'{hbold("Старая цена")} {item.get("old_price")}\n' \
               f'👩🏿‍🎓👩🏿‍🎓{hbold("Новая цена")} -{item.get("discount")}%: {item.get("item_price")}👩🏿‍🎓👩🏿‍🎓\n'
        # if counter % 5 == 0 and counter != 0:
        #     continue_buttons = ['Да', 'Нет']
        #     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        #     keyboard.add(*continue_buttons)
        #     x = await message.answer('Показать следующие пять товаров 5 товаров?', reply_markup=keyboard)
        #
        # counter += 1
        await message.answer(card)


@dp.message_handler(Text(equals='Ввести поисковый запрос'))
async def get_discount_search(message: types.Message):
    await Form.search.set()
    await message.reply("Вводите поисковый запрос:")


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
    await state.reset_state(with_data=True)


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
