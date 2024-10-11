import os


class Base:
    def __init__(self):
        self.headers = {'X-Auth-Token': os.getenv('API_TOKEN'),
                        'Content-Type': 'application/json',
                        'accept': 'application/json'}
        self.base_path = 'https://games-test.datsteam.dev'
