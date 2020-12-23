import arrow
from config import TZ
import requests
from utils import transfrom_id_type

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


def get_names(name, name_type):
    r = requests.get(
        f'https://ruz.hse.ru/api/search?term={name}&type={name_type}'
    )
    names = r.json()
    return names
