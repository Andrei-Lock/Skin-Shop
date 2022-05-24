from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ------ Main Menu ------
btnCreateNote = KeyboardButton('Кейсы')
btnOpenNote = KeyboardButton('Баланс')
btn_give_balance = KeyboardButton('Халява')
btn_inventory = KeyboardButton('Инвентарь')
btnMain = KeyboardButton('⬅ Главное меню')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4).add(btnCreateNote, btnOpenNote, btn_inventory,
                                                                      btn_give_balance, btnMain)
