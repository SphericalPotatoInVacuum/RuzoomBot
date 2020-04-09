import logging
import os
import threading
import json

import arrow
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, parsemode

from config import TOKEN, TIMETABLE, TZ
from data_catcher import get_nearest_lesson, print_nearest_lesson

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

chat_ids = set()

with open('subscribed_chats.json', 'r') as ids_file:
    data = json.load(ids_file)
chat_ids = set(data)


def start_help(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Вы ввели help или start)0))0)))')


def subscribe_chat(update, context):
    chat_ids.add(update.message.chat_id)
    with open("subscribed_chats.json", 'w') as ids_file:
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
    context.bot.send_message(chat_id=update.message.chat_id, text=print_nearest_lesson())


def echo_all(update, context):
    update.message.reply_text(update.message.text + '\nА ещё ты пидор')


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
                    updater.bot.send_message(chat_id=chat_id, text=print_nearest_lesson())
                timeout = 700

    threading.Timer(timeout, check_timetable).start()

start_handler = CommandHandler('start', start_help)
help_handler = CommandHandler('help', start_help)
subscribe_handler = CommandHandler('subscribe', subscribe_chat)
getnext_handler = CommandHandler('getnext', send_nearest_lesson)
echo_handler = MessageHandler(filters=Filters.all, callback=echo_all)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(getnext_handler)
dispatcher.add_handler(echo_handler)

check_timetable()
PORT = int(os.environ.get('PORT', '8443'))
updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook('https://ruzbot.herokuapp.com/' + TOKEN)
updater.idle()
