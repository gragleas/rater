import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import re
import string
import pygame
import math
import os
from pygame.locals import *
import sys
from unidecode import unidecode
import time
from difflib import SequenceMatcher
from threading import Thread

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_file_count(directory):
    count = 0

    for entry in os.scandir(directory):
        if entry.is_file():
            count += 1

        elif entry.is_dir():
            count += get_file_count(os.path.join(directory, entry.name))

    return count

def get_dir_count(directory):
    count = 0

    for entry in os.scandir(directory):
        if entry.is_dir():
            count += 1

    return count

def value(r):
    if (r == 'I'):
        return 1
    if (r == 'V'):
        return 5
    if (r == 'X'):
        return 10
    if (r == 'L'):
        return 50
    if (r == 'C'):
        return 100
    if (r == 'D'):
        return 500
    if (r == 'M'):
        return 1000
    return -1
 
def romanToDecimal(str):
    res = 0
    i = 0
 
    while (i < len(str)):
 
        # Getting value of symbol s[i]
        s1 = value(str[i])
 
        if (i + 1 < len(str)):
 
            # Getting value of symbol s[i + 1]
            s2 = value(str[i + 1])
 
            # Comparing both values
            if (s1 >= s2):
 
                # Value of current symbol is greater
                # or equal to the next symbol
                res = res + s1
                i = i + 1
            else:
 
                # Value of current symbol is greater
                # or equal to the next symbol
                res = res + s2 - s1
                i = i + 2
        else:
            res = res + s1
            i = i + 1
 
    return res

class Game:
    def __init__(self, name, rating, splits, platform, finished, comments="a"):
        self.name = name
        self.rating = rating
        self.splits = splits
        self.platform = platform
        self.finished = finished
        self.image_index = 0
        self.cover_index = 0
        if not os.path.exists("covers/" + self.name.replace(":", "") + "/" + str(self.image_index) + "/" + str(self.cover_index) + ".jpg"):
            self.get_image()
        self.map_splits()
        self.is_finished()
        self.image = "covers/" + self.name.replace(":", "") + "/" + str(self.image_index) + "/" + str(self.cover_index) + ".jpg"
        self.comments = comments

    def map_splits(self, new=None):
        if new != None:
            arr = str(new).split("/")
            self.splits = [int(i) for i in arr]
        else:
            arr = str(self.splits).split("/")
            self.splits = [int(i) for i in arr]

    def is_finished(self):
        if self.finished == "Y" or self.finished == None or self.finished == True:
            self.finished = True
        if self.finished == "N" or self.finished == False:
            self.finished = False

    def edit_entry(self, param, new_value):
        data = pd.read_csv("updated_data.csv")
        try:
            data = data.drop(data.columns[[5, 6]], axis=1)
        except:
            pass
        data.loc[data['Title'] == self.name, param] = new_value
        data.to_csv("updated_data.csv", index=False)
        
    def next_image(self):
        count = get_dir_count("covers/" + self.name.replace(":", "") + "/")
        self.image_index = (self.image_index + 1) % count
        self.cover_index = 0
        self.image = "covers/" + self.name.replace(":", "") + "/" + str(self.image_index) + "/" + str(self.cover_index) + ".jpg"

    def next_cover(self):
        count = get_file_count("covers/" + self.name.replace(":", "") + "/" + str(self.image_index) + "/")
        self.cover_index = (self.cover_index + 1) % count
        self.image = "covers/" + self.name.replace(":", "") + "/" + str(self.image_index) + "/" + str(self.cover_index) + ".jpg"

    def previous_image(self):
        count = get_dir_count("covers/" + self.name.replace(":", "") + "/")
        self.image_index = (self.image_index - 1) % count
        self.cover_index = 0
        self.image = "covers/" + self.name.replace(":", "") + "/" + str(self.image_index) + "/" + str(self.cover_index) + ".jpg"

    def previous_cover(self):
        count = get_file_count("covers/" + self.name.replace(":", "") + "/" + str(self.image_index) + "/")
        self.cover_index = (self.cover_index - 1) % count
        self.image = "covers/" + self.name.replace(":", "") + "/" + str(self.image_index) + "/" + str(self.cover_index) + ".jpg"

    def get_image(self):
        os.makedirs("covers/" + self.name.replace(":", ""), exist_ok=True)
        file_count = get_file_count("covers/" + self.name.replace(":", ""))
        if file_count == 0:
            response = requests.get("https://www.mobygames.com/search/?q=" + "%20".join(self.name.lower().split()))
            soup = bs(response.text, "html.parser")
            urls = soup.find_all('a', attrs={'href': re.compile("^https://")})
            valid_url = ''
            game_counter = 0
            href_list = []
            for i in urls:
                if i["href"] not in href_list:
                    href_list.append(i["href"])
                    name = i["href"].split("/")[-2]
                    temp_name = self.name.replace("'", "-").replace("_", "-").translate(str.maketrans('', '', string.punctuation.replace("-",""))).replace(' ', '-').lower()

                    entry = 1
                    try:
                        original = romanToDecimal(temp_name.split("-")[-1])
                        href_entry = romanToDecimal(name.split("-")[-1])
                        if original != href_entry:
                            entry = 0
                    except:
                        entry = 1
                        pass
                        
                    if similar(name.replace("_", ''), temp_name) > .8 and entry:
                        valid_url = i["href"]
                        valid_url += "covers/"
                        response = requests.get(valid_url)
                        soup = bs(response.content, "html.parser")
                        url = ''
                        images = soup.findAll('img')
                        img_counter = 0
                        for img in images:
                            if img.has_attr('src') and "gif" not in img['src'] and "png" not in img['src']:
                                url = img['src']
                                try:
                                    image_data = requests.get(url).content
                                except:
                                    image_data = requests.get(url).content
                                os.makedirs("covers/" + self.name.replace(":", "") + "/" + str(game_counter) + "/", exist_ok=True)
                                with open("covers/" + self.name.replace(":", "") + "/" + str(game_counter) + "/" + str(img_counter) + ".jpg", "wb") as handler:
                                    handler.write(image_data)
                                img_counter += 1
                        game_counter += 1
        return 1
