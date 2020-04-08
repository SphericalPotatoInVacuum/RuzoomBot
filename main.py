import telebot
import os
from flask import Flask, request
from config import TOKEN, TIMETABLE
from data_catcher import get_nearest_lesson
import threading
import datetime

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

chat_ids = []


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 'Вы ввели help или start)0))0)))')


@bot.message_handler(commands=['subscribe'])
def subscribe_chat(message):
    chat_ids.append(message.chat.id)
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
    threading.Timer(5, check_timetable).start()

    date = datetime.date.today()
    now = datetime.datetime.now()

    for time in TIMETABLE:
        if now - datetime.datetime.strptime(f'{date} {time}', '%Y.%m.%d %H:%M')\
                + datetime.timedelta(minutes=10) < datetime.timedelta(seconds=5):
            for chat_id in chat_ids:
                bot.send_message(chat_id, get_nearest_lesson())


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    check_timetable()
