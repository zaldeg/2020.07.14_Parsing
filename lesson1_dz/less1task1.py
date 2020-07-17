import requests
from pprint import pprint
import json


username = "zaldeg"

response = requests.get(f"https://api.github.com/users/{username}/repos")
data = response.json()
with open(f"{username}_repos.json", "w") as f:
    json.dump(data, f)
print("Название репозиториев:")
for i in data:
    print(i["full_name"])

