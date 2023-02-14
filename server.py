from fastapi import FastAPI, Path, Query

import queries


app = FastAPI()


@app.get('/')
async def main():
    return {
        'swagger': 'http://127.0.0.1:8000/docs',
        'get_city_by_geonameid': 'http://127.0.0.1:8000/cities/{geonameid}',
        'get_cities_by_page_and_count': 'http://127.0.0.1:8000/cities?page={page}&count={count}',
        'compare_two_cities': 'http://127.0.0.1:8000/cities/compare/{first_city}&{second_city}',
        'find_available_cities': 'http://127.0.0.1:8000/cities/find/{hint}',
        'made_by': 'Leznevskiy Denis'
    }


@app.get('/cities/{geonameid}')
async def get_city_by_geonameid(
    geonameid: str = Path(min_length=6, max_length=8)
) -> dict:
    try:
        int(geonameid)
    except ValueError:
        return {'Error': 'There is no such geonameid'}

    found_city: dict | bool = await queries.cities_find_by_geonameid(geonameid)
    if not found_city:
        found_city: dict = {
            'Error': f'the city with {geonameid} geonameid was not found'
        }

    return found_city


@app.get('/cities')
async def get_cities_by_page_and_count(
    page: int = Query(ge=0.1),
    count: int = Query(ge=0.1, le=500.1)
) -> queries.Union[dict, list]:
    found_cities: tuple = await queries.cities_by_page_count(page, count)

    if not found_cities[0]:
        return {'Error': f'{found_cities[1]} pages available for {count} cities'}

    return found_cities[0]


@app.get('/cities/compare/{first_city}&{second_city}')
async def compare_two_cities(
    first_city: str = Path(max_length=20),
    second_city: str = Path(max_length=20)
) -> dict:
    compared: bool | dict = await queries.cities_comparing(
        first_city.lower(), second_city.lower()
    )
    if not compared:
        return {'Error': 'there is no such city/cities'}
    
    return compared


@app.get('/cities/find/{hint}')
async def find_available_cities(
    hint: str = Path(min_length=1, max_length=20)
) -> dict:
    find_hints = await queries.cities_help_hints(hint)
    if not find_hints:
        return {'Error': 'there are no cities with such hint'}
    
    return find_hints
