import dateutil
import telebot
import os
from flask import Flask, request
from config import TOKEN, TIMETABLE, TZ
from data_catcher import get_nearest_lesson
import threading
import datetime
import arrow
from dateutil import tz

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

chat_ids = set()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 'Вы ввели help или start)0))0)))')


@bot.message_handler(commands=['subscribe'])
def subscribe_chat(message):
    chat_ids.add(message.chat.id)
    bot.send_message(message.chat.id, 'Теперь вы подписаны)0))00)))0)')


@bot.message_handler(commands=['getnext'])
def send_nearest_lesson(message):
    bot.send_message(message.chat.id, get_nearest_lesson())


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://ruzbot.herokuapp.com/' + TOKEN)
    return 'Hello world!', 200


def check_timetable():
    timeout = 5

    now = arrow.now(TZ)
    date = now.date()
    for time in TIMETABLE:
        if now.shift(minutes=+10) > arrow.get(f'{date} {time}', 'YYYY-M-D HH:mm').replace(tzinfo=TZ) > now:
            cur = get_nearest_lesson()
            cur_mes = f'Дисциплина: {cur["discipline"]}\n \
                   День недели: {cur["dayOfWeekString"]}\n \
                   Начало: {cur["beginLesson"]}\n \
                   Ссылка: {cur["url1"]}'
            if len(cur) == 0:
                cur_mes = 'Пар нет - иди спать!1!1!!!1!'
            if now.shift(minutes=+10) > arrow.get(f'{date} {cur["Начало"]}', 'YYYY-M-D HH:mm').replace(tzinfo=TZ) > now:
                for chat_id in chat_ids:
                    bot.send_message(chat_id, cur_mes)
                timeout = 700

    threading.Timer(timeout, check_timetable).start()


check_timetable()
print(__name__ == '__main__')
if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
