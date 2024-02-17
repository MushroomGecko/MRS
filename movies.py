from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
import database

def _beautiful_movies(movie, tag, attribute, class_name):
    r = requests.get("https://www.rottentomatoes.com/search?search=" + movie)
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.findAll(tag, attrs={attribute: class_name})
    if table is None:
        return None
    else:
        return table

def _parse_movie(url):
    if url is None:
        return None
    information = {}
    r = requests.get(url)
    if r:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find("h1", attrs={"class": "title"})
        if table:
            title = table.text.strip().split()
            title = " ".join(title)
            title = unidecode(title)
            information["Title"] = [title]

        table = soup.find("p", attrs={"data-qa": "movie-info-synopsis"})
        if table:
            desc = table.text.strip().split()
            desc = " ".join(desc)
            desc = unidecode(desc)
            information["Description"] = [desc]

        table = soup.find("p", attrs={"data-qa": "series-info-description"})
        if table:
            desc = table.text.strip().split()
            desc = " ".join(desc)
            desc = unidecode(desc)
            information["Description"] = [desc]

        table = soup.findAll("li", attrs={"class": "info-item"})
        if table:
            for i in table:
                item = i.find("b").text.strip(': ')
                value = i.find("span").text.strip().split()
                value = " ".join(value)
                value = unidecode(value)
                if "Date" in item:
                    information[item] = [value]
                else:
                    value = value.split(',')
                    value = list(map(str.strip, value))
                    information[item] = value

        table = soup.findAll("div", attrs={"class": "cast-and-crew-item"})
        if table:
            cast = []
            for i in table:
                value = i.find("p").text.strip().split()
                value = " ".join(value)
                value = unidecode(value)
                cast.append(value)
            item = "Cast"
            information[item] = cast

        table = soup.find("tile-dynamic", attrs={"class": "thumbnail"})
        if table:
            img = table.find("rt-img")["src"]
            information["Thumbnail"] = [img]

        if 'Rating' in information:
            if information['Rating'][0][0] == 'G':
                information['Rating'] = ['G']
            if information['Rating'][0][0] == 'R':
                information['Rating'] = ['R']
            if information['Rating'][0][0] == 'X':
                information['Rating'] = ['X']
            if 'PG-13' in information['Rating'][0]:
                information['Rating'] = ['PG-13']
            elif 'PG' in information['Rating'][0]:
                information['Rating'] = ['PG']
            if 'TV-14' in information['Rating'][0]:
                information['Rating'] = ['TV-14']
            if 'NC-17' in information['Rating'][0]:
                information['Rating'] = ['NC-17']
            else:
                information['Rating'] = []
        print(information)
        return information
    return None


def _get_movie_list(table, subtag, subattribute):
    if table is None:
        return None
    movielist = []
    for i in table:
        movielist.append(i.find(subtag).get(subattribute))
    return movielist


class MovieAPI:
    movies = []
    new_movies = []
    query = ""

    def __init__(self):
        self.movies = []
        self.new_movies = []
        self.query = ""

    def query_movie(self, query):
        self.new_movies = []
        print(query)
        for curr_movie in _get_movie_list(_beautiful_movies(query, "search-page-media-row", "data-qa", "data-row"), "a", "href"):
            print(curr_movie)
            movie = _parse_movie(curr_movie)
            if movie:
                print(movie)
                database.add_list_to_db([movie])
                self.new_movies.append(movie)
        return self.new_movies

    def print_movies(self):
        return self.movies

    def print_new_movies(self):
        return self.new_movies
