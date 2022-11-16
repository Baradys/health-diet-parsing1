import os

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()

TOKEN = str(os.environ.get('TOKEN'))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['Телевизоры', 'Мониторы', 'Видеокарты', 'Ввести поисковый запрос']
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*start_buttons)
    await message.answer(f'Добро пожаловать!\nЭтот бот позволит найти интересующее Вас товары на СберМаркете со скидкой!')


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
