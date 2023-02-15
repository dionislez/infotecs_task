import math
from datetime import datetime
from typing import Union

from dateutil.relativedelta import relativedelta
from pytz import timezone


KEYS: list = [
    'geonameid', 'name', 'asciiname', 'alternatenames',
    'latitude', 'longitude', 'feature class', 'feature code',
    'country code', 'cc2', 'admin1 code', 'admin2 code',
    'admin3 code', 'admin4 code', 'population', 'elevation',
    'dem', 'timezone', 'modification date'
]


async def cities_read_file() -> list:
    '''Method to read data from ./RU.txt file with utf8 encoding'''
    with open(file='./RU.txt', mode='r', encoding='utf8') as file:
        file: list = file.read().splitlines()
    return file


async def cities_find_by_geonameid(geonameid: str) -> Union[bool, dict]:
    '''Method for http://127.0.0.1:8000/cities/{geonameid}'''
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
    '''Method for http://127.0.0.1:8000/cities?page={page}&count={count}'''
    cities: list = await cities_read_file()

    available_pages: int = math.ceil(len(cities) / count)
    page_from: int = 0 if page == 1 else (page - 1) * count
    page_to: int = page_from + count

    result: list = list()
    for city in cities[page_from:page_to]:
        city_dict: dict = dict(zip(KEYS, city.split('\t')))
        result.append(city_dict)

    return result, available_pages


async def cities_comparing(first_city: str, second_city: str) -> Union[bool, dict]:
    '''Method for http://127.0.0.1:8000/cities/compare/{first_city}&{second_city}'''
    cities: list = await cities_read_file()
    try:
        translits_first: dict = await cities_translit(first_city, 1)
        available_translits = translits_first
    except KeyError:
        available_translits = {first_city: 1}
    try:
        translits_second = await cities_translit(second_city, 2)
        available_translits.update(translits_second)
    except KeyError:
        available_translits.update({second_city: 2})

    result: dict = dict()
    for city in cities:
        check_city: list = city.split('\t')
        name: str = check_city[1].lower().replace('ë', 'e')
        found = [False, False]

        if name in available_translits:
            found[0] = True
            found[1] = available_translits.get(name)

        if not found[0]:
            alternatenames: list = check_city[3].lower().replace('ë', 'e')
            alternatenames: list = alternatenames.replace('ё', 'е').split(',')
            found = await cities_check_city(first_city, second_city, alternatenames)

        if found[0]:
            if found[1] in result:
                added_population: int = int(result[found[1]]['population'])
                population: int = int(check_city[14])
                if added_population < population:
                    result[found[1]] = dict(zip(KEYS, check_city))
                continue

            result[found[1]] = dict(zip(KEYS, check_city))

    check_result: bool | dict = await cities_comparing_check(list(result.keys()), result)
    return check_result


async def cities_comparing_check(city: list, result: dict) -> Union[bool, dict]:
    '''Method to check timezones and north'''
    if len(result) != 2:
        return False

    result['same_timezones']: dict = {
        'timezones': True,
        f'{city[0]}': 0,
        f'{city[1]}': 0
    }

    if not result[city[0]]['timezone'] or not result[city[1]]['timezone']:
        result['same_timezones'] = {'Error': 'unknown timezone/timezones'}

    elif result[city[0]]['timezone'] != result[city[1]]['timezone']:
        utc: datetime = timezone('utc').localize(datetime.utcnow())
        city_0: datetime = utc.astimezone(
            timezone(result[city[0]]['timezone'])
        ).replace(tzinfo=None)
        city_1: datetime = utc.astimezone(
            timezone(result[city[1]]['timezone'])
        ).replace(tzinfo=None)

        result['same_timezones']: dict = {
            'timezones': False,
            f'{city[0]}': relativedelta(city_0, city_1).hours,
            f'{city[1]}': relativedelta(city_1, city_0).hours
        }

    if not result[city[0]]['latitude'] or not result[city[1]]['latitude']:
        result['city_is_north']: dict = {'Error': 'unknown latitude'}
        return result

    is_north: dict = result[city[1]]
    if result[city[0]]['latitude'] > is_north['latitude']:
        is_north: dict = result[city[0]]

    result['city_is_north']: dict = {
        'name': is_north['name'],
        'latitude': is_north['latitude'],
        'longitude': is_north['longitude'],
    }

    return result


