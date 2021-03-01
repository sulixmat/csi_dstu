from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import structs, questions



def select_struct_keyboard(structs = structs, callback = None) -> InlineKeyboardMarkup:
    row = []
    keyboard = InlineKeyboardMarkup()
    for item in structs:
        button = InlineKeyboardButton(text=item, callback_data='CSI:{}:{}'.format(callback,item))
        keyboard.add(button)
    return keyboard



def answers_keyboard(question_num: int) -> InlineKeyboardMarkup:
    row = []
    keyboard = InlineKeyboardMarkup()
    
    mark = 'q' + str(question_num)
    rateing = len(questions[mark]['answers'])
    for item in questions[mark]['answers']:
        button = InlineKeyboardButton(text=item, callback_data='CSI:{}:{}:{}'.format(mark,item,rateing))
        rateing -= 1
        keyboard.add(button)
    return keyboard


def end_form_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Отправить отзыв!',callback_data='CSI:END')
    keyboard.add(button)
    return keyboard