import re
import sqlite3

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import markups as nav

TOKEN = "TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
state = "start"


async def give_inventory(username):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    query = 'SELECT * FROM {username}_inventory'.replace("{username}", username)
    cur.execute(query)
    data = cur.fetchall()
    if data == []:
        return "Нет кейсов"
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\,|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        q = i + "\n"
        c.append(q)
    val = '\n'.join(c)
    return val


async def new_item(username):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('INSERT INTO {username}_inventory VALUES(?)'.replace("{username}", username), ("Скин",))
    con.commit()


async def give_money(username):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('UPDATE users SET balance = ? WHERE username = ?', (100, username,))
    con.commit()


async def give_balance(username):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    balance = str(cur.execute('SELECT balance FROM users WHERE username = ?', (username,)).fetchone()).strip("(),")
    con.commit()
    return int(balance)


async def new_user(username):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, balance INTEGER)')
    cur.execute('CREATE TABLE IF NOT EXISTS {username}_inventory (items TEXT)'.replace("{username}", username))
    con.commit()
    data = str(cur.execute('SELECT balance FROM users WHERE username = ?', (username,)).fetchone())
    if data == "None":
        cur.execute('INSERT INTO users VALUES(?, ?)', (username, 0))
        con.commit()


async def send_base():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    query = 'SELECT * FROM cases'
    cur.execute(query)
    data = cur.fetchall()
    if data == []:
        return "Нет кейсов"
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\,|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        q = i + "\n"
        c.append(q)
    val = '\n'.join(c)
    return val


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await new_user(message.from_user.username)
    await bot.send_message(message.chat.id, "Привет! Ты находишься в магазине кейсов", reply_markup=nav.mainMenu)


@dp.message_handler()
async def bot_message(message: types.Message):
    global state
    if message.chat.type == 'private':
        if message.text == "Кейсы":
            await bot.send_message(message.chat.id, await send_base(),
                                   reply_markup=nav.mainMenu)
            state = "buy_case"
            await bot.send_message(message.chat.id, "Выбери кейс, который хочешь купить",
                                   reply_markup=nav.mainMenu)
        elif message.text == "Баланс":
            await bot.send_message(message.chat.id, str(await give_balance(message.from_user.username)),
                                   reply_markup=nav.mainMenu)
        elif message.text == "Халява":
            await give_money(message.from_user.username)
            await bot.send_message(message.chat.id, "Проверь баланс)",
                                   reply_markup=nav.mainMenu)
        elif message.text == "Инвентарь":
            await bot.send_message(message.chat.id, await give_inventory(message.from_user.username),
                                   reply_markup=nav.mainMenu)
        elif message.text == "⬅ Главное меню":
            state = "start"
            await bot.send_message(message.chat.id, "Вы вернулись в главное меню",
                                   reply_markup=nav.mainMenu)
        else:
            if state == "buy_case" and message.text != "Выбери кейс, который хочешь купить":
                case_name = message.text
                con = sqlite3.connect("database.db")
                cur = con.cursor()
                price = int(str(cur.execute('SELECT price FROM cases WHERE name = ?', (case_name,)).fetchone()).strip("(),"))
                user_balance = int(await give_balance(message.from_user.username))
                if price > user_balance:
                    await bot.send_message(message.chat.id, "Недостаточно средств",
                                           reply_markup=nav.mainMenu)
                    state = start
                else:
                    cur.execute('UPDATE users SET balance = ? WHERE username = ?', (user_balance - price, message.from_user.username,))
                    con.commit()
                    await new_item(message.from_user.username)
                    await bot.send_message(message.chat.id, "Покупка успешна",
                                           reply_markup=nav.mainMenu)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
