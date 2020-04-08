import requests
import datetime
from config import ID1, ID2
import logging


def get_nearest_lesson():
    logging.info('Зашли в get_nearest_lesson.')

    date = datetime.date.today().strftime('%Y.%m.%d')
    now = datetime.datetime.now()

    r = requests.get(f'https://ruz.hse.ru/api/schedule/student/{ID1}?start={date}&finish={date}&lng=1')
    classes = r.json()

    for cls in classes:
        beginLesson = datetime.time.strptime(cls['beginLesson'], '%H:%M')

        if now <= beginLesson:
            return cls['discipline']
    return 'Пар нет - иди спать!1!1!!!1!'
