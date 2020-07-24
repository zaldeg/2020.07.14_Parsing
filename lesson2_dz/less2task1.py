"""
1) Необходимо собрать информацию о вакансиях на вводимую должность 
(используем input или через аргументы) с сайта superjob.ru и hh.ru.
Приложение должно анализировать несколько страниц сайта(также вводим через input или аргументы). 
Получившийся список должен содержать в себе минимум:

*Наименование вакансии
*Предлагаемую зарплату (отдельно мин. и отдельно макс. и отдельно валюта)
*Ссылку на саму вакансию        
*Сайт откуда собрана вакансия
По своему желанию можно добавить еще работодателя и расположение. Данная структура 
должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с 
помощью dataFrame через pandas.
"""

from bs4 import BeautifulSoup
import requests
from pprint import pprint
import re
import json


def salary_parsing(vacancy_salary):
    """
    полученную зарплату при помощи парсинга, превращаем в валюту, минимальную и максимальную зарплату.
    рабтает независимо от сайта, hh.ru или superjob.ru
    """
    if vacancy_salary:
        vacancy_salary = vacancy_salary.getText()
        # s = re.findall(r"(\d+\s?\d+)", vacancy_salary)
        s = re.findall(r"([\d\s]+)", vacancy_salary)
        if vacancy_salary.startswith("По"):
            vacancy_salary_from = None
            vacancy_salary_to = None
            vacancy_salary_currency = None
        elif vacancy_salary.startswith("от"):
            vacancy_salary_from = int("".join(s[0].split()))
            vacancy_salary_to = None
        elif vacancy_salary.startswith("до"):
            vacancy_salary_to = int("".join(s[0].split()))
            vacancy_salary_from = None
        else:
            vacancy_salary_from = int("".join(s[0].split()))
            if len(s) != 1:
                vacancy_salary_to = int("".join(s[1].split()))
            else:
                vacancy_salary_to = int("".join(s[0].split()))
        vacancy_salary_currency = vacancy_salary.split()[-1]
        if vacancy_salary_currency.endswith("месяц"):
            vacancy_salary_currency = vacancy_salary_currency[:-6]
    else:
        vacancy_salary_from = None
        vacancy_salary_to = None
        vacancy_salary_currency = None
    return vacancy_salary_from, vacancy_salary_to, vacancy_salary_currency


def making_result(vacancy_name, vacancy_link, vacancy_site, vacancy_salary):
    """
    функция добавляет результаты парсинга в общую структуру.
    """
    global result
    global index
    vs_from, vs_to, vs_currency = salary_parsing(vacancy_salary)
    info = {
        "index": index,
        "name": vacancy_name,
        "link": vacancy_link,
        "site": vacancy_site,
        "salary_from": vs_from,
        "salary_currency": vs_currency,
        "salary_to": vs_to,
    }
    result.append(info)
    index += 1


def hh_search(vacancy, number_of_pages=1):
    """
    парсим HH.ru
    """
    for i in range(number_of_pages):
        url = "https://spb.hh.ru/search/vacancy"
        params = {
            "L_save_area": "true",
            "clusters": "true",
            "enable_snippets": "true",
            "search_field": "name",
            "text": vacancy,
            "showClusters": "true",
            "page": i,
        }
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
        response = requests.get(url, params=params, headers={"User-Agent": user_agent})
        print(response)

        soup = BeautifulSoup(response.text, "lxml")

        vacancy_info = soup.find_all(
            "div",
            attrs={"class": "vacancy-serp-item__row vacancy-serp-item__row_header"},
        )
        vacancy_site = "hh.ru"

        for temp_info in vacancy_info:
            vacancy_link = temp_info.find(
                "a", attrs={"class": "bloko-link HH-LinkModifier"}
            )["href"]
            vacancy_name = temp_info.find(
                "a", attrs={"class": "bloko-link HH-LinkModifier"}
            ).getText()
            vacancy_salary = temp_info.find(
                "span", attrs={"data-qa": "vacancy-serp__vacancy-compensation"}
            )
            making_result(vacancy_name, vacancy_link, vacancy_site, vacancy_salary)
        if soup.find(text="дальше") is None:
            print(f"Только {i + 1} страниц с вакансиями на hh.ru")
            break


def superjob_search(vacancy, number_of_pages=1):
    """
    парсим superjobs
    """
    for i in range(number_of_pages):
        url = "http://www.superjob.ru/vacancy/search/?"
        params = {"keywords": vacancy, "page": i}
        user_agent = "Chrome/84.0.4147.89"
        response = requests.get(url, params=params, headers={"User-Agent": user_agent})
        print(response)
        soup = BeautifulSoup(response.text, "lxml")
        vacancy_info = soup.find_all("div", attrs={"class": "jNMYr"})
        for temp_info in vacancy_info:
            vacancy_name = temp_info.find("a", {"class": "icMQ_"}).getText()
            vacancy_link = (
                "http://superjob.ru" + temp_info.find("a", {"class": "icMQ_"})["href"]
            )
            vacancy_salary = temp_info.find(
                "span",
                {"class": "_3mfro"}
                # "span", {"class": "_3mfro _2Wp8I PlM3e _2JVkc _2VHxz"}
            )
            vacancy_site = "superjob.ru"
            making_result(vacancy_name, vacancy_link, vacancy_site, vacancy_salary)
        if soup.find(text="Дальше") is None:
            print(f"Только {i + 1} страниц с вакансиями на superjobs.ru")
            break


if __name__ == "__main__":

    vacancy = "уролог"
    number_of_pages = 2
    result = []
    index = 0

    hh_search(vacancy, number_of_pages)
    superjob_search(vacancy, number_of_pages)
    pprint(result)
    print(len(result))

    with open("vacancies.json", "w") as f:
        json.dump(result, f)

