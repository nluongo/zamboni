import requests

r = requests.get('https://api-web.nhle.com/v1/season/20232024')
info_json = r.json()
print(info_json)
