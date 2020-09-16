import arrow
from config import TZ
import requests

def transfrom_id_type(id_type: string) -> string:
    """Changes the id_type format to the format that
       ruz_api requires or raises the exception."""
    if id_type == 'GroupId':
        return 'group'
    if id_type == 'StudentId':
        return 'student'
    raise ValueError('Unknown type')


def get_lessons_from_ruz(id_type: string, user_id: string,
                         start_search_date: arrow.Arrow,
                         finish_search_date: arrow.Arrow) -> list:
    """Return list of lessons of student/group(defined by id_type) with id user_id,
       wich will be holded from start_search_date to finish_search_date"""
    ruz_response =
    requests.get(
        f'https://ruz.hse.ru/api/schedule/{id_type}/{user_id}?'
        f'start={date_first.strftime("%Y.%m.%d")}'
        f'&finish={date_second.strftime("%Y.%m.%d")}&lng=1')
    return ruz_response.json()


def get_nearest_lesson(id_type: string, user_id: string) -> dict:
    """Returns the closest lesson for today and tomorrow
       for student/group(defined by id_type) with id user_id,
       or an empty lesson if there are no lessons."""
    current_moment = arrow.now(TZ)
    start_date = current_moment.date()
    finish_date = current_moment.shift(days=+1).date()

    id_type = transfrom_id_type(id_type) 
    users_classes = get_lessons_from_ruz(id_type, user_id,
                                         start_date, finish_date)

    for users_class in users_classes:
        lesson_start = arrow.get(
                      f'{users_class["date"]} {users_class["beginLesson"]}').replace(tzinfo=TZ)

        if current_moment <= lesson_start:
            return users_class
    return {}


def print_nearest_lesson(id_type, user_id=ID1):
    """Returns a string containing the output of
       the closest lesson for today and tomorrow for
       student/group(defined by id_type) with id user_id."""
    nearest_lesson = get_nearest_lesson(id_type, user_id)

    if len(nearest_lesson) == 0:
        return 'Сегодня и завтра больше пар нет, можете отдыхать :)'

    response = f'Дисциплина: {nearest_lesson["discipline"]}\n' \
               f'Преподаватель: {nearest_lesson["lecturer"]}\n'\
               f'Тип занятия: {nearest_lesson["kindOfWork"]}\n' \
               f'День недели: {nearest_lesson["dayOfWeekString"]}\n' \
               f'Начало: {nearest_lesson["beginLesson"]}'
    
    if (nearest_lesson['auditorium'].split(' ')[0].upper() != 'ONLINE'):
        response += f'\nАудитория: {nearest_lesson["auditorium"]}'
    else:
        response += f'\nСсылка: {nearest_lesson["url1"]}'

    return response


def get_names(name, name_type):
    r = requests.get(
        f'https://ruz.hse.ru/api/search?term={name}&type={name_type}'
    )
    names = r.json()
    return names
