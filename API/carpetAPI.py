import json
import math
import os

from .baseAPI import Base
from .custom_exceptions import *
import requests


def find_carpet(res: list, id: str) -> dict | None:
    """
    Функция, для того, чтобы найти словарь с текущим ковром, так как в ответ на каждое дейтсиве присылается
    список сразу со всеми
    :param res: ответ от api по ключу transports
    :param id: id текущего ковра
    :return: dict с информацией по текущему ковру
    """
    for d in res:
        if d['id'] == id:
            return d


def update_attributes_decorator(func):
    """
    Декоратор, который обновляет поля ковра после действия с ним (соответственно всё, что меняет атрибуты
    ковра должно оборачиваться в этот декоратор). Работает с сырым ответом сервера
    :param func:
    :return: возвращает статы ковра
    :raise BadAnswer: если ответ от сервака не 200, то возникает эта ошибка. В консоль выводится полезная инфа
    прога не вылетает
    """
    async def wrapper(self, *args, **kwargs):
        try:
            response: requests.Response = await func(self, *args, **kwargs)
            if response.status_code != 200:
                raise BadAnswer
            data: dict = find_carpet(json.loads(response.text)['transports'], self.id)

            self.pos_x = data.get('x', self.pos_x)
            self.pos_y = data.get('y', self.pos_y)
            self.velocity = data.get('velocity', self.velocity)
            self.self_acceleration = data.get('selfAcceleration', self.self_acceleration)
            self.anomaly_acceleration = data.get('anomalyAcceleration', self.anomaly_acceleration)
            self.status = data.get('status', self.status)
            self.shield_left = data.get('shieldLeftMs', self.shield_left)
            self.attack_cd = data.get('attackCooldownMs', self.attack_cd)
            self.health = data.get('health', self.health)
            self.shield_cd = data.get('shieldCooldownMs', self.shield_cd)
            self.id = data.get('id', self.id)

            return data
        except BadAnswer as e:
            print(f'Ошибка в {func.__name__}\nStatus_code: {response.status_code}\nMessage: {response.text}')

    return wrapper


class Carpet(Base):
    def __init__(self, **kwargs):
        """
        Создаются все поля, которые приходят в ответе
        :param kwargs: тут инфа по ковру из ответа на сервер
        """
        super().__init__()
        self.pos_x = kwargs.get('x')
        self.pos_y = kwargs.get('y')
        self.velocity = kwargs.get('velocity')
        self.self_acceleration: dict = kwargs.get('selfAcceleration')
        self.anomaly_acceleration: dict = kwargs.get('anomalyAcceleration')
        self.status = kwargs.get('status')
        self.shield_left = kwargs.get('shieldLeftMs')
        self.attack_cd = kwargs.get('attackCooldownMs')
        self.health = kwargs.get('health')
        self.shield_cd = kwargs.get('shieldCooldownMs')
        self.id = kwargs.get('id')

    class BountyHandler:
        def __init__(self):
            self.bounties = dict()
            self.update_bounties()

        def update_bounties(self):
            """
            Тут нужно находить новые монетки, сортировать их по близости к нам и обновлять
            self.bounties
            :return:
            """
            pass

    class Bounty:
        def __init__(self, **kwargs):
            self.pos_x = kwargs.get('x')
            self.pos_y = kwargs.get('y')
            self.radius = kwargs.get('radius')
            self.points = kwargs.get('points')

    class AnomalyHandler:
        def __init__(self):
            self.anomalies = dict()
            self.update_anomalies()

        def update_anomalies(self):
            """
            Тут нужно находить новые аномалии, сортировать их по близости к нам и обновлять
            self.anomalies
            :return:
            """
            pass

    class Anomaly:
        def __init__(self, **kwargs):
            self.radius = kwargs.get('radius')
            self.strength = kwargs.get('strength')
            self.velocity: dict = kwargs.get('velocity')
            self.pos_x = kwargs.get('x')
            self.pos_y = kwargs.get('y')

    def calculate_vector(self, pos_x: float, pos_y: float) -> list:
        """
        Считает максимальный вектор ускорения(до 10) от текущей позиции до конкретной точки
        :param pos_x: x конечной точки
        :param pos_y: y конечной точки
        :return: возвращает список с ускорениями по осям [x, y]
        """
        vector = [pos_x - self.pos_x, pos_y - self.pos_y]

        vector_length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        normalized_vector = [vector[0] / vector_length, vector[1] / vector_length]

        accelerated_vector = [x * 10 for x in normalized_vector]

        return accelerated_vector

    @update_attributes_decorator
    async def give_acceleration(self, x: float, y: float):
        """
        Дать ускорение ковру
        :param x: ускорение по x
        :param y: ускорение по y
        :return: возвращает сырой ответ сервера
        """
        data = {
            "transports": [
                {
                    "acceleration": {
                        "x": x,
                        "y": y
                    },
                    "id": self.id
                }
            ]
        }
        headers = self.headers
        answer = requests.post(url='https://games-test.datsteam.dev/play/magcarp/player/move', headers=headers,
                               json=data)
        return answer

    @staticmethod
    async def get_carpets_data() -> dict | None:
        """
        Использовал чтобы получить все ковры в функции main. Вроде она кроме этого не должная использоваться
        :return:
        """
        answer = requests.post('https://games-test.datsteam.dev/play/magcarp/player/move',
                               headers={'X-Auth-Token': os.getenv('API_TOKEN'),
                                        'Content-Type': 'application/json',
                                        'accept': 'application/json'}
                               )
        if answer.status_code != 200:
            # BadAnswer не вызывается, так как не относиться к конкретному ковру
            print('Произошла ошибка:', answer.status_code, ' \n', answer.text)
            return
        return json.loads(answer.text)['transports']

    async def acceleration_to(self, pos_x, pos_y):
        """
        Задать максимальное ускорение к конкретной точке
        :param pos_x: кордината конечной точки x
        :param pos_y: координата конечной точки y
        :return:
        """
        return await self.give_acceleration(*self.calculate_vector(pos_x, pos_y))
