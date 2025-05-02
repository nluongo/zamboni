import requests

class APICaller():
    """ Class for querying the NHL API """
    url_base = 'https://api-web.nhle.com/v1/'

    def __init__(self):
        """
        Set URL variables and record type

        :param record_type: The type of record to be requested
        """
        self.url_base = APICaller.url_base
        self.url = None

    def set_url_template(self, record_type):
        """
        Append the relevant string to the base URL based on record type 

        :param record_type: The type of record to be requested
        """
        if record_type == 'standings':
            self.url = self.url_base + 'standings/{}' 
        elif record_type == 'player':
            self.url = self.url_base + 'player/{}/landing' 
        elif record_type == 'game':
            self.url = self.url_base + 'schedule/{}'
        elif record_type == 'roster':
            self.url = self.url_base + 'roster/{}/{}{}'
        else:
            print(f'ERROR: no endpoint associated with the record type {record_type}')

    def query(self, record_type=None, record_ids=[], throw_error=True):
        """
        Submit query to NHL API

        :param record_ids: List of values to fill to URL
        :param throw_error: Flag to throw error if query returns nothing
        :returns: JSON of API output
        """
        # If no record type given, then query with raw URL ending given
        if not record_type and not self.url:
            url = self.url_base + record_ids[0]
        elif not self.url:
            self.set_url_template(record_type)
            url = self.url.format(*record_ids)
        elif not record_type:
            url = self.url.format(*record_ids)
        try:
            api_out = requests.get(url)
            api_out.raise_for_status()  # Raise an HTTPError for bad responses
            json = api_out.json()
        except requests.exceptions.HTTPError as http_err:
            if throw_error:
                raise ValueError(f'HTTP error occurred: {http_err}') from http_err
            else:
                print(f'HTTP error occurred: {http_err}')
                json = None
        except requests.exceptions.ConnectionError as conn_err:
            if throw_error:
                raise ValueError(f'Connection error occurred: {conn_err}') from conn_err
            else:
                print(f'Connection error occurred: {conn_err}')
                json = None
        except requests.exceptions.Timeout as timeout_err:
            if throw_error:
                raise ValueError(f'Timeout error occurred: {timeout_err}') from timeout_err
            else:
                print(f'Timeout error occurred: {timeout_err}')
                json = None
        except requests.exceptions.RequestException as req_err:
            if throw_error:
                raise ValueError(f'An error occurred: {req_err}') from req_err
            else:
                print(f'An error occurred: {req_err}')
                json = None
        except ValueError as json_err:
            if throw_error:
                raise ValueError(f'JSON decode error: {json_err}') from json_err
            else:
                print(f'JSON decode error: {json_err}')
                json = None
        return json

