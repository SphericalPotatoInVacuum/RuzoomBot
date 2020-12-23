def nearest_lesson_to_str(nearest_lesson: dict) -> str:
    """Returns a string containing the output of
       the closest lesson for today and tomorrow for
       student/group(defined by id_type) with id user_id."""
     if len(nearest_lesson) == 0:
        return 'Сегодня и завтра больше пар нет, можете отдыхать :)'

    response = f'Дисциплина: {nearest_lesson["discipline"]}\n' \
               f'Преподаватель: {nearest_lesson["lecturer"]}\n'\
               f'Тип занятия: {nearest_lesson["kindOfWork"]}\n' \
               f'День недели: {nearest_lesson["dayOfWeekString"]}\n' \
               f'Начало: {nearest_lesson["beginLesson"]}'
    
    if nearest_lesson['url1'] != '':
        response += f'\nСсылка: {nearest_lesson["url1"]}'

    if nearest_lesson['auditorium'].upper().find('ONLINE') != -1:
        response += f'\nАудитория: {nearest_lesson["auditorium"]}'

    return response


def transfrom_id_type(id_type: string) -> string:
    """Changes the id_type format to the format that
       ruz_api requires or raises the exception."""
    if id_type == 'GroupId':
        return 'group'
    if id_type == 'StudentId':
        return 'student'
    raise ValueError('Unknown type')
