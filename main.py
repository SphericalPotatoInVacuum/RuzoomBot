import logging
import os
import threading
import json

import arrow
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, parsemode, ForceReply

from config import TOKEN, TIMETABLE, TZ
from data_catcher import get_nearest_lesson, print_nearest_lesson, get_students, get_groups

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

chat_ids = dict()

with open('subscribed_chats.json', 'r') as ids_file:
    data = json.load(ids_file)
chat_ids = data


def start_help(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id, text='Вы ввели help или start)0))0)))')


def subscribe_chat(update, context):
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Расписание группы',
                                                         callback_data='Группа')],
                                   [InlineKeyboardButton(text='Индивидуальное расписание',
                                                         callback_data='ФИО')]])
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Получать индивидуальное расписание или расписание группы?",
        reply_markup=markup)
    return 'Вопрос'


def subscribe(id, chat_id):
    user_ids = chat_ids.get(chat_id, [])
    if not id in user_ids:
        chat_ids[chat_id] = user_ids + [id]
    with open('subscribed_chats.json', 'w') as ids_file:
        json.dump(list(chat_ids), ids_file)


def send_nearest_lesson(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id, text=print_nearest_lesson())


def button(update, context):
    query = update.callback_query.data.split()
    if query[0] == 'Группа':
        updater.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Введите номер группы в формате БПМИ195')
        return 'Группа'
    elif query[0] == 'ФИО':
        updater.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Введите ФИО')
        return 'ФИО'
    elif query[0] == 'GroupID' or query[0] == 'StudentID':
        if query[1] != '0':
            subscribe(query[1], query[2])
            updater.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Ееее вы подписались!',
            )
        else:
            updater.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Пашёл нахер козёл',
            )


def echo_all(update, context):
    update.message.reply_text(update.message.text + '\nА ещё ты пидор')


def credentialts(update, context):
    student = update.message.text
    students = get_students(student)
    markup = []
    for student in students:
        markup.append([InlineKeyboardButton(
            text=f'{student["label"]}, {student["description"]}',
            callback_data=f'StudentID {student["id"]} {update.message.chat_id}'
        )])
    markup.append([InlineKeyboardButton(
        text='Меня тут нет!',
        callback_data='StudentID 0'
    )])
    markup = InlineKeyboardMarkup(markup)
    update.message.reply_text(
        text="Следующие студенты удовлетворяют условиям поиска, выберите себя:",
        reply_markup=markup
    )

    return 'Choose'


def group(update, context):
    group = update.message.text
    groups = get_groups(group)
    markup = []
    for group in groups:
        markup.append([InlineKeyboardButton(
            text=f'{group["label"]}, {group["description"]}',
            callback_data=f'GroupID {group["id"]} {update.message.chat_id}'
        )])
    markup.append([InlineKeyboardButton(
        text='Моей группы тут нет!',
        callback_data='GroupID 0'
    )])
    markup = InlineKeyboardMarkup(markup)
    update.message.reply_text(
        text="Следующие группы удовлетворяют условиям поиска, выберите свою:",
        reply_markup=markup
    )

    return 'Choose'


def check_timetable():
    timeout = 5

    now = arrow.now(TZ)
    date = now.date()
    for time in TIMETABLE:
        if now.shift(minutes=+10) > arrow.get(f'{date} {time}').replace(tzinfo=TZ) > now:
            nearest_lesson = get_nearest_lesson()
            if now.shift(minutes=+10) >= arrow.get(f'{nearest_lesson["date"]} '
                                                   f'{nearest_lesson["beginLesson"]}').replace(tzinfo=TZ) > now:
                for chat_id in chat_ids:
                    updater.bot.send_message(
                        chat_id=chat_id, text=print_nearest_lesson())
                timeout = 700

    threading.Timer(timeout, check_timetable).start()


def cancel(update, context):
    update.message.reply_text('Жаль что не смог вам помочь',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


start_handler = CommandHandler('start', start_help)
help_handler = CommandHandler('help', start_help)
subscribe_handler = CommandHandler('subscribe', subscribe_chat)
getnext_handler = CommandHandler('getnext', send_nearest_lesson)
echo_handler = MessageHandler(filters=Filters.all, callback=echo_all)
callback_handler = CallbackQueryHandler(button)

conv_handler = ConversationHandler(
    entry_points=[subscribe_handler],
    states={
        'Вопрос': [callback_handler],
        'Группа': [MessageHandler(filters=Filters.text, callback=group)],
        'ФИО': [MessageHandler(filters=Filters.text, callback=credentialts)],
        'Choose': [callback_handler]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
# dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(getnext_handler)
dispatcher.add_handler(conv_handler)
dispatcher.add_handler(echo_handler)

check_timetable()
PORT = int(os.environ.get('PORT', '8443'))
updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook('https://ruzbot.herokuapp.com/' + TOKEN)
updater.idle()
