import requests
import json
from zamboni import DBConnector

connector = DBConnector('zamboni.db')
connector.connect_db()
connector.close()

