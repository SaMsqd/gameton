import os
import time

from API.carpetAPI import Carpet
from dotenv import load_dotenv
import asyncio


load_dotenv()

carpets: dict[int, Carpet] = {}


async def carpet_handler(carpet: Carpet):
    """
    Тут хочу реализовать логику полного handler'а ковра (у нас их было 5 на тестовом запуске)
    :param carpet:
    :return:
    """
    pass


async def main():
    # В переменную carpets заносятся все ковры
    for index, transport in enumerate(await Carpet.get_carpets_data()):
        carpets[index] = Carpet(**transport)

    # Тесты, если честно, я нихуя не понял как работает ускорение, ковру вообще похуй на заданные параметры
    print(carpets[0].pos_x, carpets[0].pos_y)
    await carpets[0].give_acceleration(0, 10)
    print('Моё ускорение', carpets[0].self_acceleration)
    print('Ускорение в целом', carpets[0].velocity)
    time.sleep(5)
    print('Моё ускорение', carpets[0].self_acceleration)
    print('Ускорение в целом', carpets[0].velocity)
    print(carpets[0].pos_x, carpets[0].pos_y)
    await carpets[0].give_acceleration(0, -10)
    print('Моё ускорение', carpets[0].self_acceleration)
    print('Ускорение в целом', carpets[0].velocity)
    time.sleep(5)
    print('Моё ускорение', carpets[0].self_acceleration)
    print('Ускорение в целом', carpets[0].velocity)
    print(carpets[0].pos_x, carpets[0].pos_y)


if __name__ == '__main__':
    asyncio.run(main())

