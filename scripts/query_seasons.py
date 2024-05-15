import requests

r = requests.get('https://api-web.nhle.com/v1/season')
print(r)
info_json = r.json()
print(info_json)
