from pymongo import MongoClient


client = MongoClient('localhost', 27017)
mongo_base = client.instagram_users
users = mongo_base['insta']
relations = mongo_base['relations']

search = 'orlovgorskii'
user_id = 5547722020


def followers(search):
    counter = 0
    if isinstance(search,str):
        search = users.find({'username': f'{search}'})[0].get("_id")
    for user_id in relations.find({'follower': search}):
        for user in users.find({'_id': user_id.get('followed')}):
            print(user)
            # print(counter)
            # counter +=1


followers(search)