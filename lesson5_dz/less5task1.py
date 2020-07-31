'''
1) Написать программу, которая собирает входящие письма из своего 
или тестового почтового ящика и сложить данные о письмах в базу данных 
(от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172
2) Написать программу, которая собирает «Хиты продаж» с сайта техники 
mvideo и складывает данные в БД. Магазины можно выбрать свои. Главный 
критерий выбора: динамически загружаемые товары
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from pprint import pprint

def add_to_mongo(data):
    client = MongoClient("127.0.0.1", 27017)
    db = client["mails_db"]
    mails = db.mails

    texts = set()
    counter = 0
    for mail in mails.find({}):
        texts.add(mail["text"])

    for mail in data:
        if mail["text"] not in texts:
            mails.insert_one(mail)
            counter += 1
            texts.add(mail["text"])
    print(f"Добавлено {counter} записей")


chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://mail.ru/')
username = driver.find_element_by_name('login')
username.send_keys('study.ai_172@mail.ru')
username.send_keys(Keys.ENTER)
sleep(1)
password = driver.find_element_by_name('password')
password.send_keys('NextPassword172')
password.send_keys(Keys.ENTER)
sleep(3)

urls = set()

while True:
    actions = ActionChains(driver)
    letters = driver.find_elements_by_xpath("//div[@class='dataset__items']/a")
    if letters[-1].get_attribute('href') in urls:
        break
    sleep(0.5)
    for link in letters:
        url = link.get_attribute('href')
        urls.add(url)
    actions.move_to_element(letters[-1])
    actions.perform()
    # break
structure_for_db =[]
urls -= {None}
a = 1
for i in urls:
    driver.get(i)
    sleep(2)
    mail_from = driver.find_element_by_xpath("//span[@class='letter-contact']").get_attribute('title')
    mail_title = driver.find_element_by_class_name('thread__subject').text
    mail_date = driver.find_element_by_class_name('letter__date').text
    mail_text = driver.find_element_by_xpath("//div[@class='letter__body']").text
    structure_for_db.append(
        {
            'from': mail_from,
            'title': mail_title,
            'date': mail_date,
            'text': mail_text
        }
    )
    print(a)
    a += 1

add_to_mongo(structure_for_db)
driver.close()
