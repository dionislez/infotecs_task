import asyncio
import difflib
import math
import multiprocessing
import re
from concurrent.futures import ProcessPoolExecutor
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
    '''Method for /cities/{geonameid}'''
    cities: list = await cities_read_file()

    city_found: list = []
    for city in cities:
        check_id: list = city.split('\t')
        if geonameid == check_id[0]:
            city_found: list = check_id
            break

    if not city_found:
        return False

    return zip(KEYS, city_found)


async def cities_by_page_count(page: int, count: int) -> tuple:
    '''Method for /cities?page={page}&count={count}'''
    cities: list = await cities_read_file()

    available_pages: int = math.ceil(len(cities) / count)
    page_from: int = 0 if page == 1 else (page - 1) * count
    page_to: int = page_from + count

    result: list = []
    for city in cities[page_from:page_to]:
        city_dict: dict = dict(zip(KEYS, city.split('\t')))
        result.append(city_dict)

    return result, available_pages


async def cities_comparing(first_city: str, second_city: str) -> Union[bool, dict]:
    '''Method for /cities/compare/{first_city}&{second_city}'''
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

    loop = asyncio.get_event_loop()
    cores: int = multiprocessing.cpu_count()
    executor: ProcessPoolExecutor = ProcessPoolExecutor(max_workers=cores)

    total_cities: int = len(cities)
    tasks: list = []
    for core in range(1, cores+1):
        finish: int = (total_cities // cores) * core
        if core == cores:
            finish: int = total_cities
        start: int = (total_cities // cores) * (core - 1)
        tasks.append(loop.run_in_executor(executor,
                                            cities_comparing_finding, cities,
                                            start, finish, available_translits,
                                            first_city, second_city))
    tasks: list = await asyncio.gather(*tasks)

    result_check: dict = {1: [], 2: []}
    control_check: dict = {1: {}, 2: {}}
    for steps_1_2, step_3 in tasks:
        if steps_1_2:
            if 1 in steps_1_2:
                result_check[1].append(steps_1_2[1])
            if 2 in steps_1_2:
                result_check[2].append(steps_1_2[2])
            continue

        if step_3[1]:
            key: float = max(step_3[1])
            control_check[1][key] = step_3[1][key]
        if step_3[2]:
            key: float = max(step_3[2])
            control_check[2][key] = step_3[2][key]

    result: dict = {}
    if result_check[1]:
        check_name: list = sorted(
            result_check[1], key=lambda x:int(x['population']), reverse=True
        )
        cur_city: list = [
            name for name in check_name
            if name['name'].lower().replace('ë', 'e') in available_translits
        ]
        result[1]: dict = cur_city[0] if cur_city else check_name[0]
    elif control_check[1]:
        max_key: float = max(list(control_check[1].keys()))
        result[1]: dict  = control_check[1][max_key]

    if result_check[2]:
        check_name: list = sorted(
            result_check[2], key=lambda x:int(x['population']), reverse=True
        )
        cur_city: list = [
            name for name in check_name
            if name['name'].lower().replace('ë', 'e') in available_translits
        ]
        result[2]: dict = cur_city[0] if cur_city else check_name[0]
    elif control_check[2]:
        max_key: float = max(list(control_check[2].keys()))
        result[2]: dict = control_check[2][max_key]

    check_result: bool | dict = await cities_comparing_check(list(result.keys()), result)
    return check_result


def cities_comparing_finding(
    cities: list, start: int, finish: int,
    available_translits: dict, first_city: str, second_city: str
) -> tuple:
    '''Search of 2 cities in 3 steps (by translit, russian name, sequences)'''
    result: dict = {}
    control_check: dict = {1: {}, 2: {}}
    for city in cities[start:finish]:
        check_city: list = city.split('\t')
        name: str = check_city[1].lower().replace('ë', 'e')
        found = [False, False]

        if name in available_translits:
            found[0] = True
            found[1] = available_translits.get(name)

        if not found[0]:
            alternatenames: list = check_city[3].lower().replace('ë', 'e')
            alternatenames: list = alternatenames.replace('ё', 'е').split(',')
            found = cities_check_city(first_city, second_city, alternatenames)

        if not found[0] and (1 or 2) not in result:
            for translit in available_translits:
                matcher = difflib.SequenceMatcher(None, name, translit)
                ratio = matcher.ratio()
                if ratio >= 0.8:
                    control_check[available_translits[translit]][ratio] = dict(zip(KEYS,check_city))
                    break

        if found[0]:
            if found[1] in result:
                added_population: int = int(result[found[1]]['population'])
                population: int = int(check_city[14])
                if added_population < population:
                    result[found[1]] = dict(zip(KEYS, check_city))
                continue
            result[found[1]] = dict(zip(KEYS, check_city))

    return result, control_check


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
    '''Method for /cities/find/{hint}'''
    cities: list = await cities_read_file()
    try:
        latin_find: str = await cities_translit(city_part, None)
        latin_find: str = list(latin_find.keys())
    except KeyError:
        latin_find: str = [city_part]

    result: dict = {'available_names': []}
    for city in cities:
        check_city: list = city.split('\t')
        check_latin: str = check_city[1].lower().replace('ë', 'e').replace('ё', 'е')
        for check in latin_find:
            if check_latin.find(check) != -1:
                result['available_names'].append(check_city[1])
                break

    if not result['available_names']:
        return False

    result['available_names']: list = list(set(result['available_names']))
    return result


def cities_check_city(first_city: str, second_city: str, alternatenames: list):
    '''Second step to check russian alternative names of cities'''
    for altername in alternatenames:
        if first_city == altername:
            return [True, 1]
        if second_city == altername:
            return [True, 2]

    return [False, False]


async def cities_translit(word: str, city_num: int) -> dict:
    '''Own method to translit areas and cities (only russian)'''
    alphabet: dict = {'а': ('a','a','a'),'б': ('b','b','b'),'в': ('v','v','v'),'г': ('g','g','g'),
                'д': ('d','d','d'),'е': ('e','e','e'),'ё': ('yo','e','e'),'ж': ('zh','zh','zh'),
                'з': ('z','z','z'),'и': ('i','i','i'),'й': ("i'",'y','i'),'к': ('k','k','k'),
                'л': ('l','l','l'),'м': ('m','m','m'),'н': ('n','n','n'),'о': ('o','o','o'),
                'п': ('p','p','p'),'р': ('r','r','r'),'с': ('s','s','s'),'т': ('t','t','t'),
                'у': ('u','u','u'),'ф': ('f','f','f'),'х': ('kh','kh','kh'),'ц': ('tc','ts','ts'),
                'ч': ('ch','ch','ch'),'ш': ('sh','sh','sh'),'щ': ('shch','shch','shch'),
                'ъ': ("”",'',''),'ы': ('y','y','y'),'ь': ("'","’","’"),'э': ("e'",'e','e'),
                'ю': ('iu','yu','yu'),'я': ('ia','ya','ya'),' ': (' ',' ',' '),'-':('-','-','-'),
                '#': ('#','#','#'),'№': ('#','#','#'),'«': ('«','«','«'),'»': ('»','»','»'),
                "'": ("'","'","'"),'"': ('"','"','"'),')': (')',')',')'),'(': ('(','(','('),
                '?': ('?','?','?'), ',': (',', ',', ','), '.': ('.', '.', '.'),
                '!': ('!', '!', '!'), '/': ('/', '/', '/'), '\\': ('\\', '\\', '\\'),
                '[': ('[', '[', '['), ']': (']', ']', ']'), '`': ('`', '`', '`'),
                '~': ('~', '~', '~'), '$': ('$', '$', '$'), ':': (':', ':', ':'),
                '=': ('=', '=', '='), '^': ('^', '^', '^'), '{': ('{', '{', '{'),
                '}': ('}', '}', '}'), ';': (';', ';', ';'), '&': ('&', '&', '&'),
                '<': ('<', '<', '<'), '>': ('>', '>', '>'), '*': ('*', '*', '*')}

    length: int = len(word)
    glasns: list = ['а', 'е', 'ё', 'и', 'о', 'у', 'э']

    punto_word: str = str()
    recommended_word: str = str()
    extra_word: str = str()
    for index, letter in enumerate(word):
        if letter in '0123456789':
            punto_word += letter
            recommended_word += letter
            extra_word += letter
            continue

        if index == 0 and letter == 'е':
            punto_word += 'ye'
            recommended_word += 'ye'
            extra_word += 'ye'
            continue

        if index != 0 and index != length-1 and letter in ['ь', 'ъ'] and word[index+1] in glasns:
            change: str = '’y'
            if letter == 'ъ':
                change: str = '”y'
            punto_word += change
            recommended_word += change
            extra_word += change
            continue

        if index != 0 and index != length-1 and letter in glasns and word[index+1] in glasns:
            punto_word += alphabet[letter][0] + 'y'
            recommended_word += alphabet[letter][1] + 'y'
            extra_word += alphabet[letter][2] + 'y'
            continue

        punto_word += alphabet[letter][0]
        recommended_word += alphabet[letter][1]
        extra_word += alphabet[letter][2]

    result = {recommended_word: city_num, punto_word: city_num, extra_word: city_num}
    find_words = re.compile("evrop|yevrop|aziya|aziia|sankhotel|otel’|otel'")
    for gen_word in [punto_word, recommended_word, extra_word]:
        if find_words.search(gen_word):
            updated = gen_word.replace('yev', 'eu').replace('ev', 'eu')
            updated = updated.replace('sankhotel', 'sunhotel')
            updated = updated.replace('aziya', 'asia').replace('aziia', 'asia')
            updated = updated.replace("otel'", 'hotel').replace('otel’', 'hotel')
            result.update({updated: city_num})

        if '’' in gen_word:
            result.update({gen_word.replace("'", '').replace("’", ''): city_num})

        if "'" in gen_word:
            result.update({gen_word.replace("'", '').replace("’", ''): city_num})

    return result
