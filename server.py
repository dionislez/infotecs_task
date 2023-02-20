from fastapi import FastAPI, Path, Query
from fastapi.responses import JSONResponse

import queries


app: FastAPI = FastAPI(title='Infotecs task. Leznevskiy Denis.', version='TASK',
                        docs_url='/infotecs/docs', redoc_url='/infotecs/redoc')


@app.get('/cities/{geonameid}', tags=['1) Cities by a geonameid'])
async def get_city_by_geonameid(
    geonameid: int = Path(gt=0, description='example: 1489425')
) -> dict:
    '''/cities/{geonameid}'''
    found_city: dict | bool = await queries.cities_find_by_geonameid(str(geonameid))
    if not found_city:
        return JSONResponse(content={'message': 'Wrong geonameid'}, status_code=404)
    return found_city


@app.get('/cities', tags=['2) Cities by a page and a count'])
async def get_cities_by_page_and_count(
    page: int = Query(gt=0, description='example: 1'),
    count: int = Query(gt=0, lt=501, description='example: 5')
) -> list:
    '''/cities?page={page}&count={count}'''
    found_cities: tuple = await queries.cities_by_page_count(page, count)
    if not found_cities[0]:
        return JSONResponse(content={'message': f'{found_cities[1]} pages for {count} cities'},
                            status_code=404)
    return found_cities[0]


@app.get(
    '/cities/compare/{first_city}&{second_city}', tags=['3) First and second cities']
)
async def compare_two_cities(
    first_city: str = Path(max_length=150, description='example: Томск'),
    second_city: str = Path(max_length=150, description='example: Кемерово')
) -> dict:
    '''/cities/compare/{first_city}&{second_city}'''
    compared: bool | dict = await queries.cities_comparing(
        first_city.lower().replace('ë', 'e').replace('ё', 'е'),
        second_city.lower().replace('ë', 'e').replace('ё', 'е')
    )
    if not compared:
        return JSONResponse(content={'message': 'No cities'}, status_code=404)
    return compared


@app.get('/cities/find/{hint}', tags=['4) Find cities by a hint'])
async def find_available_cities(
    hint: str = Path(max_length=150, description='example: Томск')
) -> dict:
    '''/cities/find/{hint}'''
    find_hints: bool | dict = await queries.cities_help_hints(
        hint.lower().replace('ë', 'e').replace('ё', 'е')
    )
    if not find_hints:
        return JSONResponse(content={'message': 'No cities'}, status_code=404)
    return find_hints
