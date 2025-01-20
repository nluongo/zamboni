import requests

class APICaller():
    """ Class for querying the NHL API """
    url_base = 'https://api-web.nhle.com/v1/'

    def __init__(self, record_type):
        """
        Set URL variables and record type

        :param record_type: The type of record to be requested
        """
        self.url_base = APICaller.url_base
        self.url = self.url_base
        self.record_type = record_type
        self.set_url_template(record_type)

    def set_url_template(self, record_type):
        """
        Append the relevant string to the base URL based on record type 

        :param record_type: The type of record to be requested
        """
        if record_type == 'standings':
            self.url += 'standings/now' 
        elif record_type == 'player':
            self.url += 'player/{}/landing' 
        elif record_type == 'game':
            self.url += 'schedule/{}'
        elif record_type == 'roster':
            self.url += 'roster/{}/{}{}'
        else:
            print(f'ERROR: no endpoint associated with the record type {record_type}')

    def query(self, record_ids, throw_error=True):
        """
        Submit query to NHL API

        :param record_ids: List of values to fill to URL
        :param throw_error: Flag to throw error if query returns nothing
        :returns: JSON of API output
        """
        url = self.url.format(*record_ids)
        try:
            api_out = requests.get(url)
        except requests.exceptions.JSONDecodeError:
            if throw_error:
                raise ValueError(f'Failed to query {url}')
            else:
                api_out = None
        json = api_out.json() if api_out else None
        return json    
        
