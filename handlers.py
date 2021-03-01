import aiogram.utils.markdown as md
from aiogram import Bot, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ParseMode
from aiogram.utils import executor

from keyboards import *
from main import bot, dp, storage
from filters import Button_call_back
from config import questions, q_answers
from states import EndForm
import dbworker
from .statistic import calculate_the_average_score_by_struct


@dp.message_handler(commands=['start'])
async def cmd_start(msg: types.Message):
    print(msg)
    chat_id = msg.chat.id
    await bot.send_message(
        chat_id=chat_id,
        text='Здравствуйте! С помощью данного бота вы можете оценить качество предоставляемых ' \
            'услуг подразделений университета и направить отзыв или предложение.' \
            '\n\nВыберите подразделение, которое хотите оценить!',
        reply_markup=select_struct_keyboard(callback='START'))


@dp.callback_query_handler(Button_call_back('CSI:START'))
async def csi_q1(call: types.CallbackQuery):
    struct = call.data.split(':')[2]
    chat_id = call.message.chat.id
    q_answers[chat_id] = {}
    q_answers[chat_id]['struct'] = struct
    await bot.send_message(
        chat_id=chat_id,
        text=questions['q1']['q'],
        reply_markup=answers_keyboard(1))


@dp.callback_query_handler(Button_call_back('CSI:q'))
async def csi_q(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    mark, answer, rateing = call.data.split(':')[1:4]

    q_num = int(mark[1])
    q_num_mark = 'q{}_answer'.format(q_num)
    q_answers[chat_id][q_num_mark] = rateing

    if q_num < 5:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=questions['q{}'.format(str(q_num + 1))]['q'],
            reply_markup=answers_keyboard(q_num + 1),
            parse_mode=ParseMode.MARKDOWN
        )

    else:
        await csi_pre_end(call)


@dp.callback_query_handler(Button_call_back('CSI:q5'))
async def csi_pre_end(call: types.CallbackQuery):
    chat_id = call.message.chat.id

    await bot.send_message(
        chat_id=chat_id,
        text='Напишите отзыв или нажмите кнопку "Отправить отзыв", чтобы завершить опрос!',
        reply_markup=end_form_keyboard())
    await EndForm.end.set()


@dp.callback_query_handler(Button_call_back('CSI:END'), state=EndForm.end)
async def csi_end(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    q_answers[chat_id]['q6_answer'] = None

    dbworker.insert_form(
        q_answers[chat_id]['q1_answer'],
        q_answers[chat_id]['q2_answer'],
        q_answers[chat_id]['q3_answer'],
        q_answers[chat_id]['q4_answer'],
        q_answers[chat_id]['q5_answer'],
        q_answers[chat_id]['q6_answer'],
        q_answers[chat_id]['struct'],
    )

    dbworker.update_mean(q_answers[chat_id]['struct'])

    await bot.send_message(
        chat_id=chat_id,
        text='Спасибо за ваш отзыв!'
    )
    await state.finish()


@dp.message_handler(state=EndForm.end)
async def csi_end(msg: types.Message, state: FSMContext):
    chat_id = msg.chat.id
    q_answers[chat_id]['q6_answer'] = msg.text

    dbworker.insert_form(
        q_answers[chat_id]['q1_answer'],
        q_answers[chat_id]['q2_answer'],
        q_answers[chat_id]['q3_answer'],
        q_answers[chat_id]['q4_answer'],
        q_answers[chat_id]['q5_answer'],
        q_answers[chat_id]['q6_answer'],
        q_answers[chat_id]['struct'],
    )

    dbworker.update_mean(q_answers[chat_id]['struct'])

    await bot.send_message(
        chat_id=chat_id,
        text='Спасибо за ваш отзыв!'
    )
    await state.finish()


@dp.message_handler(commands='statistic')
async def select_struct_to_get_stats(message: types.Message):
    chat_id = message.chat.id

    await bot.send_message(
        chat_id=chat_id,
        text='Статистику какого подразделения вам показать?',
        reply_markup=select_struct_keyboard(callback='GETSTATS'))


@dp.callback_query_handler(Button_call_back('CSI:GETSTATS'))
async def get_stats(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    struct = call.data.split(':')[2]


    struct_statistic = dbworker.get_all_form_by_struct(struct)
    respondents_count = dbworker.respondents_count_by_struct(struct)
    q1, q2, q3, q4, q5 = calculate_the_average_score_by_struct(struct_statistic)

    respondents_count = '*Респондентов* - {}'.format(respondents_count)

    q1 = '*Качество обслуживания* - {} из {}'.format(int(q1), len(questions['q1']['answers']))
    q2 = '*Удовлетворенность работой* - {} из {}'.format(int(q2), len(questions['q2']['answers']))
    q3 = '*Активность сотрудников* - {} из {}'.format(int(q3), len(questions['q3']['answers']))
    q4 = '*Скорость обслуживания* - {} из {}'.format(int(q4), len(questions['q4']['answers']))
    q5 = '*Коэффициент рекомендации* - {} из {}'.format(int(q5), len(questions['q5']['answers']))
    await bot.send_message(
        chat_id=chat_id,
        text='\n\n'.join((respondents_count, q1, q2, q3, q4, q5)),
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(commands=['help'])
async def cmd_not_exist(message: types.Message):
    chat_id = message.chat.id

    await bot.send_message(
        chat_id=chat_id,
        text='Мои команды:\n/start - Оставить отзыв\n/statistic - посмотреть статистику')


@dp.message_handler()
async def cmd_not_exist(message: types.Message):
    chat_id = message.chat.id

    await bot.send_message(chat_id=chat_id, text='Для просмотра всех команд напишите /help')
