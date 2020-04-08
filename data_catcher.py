import requests
import datetime
from config import ID1, ID2
import logging


def get_nearest_lesson():
    date_first = datetime.date.today()
    date_second = date_first + datetime.timedelta(days=1)
    now = datetime.datetime.now()

    r = requests.get(f'https://ruz.hse.ru/api/schedule/student/{ID1}?start={date_first.strftime("%Y.%m.%d")}'
                     f'&finish={date_second.strftime("%Y.%m.%d")}&lng=1')
    classes = r.json()

    for cls in classes:
        beginLesson = datetime.datetime.strptime(f'{cls["date"]} {cls["beginLesson"]}', '%Y.%m.%d %H:%M')

        if now <= beginLesson:
            return f'Дисциплина: {cls["discipline"]}\n' \
                   f'День недели: {cls["dayOfWeekString"]}\n' \
                   f'Начало: {cls["beginLesson"]}\n' \
                   f'Ссылка: {cls["url1"]}'

    return 'Пар нет - иди спать!1!1!!!1!'
