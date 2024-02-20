import requests

class APICaller():
    url_base = 'https://api-web.nhle.com/v1/{}/{}'

    def __init__(self):
        pass

    def query(self, record_type, record_id):
        url = APICaller.url_base.format(record_type, record_id)
        api_out = requests.get(url)
        json = api_out.json()
        return json    
        
