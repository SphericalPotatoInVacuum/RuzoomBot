import requests
import arrow
from config import ID1, ID2, TZ
import logging


def get_nearest_lesson(user_id=ID1):
    now = arrow.now(TZ)
    date_first = now.date()
    date_second = now.shift(days=+1).date()

    r = requests.get(f'https://ruz.hse.ru/api/schedule/student/{user_id}?start={date_first.strftime("%Y.%m.%d")}'
                     f'&finish={date_second.strftime("%Y.%m.%d")}&lng=1')
    classes = r.json()

    for cls in classes:
        beginLesson = arrow.get(
            f'{cls["date"]} {cls["beginLesson"]}').replace(tzinfo=TZ)

        if now <= beginLesson:
            return cls

    return {}


def print_nearest_lesson(user_id=ID1):
    nearest_lesson = get_nearest_lesson(user_id)
    if len(nearest_lesson) == 0:
        return 'Пар нет - иди спать!1!1!!!1!'
    return f'Дисциплина: {nearest_lesson["discipline"]}\n' \
           f'Тип заняти: {nearest_lesson["kindOfWork"]}\n' \
           f'День недели: {nearest_lesson["dayOfWeekString"]}\n' \
           f'Начало: {nearest_lesson["beginLesson"]}\n' \
           f'Ссылка: {nearest_lesson["url1"]}'


def get_students(student):
    r = requests.get(
        f'https://ruz.hse.ru/api/search?term={student}&type=student'
    )
    students = r.json()
    return students


def get_groups(group):
    r = requests.get(
        f'https://ruz.hse.ru/api/search?term={group}&type=group'
    )
    groups = r.json()
    return groups
