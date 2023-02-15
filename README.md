
# ***Задание от "Ifotecs Academy"***

##### **Номер заявки:** _СТ-ТОМ-22830_
##### **Дата заявки:** _30.01.2023 15:55:34_
##### **Город:** _Томск_
##### **Тема стажировки:** _Разработчик Python_
##### **Срок выполнения:** _26.02.2023_
---
## ***Содержание***
> - **[Описание задания](#📄-описание-задания)**
> - **[Установка проекта](#📄-установка-проекта)**
> - **[Примеры работы](#📄-примеры-работы)**
> - **[Описание функций](#📄-описание-функций)**
---

## [📄](#содержание) _Описание задания_

**✅Реализованные задания**

Реализовать HTTP-сервер для предоставления информации по **географическим объектам.**

Реализованный сервер должен предоставлять **REST API сервис со следующими методами:**
1. ✅ Метод принимает идентификатор geonameid и возвращает информацию о городе.
2. ✅ Метод принимает страницу и количество отображаемых на странице городов и возвращает список городов с их информацией. 
3. ✅ Метод принимает названия двух городов (на русском языке) и получает информацию о найденных городах, а также дополнительно: какой из них расположен севернее и одинаковая ли у них временная зона (когда несколько городов имеют одно и то же название, разрешать неоднозначность выбирая город с большим населением; если население совпадает, брать первый попавшийся)

**Дополнительные задания:**
1. ✅ Для 3-его метода показывать пользователю не только факт различия временных зон, но и на сколько часов они различаются.
2. ✅ Реализовать метод, в котором пользователь вводит часть названия города и возвращает ему подсказку с возможными вариантами продолжений.
---

## [📄](#содержание) _Установка проекта_

**Для запуска необходимо:**
- _Python 3.10 и выше._

**Для установки неободимо:**
- _Склонировать репозиторий:_
```
git clone https://github.com/dionislez/infotecs_task.git
```
- _Установить необходимое содержимое:_
```
pip install -r .\requirements.txt
```
- _Запустить сервер (порт 8000):_
```
uvicorn server:app --reload --port 8000
```
---

## [📄](#содержание) _Примеры работы_

http://127.0.0.1:8000/cities/1489425
```
{
  "geonameid": "1489425",
  "name": "Tomsk",
  "asciiname": "Tomsk",
  "alternatenames": "TOF,Tom'sku,Tomck,Tomium,Toms'k,Tomsk,Tomska,Tomskaj,Tomskas,Tomszk,Tomçk,tomseukeu,tomska,tomusuku,tuo mu si ke,twmsk,twmsq,Τομσκ,Томск,Томскай,Томськ,Томьскъ,Տոմսկ,טומסק,تومسك,تومسک,ٹومسک,तोम्स्क,トムスク,托木斯克,톰스크",
  "latitude": "56.49771",
  "longitude": "84.97437",
  "feature class": "P",
  "feature code": "PPLA",
  "country code": "RU",
  "cc2": "",
  "admin1 code": "75",
  "admin2 code": "1489419",
  "admin3 code": "",
  "admin4 code": "",
  "population": "574002",
  "elevation": "",
  "dem": "117",
  "timezone": "Asia/Tomsk",
  "modification date": "2022-10-16"
}
```
http://127.0.0.1:8000/cities?page=1&count=5
```
[
  {
    "geonameid": "451747",
    "name": "Zyabrikovo",
    "asciiname": "Zyabrikovo",
    "alternatenames": "",
    "latitude": "56.84665",
    "longitude": "34.7048",
    "feature class": "P",
    "feature code": "PPL",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "77",
    "admin2 code": "",
    "admin3 code": "",
    "admin4 code": "",
    "population": "0",
    "elevation": "",
    "dem": "204",
    "timezone": "Europe/Moscow",
    "modification date": "2011-07-09"
  },
  {
    "geonameid": "451748",
    "name": "Znamenka",
    "asciiname": "Znamenka",
    "alternatenames": "",
    "latitude": "56.74087",
    "longitude": "34.02323",
    "feature class": "P",
    "feature code": "PPL",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "77",
    "admin2 code": "",
    "admin3 code": "",
    "admin4 code": "",
    "population": "0",
    "elevation": "",
    "dem": "215",
    "timezone": "Europe/Moscow",
    "modification date": "2011-07-09"
  },
  {
    "geonameid": "451749",
    "name": "Zhukovo",
    "asciiname": "Zhukovo",
    "alternatenames": "",
    "latitude": "57.26429",
    "longitude": "34.20956",
    "feature class": "P",
    "feature code": "PPL",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "77",
    "admin2 code": "",
    "admin3 code": "",
    "admin4 code": "",
    "population": "0",
    "elevation": "",
    "dem": "237",
    "timezone": "Europe/Moscow",
    "modification date": "2011-07-09"
  },
  {
    "geonameid": "451750",
    "name": "Zhitovo",
    "asciiname": "Zhitovo",
    "alternatenames": "",
    "latitude": "57.29693",
    "longitude": "34.41848",
    "feature class": "P",
    "feature code": "PPL",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "77",
    "admin2 code": "",
    "admin3 code": "",
    "admin4 code": "",
    "population": "0",
    "elevation": "",
    "dem": "247",
    "timezone": "Europe/Moscow",
    "modification date": "2011-07-09"
  },
  {
    "geonameid": "451751",
    "name": "Zhitnikovo",
    "asciiname": "Zhitnikovo",
    "alternatenames": "",
    "latitude": "57.20064",
    "longitude": "34.57831",
    "feature class": "P",
    "feature code": "PPL",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "77",
    "admin2 code": "",
    "admin3 code": "",
    "admin4 code": "",
    "population": "0",
    "elevation": "",
    "dem": "198",
    "timezone": "Europe/Moscow",
    "modification date": "2011-07-09"
  }
]
```
http://127.0.0.1:8000/cities/compare/томск&москва
```
{
  "2": {
    "geonameid": "524894",
    "name": "Moskva",
    "asciiname": "Moskva",
    "alternatenames": "Maskva,Moscou,Moscow,Moscu,Moscú,Moskau,Moskou,Moskovu,Moskva,Məskeu,Москва,Мәскеу",
    "latitude": "55.76167",
    "longitude": "37.60667",
    "feature class": "A",
    "feature code": "ADM1",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "48",
    "admin2 code": "",
    "admin3 code": "",
    "admin4 code": "",
    "population": "13010112",
    "elevation": "",
    "dem": "161",
    "timezone": "Europe/Moscow",
    "modification date": "2023-01-12"
  },
  "1": {
    "geonameid": "1489425",
    "name": "Tomsk",
    "asciiname": "Tomsk",
    "alternatenames": "TOF,Tom'sku,Tomck,Tomium,Toms'k,Tomsk,Tomska,Tomskaj,Tomskas,Tomszk,Tomçk,tomseukeu,tomska,tomusuku,tuo mu si ke,twmsk,twmsq,Τομσκ,Томск,Томскай,Томськ,Томьскъ,Տոմսկ,טומסק,تومسك,تومسک,ٹومسک,तोम्स्क,トムスク,托木斯克,톰스크",
    "latitude": "56.49771",
    "longitude": "84.97437",
    "feature class": "P",
    "feature code": "PPLA",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "75",
    "admin2 code": "1489419",
    "admin3 code": "",
    "admin4 code": "",
    "population": "574002",
    "elevation": "",
    "dem": "117",
    "timezone": "Asia/Tomsk",
    "modification date": "2022-10-16"
  },
  "same_timezones": {
    "timezones": false,
    "2": -4,
    "1": 4
  },
  "city_is_north": {
    "name": "Tomsk",
    "latitude": "56.49771",
    "longitude": "84.97437"
  }
}
```
http://127.0.0.1:8000/cities/find/кемерово
```
{
  "available_names": [
    "Kemerovo Airport",
    "Kemerovo",
    "Kemerovo Oblast",
    "Kemerovo South"
  ]
}
```
---

## [📄](#содержание) _Описание функций_
---