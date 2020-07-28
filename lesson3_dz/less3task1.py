# """
# 1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать
# функцию, записывающую собранные вакансии в созданную БД
# 2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной
# платой больше введенной суммы. Поиск по двум полям (мин и макс зарплату)
# 3) Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта
# """


from pymongo import MongoClient
from pprint import pprint
import json


def add_to_mongo(data):
    client = MongoClient("127.0.0.1", 27017)
    db = client["vacancies_db"]
    vacancies = db.vacancies

    links = set()
    counter = 0
    for vacancy in vacancies.find({}):
        links.add(vacancy["link"])

    for vacancy in data:
        if vacancy["link"] not in links:
            vacancies.insert_one(vacancy)
            counter += 1
            links.add(vacancy["link"])
    print(f"Добавлено {counter} записей")


def vacancies_with_salary_mte(salary):
    client = MongoClient("127.0.0.1", 27017)
    db = client["vacancies_db"]
    vacancies = db.vacancies
    for vacancy in vacancies.find(
        {"$or": [{"salary_from": {"$gte": salary}}, {"salary_from": {"$gte": salary}}]}
    ):
        print(vacancy)


def clear_db(name):
    client = MongoClient("127.0.0.1", 27017)
    client.drop_database(name)
    print(f"Database {name} deleted")


if __name__ == "__main__":

    # with open("/lesson3_dz/vacancies.json", "r") as f:
    with open("vacancies.json", "r") as f:
        data = json.load(f)

    # clear_db("vacancies_db")
    add_to_mongo(data)
    salary = 40000
    vacancies_with_salary_mte(salary)


