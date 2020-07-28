'''
1)Написать приложение, которое собирает основные новости с сайтов:
news.mail.ru, lenta.ru, yandex.ru/news
Для парсинга использовать xpath. Структура данных должна содержать:
* название источника,
* наименование новости,
* ссылку на новость,
* дата публикации

2)Сложить все новости в БД

'''


from pprint import pprint
import requests
from lxml import html
import datetime
from pymongo import MongoClient

def add_to_mongo(data):
    '''
    Добавляем наши документы в базу, если в базе уже есть такая новость(проверяем по линку),
    то новость не добавляется.
    '''
    client = MongoClient("127.0.0.1", 27017)
    db = client["top_news_db"]
    news = db.news
    counter = 0
    for document in data:
        if not news.find_one({'link': document['link']}):
            news.insert_one(document)
            counter += 1
    print(f"Добавлено {counter} записей")

def clear_db(name):
    '''
    удаление датабазы
    '''
    client = MongoClient("127.0.0.1", 27017)
    client.drop_database(name)
    print(f"Database {name} deleted")

def results_to_dict(news_titles, news_links, news_time, news_sources):
    '''
    Переводим наши собранные данные в структуру для монго
    '''
    result = []
    for i in  range(len(news_titles)):
        temp = {
            'title': news_titles[i],
            'link': news_links[i],
            'published_at': news_time[i],
            'soursce': news_sources[i]
        }
        result.append(temp)
    return result



def get_response(link):
    '''
    получаем результаты по запросу к серверу, если есть ошибка при получении, то выводим адрес с которым не срослось.
    '''
    try:
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        response = requests.get(link, headers=headers)
        print(response)
        return response
    except:
        print(f'Не получилось получить ответ от {link}')

def news_mail():
    '''
    собираем первых 11 новостей news.mail.ru
    '''
    def take_some_info(news_link):
        '''
        Заходим в каждую новость, что бы получить источник и дату написания новости. 
        '''
        news_sources = []
        news_time = []
        for link in news_link:
            news_response = get_response(link)
            news_dom = html.fromstring(news_response.text)
            news_time.append(news_dom.xpath("//span[@class='note']//@datetime"))
            news_sources.append(news_dom.xpath("//a[@class='link color_gray breadcrumbs__link']/@href"))
        return news_time, news_sources
        

    url = 'https://news.mail.ru'
    response = get_response(url)

    dom = html.fromstring(response.text)

    news_titles = dom.xpath("//div[@class='block']//li//text()")
    more_news_titles = dom.xpath("//span[@class='photo__title photo__title_new photo__title_new_hidden js-topnews__notification']//text()")
    news_titles.extend(more_news_titles[:3])

    for i in range(len(news_titles)):
        news_titles[i] = news_titles[i].replace('\xa0', ' ')

    news_links = dom.xpath("//div[@class='block']//li/a/@href")
    more_news_links = dom.xpath("//td/div/a/@href")
    news_links.extend(more_news_links[:3])
    for i, link in enumerate(news_links):
        if link.startswith('/'):
            news_links[i] = url + link
    
    news_time, news_sources = take_some_info(news_links)

    return results_to_dict(news_titles, news_links, news_time, news_sources)

    # pprint(news_links)
    # pprint(news_titles)
    # pprint(news_sources)
    # pprint(news_time)


def news_yandex():
    '''
    Собираем новости с яндекса, тут в общем нету блоков важных, на странице просто 65 новостей по разным категориям.
    Так что берем все.
    '''

    url = "https://yandex.ru/news"

    response = get_response(url)
    dom = html.fromstring(response.text)
    news_titles = dom.xpath("//h2[@class='story__title']/a/text()")
    news_links = dom.xpath("//h2[@class='story__title']/a/@href")
    for i in range(len(news_links)):
        news_links[i] = url + news_links[i][5:]
    source_and_time = dom.xpath("//div[@class='story__date']/text()")
    news_time = []
    news_sources= []
    for element in source_and_time:
        '''
        на яндексе просто пишется время публикации новости, если она вчерашняя то добавляется к ней что она вышла вчера.
        добавляем сегодняшнюю дату, или вчерашнюю если новость вчерашняя.
        '''
        
        if 'вчера' in element:
            news_sources.append(element[:-14])
            news_time.append(element[-5:] + " " + str(datetime.date.today() - datetime.timedelta(1)))
        else:
            news_sources.append(element[:-6])
            news_time.append(element[-5:] + " " + str(datetime.date.today()))

    return results_to_dict(news_titles, news_links, news_time, news_sources)
    # pprint(news_titles)
    # pprint(news_links)
    # pprint(news_sources)
    # pprint(news_time)

def news_lenta():
    '''
    парсим ленту, на ленте новости только с ленты, так что источник один.
    '''
    url = "https://lenta.ru/"

    response = get_response(url)
    dom = html.fromstring(response.text)
    news_titles = dom.xpath("//section[contains(@class, 'js-top-seven')]//a//@datetime/../../text()")
    for i in range(len(news_titles)):
        news_titles[i] = news_titles[i].replace('\xa0', ' ')
    news_links = dom.xpath("//section[contains(@class, 'js-top-seven')]//a//@datetime/../../@href")
    for i, link in enumerate(news_links):
        if link.startswith('/'):
            news_links[i] = url + link[1:]
    news_sources = ["lenta.ru" for i in range(10)]
    news_time = dom.xpath("//section[contains(@class, 'js-top-seven')]//a//@datetime")

    return results_to_dict(news_titles, news_links, news_time, news_sources)

    # pprint(news_titles)
    # pprint(news_links)
    # pprint(news_sources)
    # pprint(news_time)
    


    

if __name__ == "__main__":
    # clear_db('top_news_db')
    news_info = []
    news_info.extend(news_mail())
    news_info.extend(news_yandex())
    news_info.extend(news_lenta())
    add_to_mongo(news_info)

    
    # pprint(news_info)
