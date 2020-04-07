import requests

r = requests.get('https://ruz.hse.ru/api/schedule/student/202454?start=2020.04.13&finish=2020.04.19&lng=1')
print(r.json()[2]['beginLesson'])
print(r.json()[2]['endLesson'])
