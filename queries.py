import asyncio
import math
from datetime import datetime
from typing import Union

import cyrtranslit
from transliterate import translit
from pytz import timezone


KEYS = [
    'geonameid', 'name', 'asciiname', 'alternatenames',
    'latitude', 'longitude', 'feature class', 'feature code',
    'country code', 'cc2', 'admin1 code', 'admin2 code',
    'admin3 code', 'admin4 code', 'population', 'elevation',
    'dem', 'timezone', 'modification date'
]


async def cities_read_file() -> list:
    with open(file='./RU.txt', mode='r', encoding='utf8') as file:
        file = file.read().splitlines()
    return file


async def cities_find_by_geonameid(geonameid: str) -> Union[bool, dict]:
    cities: list = await cities_read_file()
    city_found: list = list()

    for city in cities:
        check_id: list = city.split('\t')
        if geonameid == check_id[0]:
            city_found: list = check_id
            break

    if not city_found:
        return False

    return zip(KEYS, city_found)


async def cities_by_page_count(page: int, count: int) -> tuple:
    cities: list = await cities_read_file()
    result: list = list()
    available_pages: int = math.ceil(len(cities) / count)
    page_from: int = 0 if page == 1 else (page - 1) * count
    page_to: int = page_from + count

    for city in cities[page_from:page_to]:
        city_dict: dict = dict(zip(KEYS, city.split('\t')))
        result.append(city_dict)

    return result, available_pages


async def cities_comparing(first_city: str, second_city: str) -> Union[bool, dict]:
    cities: list = await cities_read_file()
    latin_first: str = cyrtranslit.to_latin(
        f'{first_city} {second_city}'.lower(), 'ru'
    )
    latin_second: str = translit(
        f'{first_city} {second_city}'.lower(), language_code='ru', reversed=True
    )

    available_translits: list = latin_first.split(' ') + latin_second.split(' ')
    result: dict = dict()
    for city in cities:
        check_city: list = city.split('\t')
        name: str = check_city[1].lower()
        population: int = int(check_city[14])

        if name in available_translits:
            if name in result:
                added_population: int = int(result[name]['population'])
                if added_population < population:
                    result[name] = dict(zip(KEYS, check_city))
                continue

            result[name] = dict(zip(KEYS, check_city))
    
    check_result: bool | dict = await cities_comparing_check(list(result.keys()), result)
    return check_result


async def cities_comparing_check(city: list, result: dict) -> Union[bool, dict]:
    if len(result) != 2:
        return False

    result['same_timezones']: dict = {
        'timezones': True,
        f'{city[0]}/{city[1]}': 0,
        f'{city[1]}/{city[0]}': 0
    }
    if result[city[0]]['timezone'] != result[city[1]]['timezone']:
        first_time = timezone(result[city[0]]['timezone'])
        second_time = timezone(result[city[1]]['timezone'])
        delta: int = datetime.now(first_time).hour - datetime.now(second_time).hour
        result['same_timezones']: dict = {
            'timezones': False,
            f'{city[0]}/{city[1]}': delta * -1,
            f'{city[1]}/{city[0]}': delta
        }

    is_north: dict = result[city[1]]
    if result[city[0]]['latitude'] > is_north['latitude']:
        is_north: dict = result[city[0]]

    result['city_is_north']: dict = {
        'name': is_north['name'],
        'latitude': is_north['latitude'],
        'longitude': is_north['longitude'],
    }

    return result


if __name__ == '__main__':
    asyncio.run()