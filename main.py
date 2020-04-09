import logging
import os
import threading
import json

import arrow
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, parsemode, ForceReply

from config import TOKEN, TIMETABLE, TZ
from data_catcher import get_nearest_lesson, print_nearest_lesson, get_students

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

chat_ids = set()

with open('subscribed_chats.json', 'r') as ids_file:
    data = json.load(ids_file)
chat_ids = set(data)


def start_help(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id, text='Вы ввели help или start)0))0)))')


def subscribe_chat(update, context):
    chat_ids.add(update.message.chat_id)
    with open('subscribed_chats.json', 'w') as ids_file:
        json.dump(list(chat_ids), ids_file)

    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Расписание группы',
                                                         callback_data='Группа')],
                                   [InlineKeyboardButton(text='Индивидуальное расписание',
                                                         callback_data='ФИО')]])
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Получать индивидуальное расписание или расписание группы?",
        reply_markup=markup)


def send_nearest_lesson(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id, text=print_nearest_lesson())


def button(update, context):
    if update.callback_query.data == 'Группа':
        updater.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Введите номер группы в формате БПМИ195.',
            reply_markup=ForceReply)
    elif update.callback_query.data == 'ФИО':
        update.message.reply_text(
            chat_id=update.effective_chat.id,
            text='Введите ФИО.',
            reply_markup=ForceReply)


def echo_all(update, context):
    update.message.reply_text(update.message.text + '\nА ещё ты пидор')


def credentialts(update, context):
    student = update.message.text
    students = get_students(student)
    markup = []
    for student in students:
        markup.append([InlineKeyboardButton(
            text=f'{student["label"]}, {student["description"]}',
            callback_data=student['id']
        )])
    markup.append([InlineKeyboardButton(
        text='Меня тут нет!',
        callback_data='0'
    )])
    markup = InlineKeyboardMarkup(markup)
    update.message.reply_text(
        text="Следующие студенты удовлетворяют условиям поиска, выберите себя:",
        reply_markup=markup
    )

    return ConversationHandler.END


def group(update, context):
    group = update.message.text
    groups = get_students(student)
    markup = []
    for group in groups:
        markup.append([InlineKeyboardButton(
            text=f'{group["label"]}, {group["description"]}',
            callback_data=group['id']
        )])
    markup.append([InlineKeyboardButton(
        text='Моей группы тут нет!',
        callback_data='0'
    )])
    markup = InlineKeyboardMarkup(markup)
    update.message.reply_text(
        text="Следующие группы удовлетворяют условиям поиска, выберите свою:",
        reply_markup=markup
    )

    return ConversationHandler.END


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
subscriber_type_handler = CallbackQueryHandler(button)

conv_handler = ConversationHandler(
    entry_points=[subscriber_type_handler],
    states={
        'Группа': [MessageHandler(filters=Filters.text, callback=group)],
        'ФИО': [MessageHandler(filters=Filters.text, callback=credentialts)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(getnext_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(conv_handler)

check_timetable()
PORT = int(os.environ.get('PORT', '8443'))
updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook('https://ruzbot.herokuapp.com/' + TOKEN)
updater.idle()
