'''2) Написать программу, которая собирает «Хиты продаж» с сайта техники 
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
    db = client["hits_db"]
    hits = db.hits

    link = set()
    counter = 0
    for hit in hits.find({}):
        link.add(hit["link"])

    for hit in data:
        if hit["link"] not in link:
            hits.insert_one(hit)
            counter += 1
            link.add(hit["link"])
    print(f"Добавлено {counter} записей")




chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)
url = 'https://www.mvideo.ru/'
driver.get('https://www.mvideo.ru/')
sleep(10)
actions = ActionChains(driver)
button = driver.find_elements_by_xpath(
    "//a[@class='next-btn sel-hits-button-next']"
)

hits= []
actions.move_to_element(button[2]).perform()
for i in range(4):
    offers = driver.find_elements_by_xpath("//a[@class='sel-product-tile-title']")[4:8]
    for offer in offers:
        hits.append(
            {
            'product': offer.text,
            'link': url[:-1] + offer.get_attribute('href')
            }
        )
    actions.click().perform()
    sleep(10)
    
pprint(hits)
add_to_mongo(hits)

driver.close()