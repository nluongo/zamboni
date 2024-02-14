import requests

r = requests.get('https://api-web.nhle.com/v1/schedule/now')
print(r.json())
