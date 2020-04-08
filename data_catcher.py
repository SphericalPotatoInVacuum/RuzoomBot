import requests
import arrow
from config import ID1, ID2, TZ
import logging


def get_nearest_lesson():
    now = arrow.now(TZ)
    date_first = now.date()
    date_second = now.shift(days=+1).date()

    r = requests.get(f'https://ruz.hse.ru/api/schedule/student/{ID1}?start={date_first.strftime("%Y.%m.%d")}'
                     f'&finish={date_second.strftime("%Y.%m.%d")}&lng=1')
    classes = r.json()

    for cls in classes:
        beginLesson = arrow.get(f'{cls["date"]} {cls["beginLesson"]}', 'YYYY.M.D HH:mm').replace(tzinfo=TZ)

        if now <= beginLesson:
            return f'Дисциплина: {cls["discipline"]}\n' \
                   f'День недели: {cls["dayOfWeekString"]}\n' \
                   f'Начало: {cls["beginLesson"]}\n' \
                   f'Ссылка: {cls["url1"]}'

    return 'Пар нет - иди спать!1!1!!!1!'
