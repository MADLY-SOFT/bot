import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = '7912798466:AAHMMt2pPa5lbiFqsw8cO_2Lg6tu3FhiVks'
DB_NAME = 'users.db'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def setup_database():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                click_count INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

async def get_user_click_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT click_count FROM users WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        if row:
            return row[0]
        return 0

async def increment_user_click_count(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        await db.execute('UPDATE users SET click_count = click_count + 1 WHERE user_id = ?', (user_id,))
        await db.commit()

@dp.message(CommandStart())
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    await increment_user_click_count(user_id)
    click_count = await get_user_click_count(user_id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Клик")]
        ],
        resize_keyboard=True
    )
    await message.reply(
        f"Привет, {message.from_user.first_name}! Твой счетчик кликов: {click_count}. Нажми кнопку ниже.",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "Клик")
async def handle_click(message: types.Message):
    user_id = message.from_user.id
    await increment_user_click_count(user_id)
    click_count = await get_user_click_count(user_id)

    await message.reply(f"Ты кликнул! Твой счетчик кликов: {click_count}.")

async def main():
    await setup_database()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
