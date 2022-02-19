# 1) Посмотреть документацию к API GitHub, разобраться как вывести список
#репозиториев для конкретного пользователя, сохранить JSON-вывод в файле
 #*.json; написать функцию, возвращающую(return) список репозиториев.

import os
import requests
import json
from decouple import config

from openweathermap import appid

GITHUB_SECRET = config("GITHUB_SECRET")
GITHUB_USER = input("Enter github username: ")

def get_repos(user):
    r = requests.get(
        f"https://api.github.com/users/{user}/repos", auth=(GITHUB_USER, GITHUB_SECRET)
    )

    if r.status_code != 200:
        print(f"User {user} does not exists")
        return None
        repos = []
        for i in r.json():
            repo = dict()
        try:
            repo["id"] = i["id"]
            repo["full_name"] = i["full_name"]
            repo["svn_url"] = i["svn_url"]
        except KeyError as err:
            print(f"Underfined: {err}")
        finally:
            repos.append(repo)
        return repos

def repos_to_json(repos):
    json_repos = json.dumps(repos)
    return json_repos

def save_json(json_string, filename=f"./json_data/{GITHUB_USER}.json"):
    try:
        with open(filename, "w", encoding="utf-8")as jf:
            jf.write(json_string)
    except FileNotFoundError:
        os.mkdir(os.path.join(os.getcwd(), filename.split("/")[1]))
        with open(filename, "w", encoding="utf-8") as jf:
            jf.write(json_string)


def main():
    repos = get_repos(GITHUB_USER)
    if not repos:
        return None
    json_repos = repos_to_json(repos)
    save_json(json_repos)



#******************************************************************************


# 2) Зарегистрироваться на https://openweathermap.org/api и написать функцию,
# которая получает погоду в данный момент для города,
# название которого получается через input. https://openweathermap.org/current

import os
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

class Status:
    NOT_FOUND_404 = 404
    OK_200 = 200

class GetWeather:
    WEATHER_URL_TEMPLATE = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q=[city]&appid={os.getenv('OPEN_WEATHER_API_KEY')}"
    )

    def __init__(self):
        self._run_logic()

    @staticmethod
    def by_city_name_input():
        return GetWeather()
    def _run_logic(self) -> None:
        self.current_city = self._get_city_input()
        self.current_data = self._response_data()

    def _get_city_input(self) -> str:
        city = input('Введите название города[default: Moscow]: ')
        if not city:
            city = 'Moscow'
        return city
    def _get_response_data(self) -> None:
        url = self.WEATHER_URL_TEMPLATE.replace("[city]", self.current_city)
        response = requests.get(url)
        if response.status_code == Status.NOT_FOUND_404:
            raise ValueError('City not found')
        print(type(response.json()))
        return response.json()

    @property
    def data(self):
        return self.current_data

if __name__ == "__main__":
    city_weather = GetWeather.by_city_name_input().data
    pprint(city_weather)



