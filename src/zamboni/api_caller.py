import requests

class APICaller():
    url_base = 'https://api-web.nhle.com/v1/'

    def __init__(self, record_type):
        self.url_base = APICaller.url_base
        self.url = self.url_base
        self.record_type = record_type
        self.set_url_template(record_type)

    def set_url_template(self, record_type):
        if record_type == 'standings':
            self.url += 'standings/now' 
        elif record_type == 'player':
            self.url += 'player/{}/landing' 
        elif record_type == 'game':
            self.url += 'schedule/{}'

    def query(self, record_id, throw_error=True):
        url = self.url.format(record_id)
        try:
            api_out = requests.get(url)
        except:
            if throw_error:
                raise ValueError(f'Failed to query {url}')
            else:
                api_out = None
        json = api_out.json() if api_out else None
        return json    
        
