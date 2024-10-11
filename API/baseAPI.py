import os


class Base:
    def __init__(self):
        self.headers = {'X-Auth-Token': os.getenv('API_TOKEN')}
