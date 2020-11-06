from configparser import ConfigParser
from qbittorrent import Client
import pandas as pd
import numpy as np
import argparse
import requests
import json
import os

config = ConfigParser()
config.read("config.ini")
username = config.get("qbit-username", "username")
password = config.get("qbit-password", "password")

qb = Client("http://127.0.0.1:8080/")
qb.login(username, password)

parser = argparse.ArgumentParser(description='Query YTS for movies.')
parser.add_argument('query', type=str, help='Search query or imdbid of a movie')
args = parser.parse_args()


URL = "https://yts.mx/api/v2/list_movies.json?query_term="


def download_torrent(url, filename):
    torrent_file = requests.get(url, allow_redirects=True)
    print(f"Downloading {filename}.torrent")
    open(f'{filename}.torrent', 'wb').write(torrent_file.content)
    print("Download completed.")

def download_movie(url, filename):
    qb.download_from_link(url)
    print(f"{filename} sucessfully added to download queue.")


search_results = []
def search_torrent(search_query):
    movies = requests.get(URL+str(search_query)).json()
    if movies["data"]["movie_count"] != 0:
        meta_data = movies["data"]["movies"]

        for movie in meta_data:

            imdbid = movie["imdb_code"]
            title = movie["title_long"]
            torrents = movie["torrents"]
            
            for torrent in torrents:
                quality = torrent["quality"]
                type_ = torrent["type"].capitalize()
                size = torrent["size"] 
                url = torrent["url"]

                data = {
                    "ImdbId": imdbid,
                    "Title": title,
                    "Quality": quality,
                    "Type": type_,
                    "Size": size,
                    "Url": url
                }
                
                search_results.append(data)

    else:
        print("No result found!")
        exit()


def main():
    #search_query = input("Enter search query: ")
    search_query = args.query

    search_torrent(search_query)
    df = pd.DataFrame(search_results)
    df.index = np.arange(1, len(df) + 1)
    print(df.iloc[:, :-1])

    select_movie = input("Select a movie to download: ")

    if select_movie.isnumeric():
        movie_row = df.iloc[int(select_movie)-1, :]
        title = movie_row["Title"]
        quality = movie_row["Quality"]
        type_ = movie_row["Type"]
        url = movie_row["Url"]
        filename = f"{title} [{quality}] [{type_}]"

        #download_torrent(url, filename)
        download_movie(url, filename)
        
    else:
        print("Selection must be a number!")


if __name__ == "__main__":
    main()