async def cities_help_hints(city_part: str) -> Union[bool, dict]:
    '''Method for http://127.0.0.1:8000/cities/find/{hint}'''
    cities: list = await cities_read_file()
    try:
        latin_find: str = await cities_translit(city_part, None)
        latin_find: str = list(latin_find.keys())[0]
    except KeyError:
        latin_find: str = city_part

    result: dict = {'available_names': []}
    for city in cities:
        check_city: list = city.split('\t')
        check_latin: str = check_city[1].lower().replace('ë', 'e').replace('ё', 'е')
        check_latin: str = check_latin.find(latin_find)

        if check_latin != -1:
            result['available_names'].append(check_city[1])

    if not result['available_names']:
        return False

    result['available_names']: list = list(set(result['available_names']))
    return result


async def cities_check_city(first_city: str, second_city: str, alternatenames: list):
    '''Second step to check russian alternative names of cities'''
    for altername in alternatenames:
        if first_city == altername:
            return [True, 1]
        elif second_city == altername:
            return [True, 2]

    return [False, False]


async def cities_translit(word: str, city_num: int) -> dict:
    '''Own method to translit areas and cities'''
    alphabet: dict = {'а': ('a', 'a'), 'б': ('b', 'b'), 'в': ('v', 'v'), 'г': ('g', 'g'),
                'д': ('d', 'd'), 'е': ('e', 'e'), 'ё': ('yo', 'e'), 'ж': ('zh', 'zh'),
                'з': ('z', 'z'), 'и': ('i', 'i'), 'й': ("i'", 'y'), 'к': ('k', 'k'),
                'л': ('l', 'l'), 'м': ('m', 'm'), 'н': ('n', 'n'), 'о': ('o', 'o'),
                'п': ('p', 'p'), 'р': ('r', 'r'), 'с': ('s', 's'), 'т': ('t', 't'),
                'у': ('u', 'u'), 'ф': ('f', 'f'), 'х': ('kh', 'kh'), 'ц': ('tc', 'ts'),
                'ч': ('ch', 'ch'), 'ш': ('sh', 'sh'), 'щ': ('shch', 'shch'), 'ъ': ("”", ''),
                'ы': ('y', 'y'), 'ь': ("'", "’"), 'э': ("e'", 'e'), 'ю': ('iu', 'yu'),
                'я': ('ia', 'ya'), ' ': (' ', ' '), '-':('-', '-'), '#': ('#', '#'),
                '№': ('#', '#'), '«': ('«', '«'), '»': ('»', '»'), "'": ("'", "'"),
                '"': ('"', '"'), ')': (')', ')'), '(': ('(', '('), '?': ('?', '?')}

    length: int = len(word)
    glasns: list = ['а', 'е', 'ё', 'и', 'о', 'у', 'э']

    punto_word: str = str()
    recommended_word: str = str()
    for index, letter in enumerate(word):
        if letter in '0123456789':
            punto_word += letter
            recommended_word += letter
            continue

        if index == 0 and letter == 'е':
            punto_word += 'ye'
            recommended_word += 'ye'
            continue

        if index != 0 and index != length-1 and letter in ['ь', 'ъ'] and word[index+1] in glasns:
            change: str = '’y'
            if letter == 'ъ':
                change: str = '”y'
            punto_word += change
            recommended_word += change
            continue

        if index != 0 and index != length-1 and letter in glasns and word[index+1] in glasns:
            punto_word += alphabet[letter][0] + 'y'
            recommended_word += alphabet[letter][1] + 'y'
            continue

        punto_word += alphabet[letter][0]
        recommended_word += alphabet[letter][1]

    if punto_word == recommended_word:
        return {recommended_word: city_num}

    return {recommended_word: city_num, punto_word: city_num}
