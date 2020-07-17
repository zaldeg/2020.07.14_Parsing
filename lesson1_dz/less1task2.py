import requests
from pprint import pprint
import json

key = "AIzaSyA75TV3M5C61MPSW9r9KH04CTR9QKuCMNk"
params = {
    "key": key,
    "channelId": "UC-lHJZR3Gqxm24_Vd_AJ5Yw",
    "part": "snippet,id",
    "order": "date",
}

url = "https://www.googleapis.com/youtube/v3/search?"

response = requests.get(url, params)
resp = response.json()
with open(f"answer.json", "w") as f:
    json.dump(resp, f)
# print(1)
print("Названия последних пяти видео на канал PewDiePi:")
for i in resp["items"]:
    print(i["snippet"]["title"])
