#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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

platform_list = {
    "PC": "https://www.mobygames.com/game/windows/",
    "VR": "https://www.mobygames.com/game/windows/",
    "Wii": "https://www.mobygames.com/game/wii/",
    "Xbox": "https://www.mobygames.com/game/xbox/",
    "Xbox 360": "https://www.mobygames.com/game/xbox360/",
    "Xbox One": "https://www.mobygames.com/game/xbox-one/",
    "Gamecube": "https://www.mobygames.com/game/gamecube/",
    "PS2": "https://www.mobygames.com/game/ps2/",
    "PS3": "https://www.mobygames.com/game/ps3/",
    "PS4": "https://www.mobygames.com/game/playstation-4/",
    "PS5": "https://www.mobygames.com/game/playstation-5/"
    
}

platform_names = {
		"PC": "windows",
		"VR": "windows",
		"Wii": "wii",
		"Xbox": "xbox",
		"Xbox 360": "xbox360",
		"Xbox One": "xbox-one",
		"Gamecube": "gamecube",
		"PS2": "playstation-2",
		"PS3": "playstation-3",
		"PS4": "playstation-4",
		"PS5": "playstation-5"
}

platforms = [key for key in platform_list]

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class Game:
    def __init__(self, name, rating, splits, platform, finished, comments="a"):
        self.name = name
        self.rating = rating
        self.splits = splits
        self.platform = platform
        self.finished = finished
        self.image_dup_count = 0
        if not os.path.exists("covers/" + name + ".jpg"):
            self.get_image()
        self.map_splits()
        self.is_finished()
        self.image = "covers/" + self.name + ".jpg"
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
        self.image_dup_count += 1
        self.get_image()
        
        
    def get_image(self):
        response = requests.get("https://mobygames.com/search/quick?q=" + self.name)
        soup = bs(response.text, "html.parser")
        urls = soup.find_all('a', attrs={'href': re.compile("^https://")})
        valid_url = ''
        for i in urls:
            name = i["href"].replace("https://mobygames.com/game/", '')
            temp_name = self.name.replace("'", "-").replace("_", "-").translate(str.maketrans('', '', string.punctuation.replace("-",""))).replace(' ', '-').lower()
            if similar(name, platform_names[self.platform] + "/" + temp_name) > .8:
                valid_url = i["href"]
                #print("valid", valid_url)
                break
        if valid_url:
		        response = requests.get(valid_url)
		        soup = bs(response.content, "html.parser")
		        url = ''
		        images = soup.findAll('img')
		        for img in images:
		            if img.has_attr('src') and "covers" in img["src"]:
		                url = img['src']

		        image_data = requests.get("https://www.mobygames.com" + url).content
		        with open("covers/" + self.name + ".jpg", "wb") as handler:
		            handler.write(image_data)
		            return 1
		            
        else:
		        print(self.name, "Game not found! Check spelling and platform.")

#game = Game("God of War: Ragnarok", 20, "5/5/5/5", "PS5", True, comments="a")
#game.get_image()
WIDTH = 1500
HEIGHT = 700
FPS = 30
# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (125, 125, 125)

COLOR1 = (23, 26, 33)
COLOR2 = (102, 192, 244)
COLOR3 = (27, 40, 56)
COLOR4 = (42, 71, 94)
COLOR5 = (199, 213, 224)

split_names = ["Absorption: ", "Gameplay Balance: ", "Environment: ", "Social/Story: "]

## initialize pygame and create window
pygame.init()

#pygame.scrap.init()
#pygame.scrap.set_mode(SCRAP_CLIPBOARD)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Ratings")
clock = pygame.time.Clock()  ## For syncing the FPS

    
def drawArc(surf, color, center, radius, width, end_angle):
    arc_rect = pygame.Rect(0, 0, radius * 2, radius * 2)
    arc_rect.center = center
    pygame.draw.arc(surf, color, arc_rect, math.pi / 2, math.pi / 2 + end_angle, width)


def blit_text(surface, text, pos, font, color=WHITE):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.


def add_data(dataframe, data):
    new_row = {'Title': data[0], 'Score': data[1], 'Splits': data[2], 'Platform': data[3], 'Finished': data[4],
               'Comments': data[5]}
    df = pd.concat([dataframe, pd.DataFrame.from_records([new_row])], ignore_index=True)
    df.to_csv("updated_data.csv", mode='w+', index=False)
    return (df)


def remove_data(dataframe, name):
    i = dataframe.loc[dataframe['Title'] == name].index
    dataframe.drop(i, inplace=True)
    dataframe.to_csv("updated_data.csv", index=False)
    return (dataframe)

def reload_structures(sort_by):
    data = pd.read_csv("updated_data.csv")
    new_game_list = {}
    new_sorted_list = []
    new_game_rects = {}
    for index, row in data.iterrows():
        new_game = Game(row[0], row[1], row[2], row[3], row[4], row[5])
        new_game_list[row[0]] = new_game
    if sort_by == "alphabetical":
        new_sorted_list = sorted(new_game_list.keys())
    if sort_by == "rating":
        new_sorted_list = sorted(new_game_list.keys(), key=lambda x: new_game_list[x].rating)
        new_sorted_list.reverse()
    for title in new_sorted_list:
        font = pygame.font.Font('freesansbold.ttf', 24)
        width, height = font.size(title)
        n = new_sorted_list.index(title)
        rect = pygame.Rect(23, 16 + (40 * n), width + 4, height + 4)
        text = font.render(title, True, WHITE, COLOR4)
        textRect = text.get_rect()
        textRect.center = (width // 2 + 25, 30 + (40 * n))
        new_game_rects[title] = [rect, textRect, text]


    return (new_game_list, new_sorted_list, new_game_rects)


base_font = pygame.font.Font(None, 32)

input_rect = pygame.Rect(200, 200, 140, 32)
color_active = pygame.Color('chartreuse1')
color_passive = pygame.Color('chartreuse4')
color = color_passive
clock = pygame.time.Clock()
DEFAULT_IMAGE_SIZE = (300, 300)
RADIUS = 70
scroll_count = 0

active = False

## Game loop
running = True
new_entry_active = False
title_active = True
try:
    data = pd.read_csv("updated_data.csv")
except:
    data = pd.DataFrame()
    data = data.append([{"Title": "New Game", "Score": 0, "Splits": "0/0/0/0", "Platform": "PC", "Finished": "N", "Comments": "a"}])
    data.to_csv("updated_data.csv", index=False)
    new_entry_active = True
    title_active = True

game_list = {}

for index, row in data.iterrows():
    game = Game(row[0], row[1], row[2], row[3], row[4], row[5])
    if not isinstance(row[5], str):
        game.comments = "a"
    game_list[row[0]] = game

sorted_games = sorted(game_list.keys(), key=lambda x: game_list[x].rating)
sorted_games.reverse()
game_rects = {}

for title in sorted_games:
    font = pygame.font.Font('freesansbold.ttf', 24)
    width, height = font.size(title)

    n = sorted_games.index(title)
    rect = pygame.Rect(21, 14 + (40 * n), width + 8, height + 8)

    text = font.render(title, True, WHITE, COLOR4)
    textRect = text.get_rect()
    textRect.center = (width // 2 + 25, 30 + (40 * n))

    game_rects[title] = [rect, textRect, text]

plus_list = []
for i in range(4):
    rect = pygame.Rect(WIDTH * .93 - 10, (HEIGHT / 2) - 28 + (40 * i), 41, 35)
    plus_list.append(rect)

minus_list = []
for i in range(4):
    rect = pygame.Rect(WIDTH * .93 + 48, (HEIGHT / 2) - 28 + (40 * i), 36, 35)
    minus_list.append(rect)

temp_stars = [0, 0, 0, 0]
loaded = False
selected_game = game_list[sorted_games[0]]
finished = selected_game.finished

comment_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT - 120, 600, 100)
comment_rect_2 = pygame.Rect(WIDTH // 2 - 298, HEIGHT - 118, 596, 96)

comment_active = False
comment_text = selected_game.comments

new_entry_rect = pygame.Rect(WIDTH * .88 - 97, HEIGHT - 100, 194, 40)
blank_game = Game("New Game", 0, "0/0/0/0", "PC", "N", "")

new_title = selected_game.name
text = font.render(new_title, True, WHITE, COLOR3)
new_title_rect = text.get_rect()
new_title_rect.width *= 2
new_title_rect.width += 8
new_title_rect.height += 36
new_title_rect.center = (WIDTH/2, 100)

delete_rect = pygame.Rect(WIDTH * .88 - 105, HEIGHT - 50, 212, 40)

font = pygame.font.Font('freesansbold.ttf', 32)
platform_text = font.render(selected_game.platform, True, WHITE, COLOR3)
platform_textRect = platform_text.get_rect()
platform_textRect.center = (WIDTH / 2, 150)

platform_rect_l = pygame.Rect(615, 140, 25, 25)
platform_rect_r = pygame.Rect(866, 140, 25, 25)

alpha_rect = pygame.Rect(WIDTH // 2 - 129, 26, 158, 30)
rating_rect = pygame.Rect(WIDTH // 2 + 58, 26, 84, 30)

next_image_rect = pygame.Rect(WIDTH - 271, 25, 182, 30)

sorting_by = "rating"

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if comment_rect.collidepoint(event.pos):
                comment_active = True
                title_active = False
                comment_text = selected_game.comments
            else:
                comment_active = False

            if next_image_rect.collidepoint(event.pos):
                selected_game.next_image()
                loaded = False
                game_list, sorted_games, game_rects = reload_structures(sorting_by)

            if alpha_rect.collidepoint(event.pos):
                game_list, sorted_games, game_rects = reload_structures("alphabetical")
                sorting_by = "alphabetical"
                loaded = False
                selected_game = game_list[sorted_games[0]]

            if rating_rect.collidepoint(event.pos):
                game_list, sorted_games, game_rects = reload_structures("rating")
                sorting_by = "rating"
                loaded = False
                selected_game = game_list[sorted_games[0]]

            if platform_rect_r.collidepoint(event.pos):
                selected_game.platform = platforms[(platforms.index(selected_game.platform) + 1) % len(platforms)]

            if platform_rect_l.collidepoint(event.pos):
                selected_game.platform = platforms[(platforms.index(selected_game.platform) - 1) % len(platforms)]

            if delete_rect.collidepoint(event.pos):
                data = remove_data(data, selected_game.name)
                selected_game = game_list[sorted_games[0]]
                comment_text = selected_game.comments
                game_list, sorted_games, game_rects = reload_structures(sorting_by)
                if len(sorted_games) == 0:
                    data = data.append([{"Title": "New Game", "Score": 0, "Splits": "0/0/0/0", "Platform": "PC",\
                                         "Finished": "N", "Comments": ""}])
                    data.to_csv("updated_data.csv", index=False)
                    new_entry_active = True
                    title_active = True
                    new_title = "New Game"
                    comment_text = ""
                    finished = False
                    game_list, sorted_games, game_rects = reload_structures(sorting_by)
                    selected_game = game_list[sorted_games[0]]
                loaded = False

            if new_entry_rect.collidepoint(event.pos):
                selected_game = Game("New Game", 0, "0/0/0/0", "PC", "N", "")
                new_title = "New Game"
                comment_text = ""
                splits = "0/0/0/0"
                temp_stars = [0, 0, 0, 0]
                loaded = False
                finished = False
                new_entry_active = True
                title_active = True
                font = pygame.font.Font('freesansbold.ttf', 16)
                text = font.render("New Game", True, WHITE, COLOR3)
                commentWidth = text.get_width()
                new_title_rect = pygame.Rect(WIDTH // 2 - (commentWidth * 3) // 2 - 5, 70, (commentWidth * 3) + 10, 60)

            if new_title_rect.collidepoint(event.pos) and new_entry_active:
                title_active = True
                comment_active = False

            if save_rect.collidepoint(event.pos):

                splits = str(temp_stars[0]) + "/" + str(temp_stars[1]) + "/" + str(temp_stars[2]) + "/" + str(
                    temp_stars[3])
                if new_entry_active == True:
                    data = add_data(data, [new_title, sum(temp_stars), splits, selected_game.platform, finished, comment_text])
                    selected_game.name = new_title


                else:
                    selected_game.edit_entry("Splits", splits)
                    selected_game.edit_entry("Score", sum(temp_stars))
                    if not isinstance(comment_text, str):
                        comment_text = "a"
                    if comment_text != "a":
                        if len(comment_text) > 0:
                            selected_game.edit_entry("Comments", comment_text)
                    selected_game.edit_entry("Finished", finished)
                    #selected_game.edit_entry("Title", new_title)
                    selected_game.edit_entry("Platform", selected_game.platform)
                    selected_game.edit_entry("Title", new_title)

                selected_game.comments = comment_text
                selected_game.finished = finished
                try:
                    os.rename("covers/" + selected_game.name + ".jpg", "covers/" + new_title + ".jpg")
                except FileNotFoundError:
                    selected_game.get_image()
                    os.rename("covers/" + selected_game.name + ".jpg", "covers/" + new_title + ".jpg")
                selected_game.name = new_title
                game_list, sorted_games, game_rects = reload_structures(sorting_by)

                selected_game = game_list[selected_game.name]

                if "New Game" in sorted_games:
                    data = remove_data(data, "New Game")
                    game_list, sorted_games, game_rects = reload_structures(sorting_by)
                    selected_game = game_list[sorted_games[0]]
                    comment_text = selected_game.comments

                loaded = False
                new_entry_active = False
                title_active = True
                comment_active = False

            if discard_rect.collidepoint(event.pos):
                comment_text = selected_game.comments
                temp_stars = selected_game.splits
                finished = selected_game.finished
                title_active = True
                comment_active = False

                if new_entry_active:
                    selected_game = game_list[sorted_games[0]]
                    new_entry_active = False
                else:
                    selected_game = game_list[selected_game.name]
                loaded = False

            if finished_rect.collidepoint(event.pos):
                if finished:
                    finished = False
                else:
                    finished = True

            for title in sorted_games:
                if game_rects[title][0].collidepoint(pygame.mouse.get_pos()):
                    selected_game = game_list[title]
                    finished = selected_game.finished
                    loaded = False
                    comment_text = selected_game.comments
                    new_entry_active = False
                    title_active = True
                    new_title = selected_game.name
                    comment_active = False
                    
                    text = font.render(new_title, True, WHITE, COLOR3)
                    new_title_rect = text.get_rect()
                    new_title_rect.width *= 2
                    new_title_rect.width += 8
                    new_title_rect.height += 36
                    new_title_rect.center = (WIDTH/2, 100)

            for i in range(4):
                if plus_list[i].collidepoint(pygame.mouse.get_pos()):
                    if temp_stars[i] < 5:
                        temp_stars[i] += 1

            for i in range(4):
                if minus_list[i].collidepoint(pygame.mouse.get_pos()):
                    if temp_stars[i] > 0:
                        temp_stars[i] -= 1
                        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if comment_active:
                    comment_text = comment_text.replace('|', '', 1)[:-1]
                if title_active:
                    if new_title == "New Game":
                        new_title = ""
                        text = font.render(new_title, True, WHITE, COLOR3)
                        commentWidth = text.get_width()
                        new_title_rect = text.get_rect()
                        new_title_rect.width *= 2
                        new_title_rect.width += 8
                        new_title_rect.height += 36
                        new_title_rect.center = (WIDTH/2, 100)
                    else:
                        new_title = new_title[:-1]
                        text = font.render(new_title, True, WHITE, COLOR3)
                        commentWidth = text.get_width()
                        new_title_rect = text.get_rect()
                        new_title_rect.width *= 2
                        new_title_rect.width += 8
                        new_title_rect.height += 36
                        new_title_rect.center = (WIDTH/2, 100)
                


            else:
                if comment_active:
                    if not isinstance(comment_text, str):
                        comment_text = ""
                    if comment_text == "a" or comment_text == "a|":
                        comment_text = comment_text.replace("a", '', 1)
                    comment_text += event.unicode
                    font = pygame.font.Font('freesansbold.ttf', 16)
                    try:
                        split = comment_text.splitlines()[-1].split()
                        text = font.render(comment_text.splitlines()[-1], True, WHITE, COLOR3)
                    except IndexError:
                        split = comment_text.split()
                        text = font.render(comment_text, True, WHITE, COLOR3)

                    commentWidth = text.get_rect().width

                    temp_text = ""
                    for q in range(len(split)):
                        temp_text += split[q]
                        commentWidth = font.render(temp_text, True, COLOR3, COLOR3).get_rect().width
                        if commentWidth > (comment_rect.width - 180):
                            last_line = ' '.join(split[:q]) + '\n' + ' '.join(split[q:])
                            try:
                                temp = ""
                                for j in comment_text.splitlines()[:-1]:
                                    temp += j
                                    temp += " \n"
                                comment_text = temp + last_line
                            except:
                                comment_text = last_line
                if title_active:
                    if not isinstance(new_title, str):
                        new_title = ""
                    if (event.key == pygame.K_v) and (event.mod & pygame.KMOD_CTRL):
                        if not isinstance(new_title, str):
                            new_title = ""
                        new_title += pygame.scrap.get("text/plain;charset=utf-8").decode("utf-8")
                        font = pygame.font.Font('freesansbold.ttf', 16)
                        text = font.render(new_title, True, WHITE, COLOR3)
                        titleWidth = text.get_width()
                        new_title_rect = pygame.Rect(WIDTH // 2 - (titleWidth * 3) // 2 - 5, 70, (titleWidth * 3) + 10, 60)

                    else:
                    		if new_title == "New Game":
                    				new_title = event.unicode
                    		else:
				                    new_title += event.unicode
				                    font = pygame.font.Font('freesansbold.ttf', 16)
				                    text = font.render(new_title, True, WHITE, COLOR3)
				                    commentWidth = text.get_width()
				                    new_title_rect = pygame.Rect(WIDTH // 2 - (commentWidth * 3) // 2 - 5, 70, (commentWidth * 3) + 10, 60)

        if event.type == MOUSEWHEEL:
            if event.y < 0 and game_rects[sorted_games[-1]][0].y + 30 > HEIGHT:
                for title in sorted_games:
                    game_rects[title][0] = game_rects[title][0].move(0, event.y * 30)
                    game_rects[title][1] = game_rects[title][1].move(0, event.y * 30)
            if event.y > 0 and game_rects[sorted_games[0]][0].y < 16:
                for title in sorted_games:
                    game_rects[title][0] = game_rects[title][0].move(0, event.y * 30)
                    game_rects[title][1] = game_rects[title][1].move(0, event.y * 30)
    screen.fill(COLOR3)

    if new_entry_active == True:
        if title_active:
            pygame.draw.rect(screen, pygame.Color('chartreuse4'), new_title_rect)
        else:
            pygame.draw.rect(screen, WHITE, new_title_rect)
    if title_active:
        pygame.draw.rect(screen, pygame.Color('chartreuse4'), new_title_rect)
    try:
    	image = pygame.image.load(selected_game.image)
    except FileNotFoundError:
    	selected_game.get_image()
    	image = pygame.image.load(selected_game.image)
    	
    width = image.get_width()
    height = image.get_height()

    if (width * height) > (DEFAULT_IMAGE_SIZE[0] * DEFAULT_IMAGE_SIZE[1]):
        while (width * height) > (DEFAULT_IMAGE_SIZE[0] * DEFAULT_IMAGE_SIZE[1]):
            width *= .99
            height *= .99

    if (width * height) < (DEFAULT_IMAGE_SIZE[0] * DEFAULT_IMAGE_SIZE[1]):
        while (width * height) < (DEFAULT_IMAGE_SIZE[0] * DEFAULT_IMAGE_SIZE[1]):
            width *= 1.01
            height *= 1.01

    image = pygame.transform.scale(image, (round(width), round(height)))
    screen.blit(image, (WIDTH // 2 - round(width) // 2, HEIGHT // 2 - round(height) // 2))

    font = pygame.font.Font('freesansbold.ttf', 32)
    platform_text = font.render(selected_game.platform, True, WHITE, COLOR3)
    platform_textRect = platform_text.get_rect()
    platform_textRect.center = (WIDTH / 2, 150)
    screen.blit(platform_text, platform_textRect)

    platform_rect_l = pygame.Rect(615, 140, 25, 25)
    platform_rect_r = pygame.Rect(866, 140, 25, 25)

    pygame.draw.rect(screen, COLOR3, platform_rect_l)
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("<", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (625, 150)
    screen.blit(text, textRect)

    pygame.draw.rect(screen, COLOR3, platform_rect_r)
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(">", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (876, 150)
    screen.blit(text, textRect)

    for title in sorted_games:
        pygame.draw.rect(screen, COLOR4, game_rects[title][0])
        screen.blit(game_rects[title][2], game_rects[title][1])

    if title_active:
        font = pygame.font.Font('freesansbold.ttf', 48)
        text = font.render(new_title, True, WHITE, COLOR3)
        textRect = text.get_rect()
        textRect.center = (WIDTH / 2, 100)
        screen.blit(text, textRect)

    else:
        font = pygame.font.Font('freesansbold.ttf', 48)
        text = font.render(selected_game.name, True, WHITE, COLOR3)
        textRect = text.get_rect()
        textRect.center = (WIDTH / 2, 100)
        screen.blit(text, textRect)

    for rect in plus_list:
        pygame.draw.rect(screen, pygame.Color('GREEN'), rect)
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(" + ", True, pygame.Color('GREEN'), COLOR3)
        textRect = text.get_rect()
        textRect.center = (rect.x + 20, rect.y + 18)
        screen.blit(text, textRect)

    for rect in minus_list:
        pygame.draw.rect(screen, pygame.Color('RED'), rect)
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(" - ", True, pygame.Color('RED'), COLOR3)
        textRect = text.get_rect()
        textRect.center = (rect.x + 18, rect.y + 18)
        screen.blit(text, textRect)

    if comment_active:
        comment_color = pygame.Color('chartreuse4')
    else:
        comment_color = WHITE

    pygame.draw.rect(screen, comment_color, comment_rect)
    pygame.draw.rect(screen, COLOR3, comment_rect_2)

    font = pygame.font.Font('freesansbold.ttf', 16)
    text = font.render("Comments:", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (comment_rect.x + textRect.width // 2, comment_rect.y - 20)
    screen.blit(text, textRect)

    if comment_active:
        if time.time() % 1 >= 0.5:
            try:
                comment_text = comment_text.replace('|', '', 1)
            except AttributeError:
                comment_text = ""
        else:
            try:
                comment_text = comment_text.replace('|', '', 1)
                comment_text += '|'
            except AttributeError:
                comment_text = '|'

    for n in range(len(selected_game.splits)):
        if loaded == False:
            stars = selected_game.splits[n]
            temp_stars[n] = stars
            if n == len(selected_game.splits) - 1:
                loaded = True
        name = split_names[n]
        star = pygame.image.load("star.png").convert_alpha()
        star = pygame.transform.scale(star, (30, 30))

        empty_stars = 5 - temp_stars[n]
        empty_star = pygame.image.load("empty_star.png").convert_alpha()
        empty_star = pygame.transform.scale(empty_star, (30, 30))

        font = pygame.font.Font('freesansbold.ttf', 24)
        text = font.render(name, True, WHITE, COLOR3)
        textRect = text.get_rect()
        textRect.center = (WIDTH * .75, (HEIGHT / 2) - 8 + (40 * n))
        screen.blit(text, textRect)

        for i in range(temp_stars[n]):
            screen.blit(star, (WIDTH * .83 + (i * 25), (HEIGHT / 2) - 25 + (40 * n)))

        for j in range(empty_stars):
            screen.blit(empty_star, (WIDTH * .83 + (temp_stars[n] * 25) + (j * 25), (HEIGHT / 2) - 25 + (40 * n)))

    score = sum(temp_stars) * 5

    red = (100 - score) / 25

    if score <= 75:
        red = 255
        if score <= 50:
            green = 0
        else:
            green = ((75 - score) / 25) * 255
    if score >= 75:
        green = 255
        red = ((100 - score) / 25) * 255

    color = (red, green, 0)
    drawArc(screen, color, (WIDTH * .88, 150), RADIUS, 10, 6.28 * (score / 100))

    font = pygame.font.Font('freesansbold.ttf', 48)
    text = font.render(str(sum(temp_stars)), True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (WIDTH * .88, 150)
    screen.blit(text, textRect)

    save_rect = pygame.Rect(WIDTH * .88 - 130, HEIGHT - 200, 255, 40)
    pygame.draw.rect(screen, COLOR2, save_rect)

    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(" Save Changes ", True, WHITE, pygame.Color("chartreuse4"))
    textRect = text.get_rect()
    textRect.center = (save_rect.x + save_rect.width / 2, save_rect.y + save_rect.height / 2)
    screen.blit(text, textRect)

    discard_rect = pygame.Rect(WIDTH * .88 - 150, HEIGHT - 150, 300, 40)
    pygame.draw.rect(screen, COLOR2, discard_rect)

    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(" Discard Changes ", True, WHITE, pygame.Color("firebrick3"))
    textRect = text.get_rect()
    textRect.center = (discard_rect.x + discard_rect.width / 2, discard_rect.y + discard_rect.height / 2)
    screen.blit(text, textRect)

    finished_rect = pygame.Rect(WIDTH * .94, 250, 45, 35)
    pygame.draw.rect(screen, WHITE, finished_rect)

    pygame.draw.rect(screen, COLOR2, new_entry_rect)
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(" New Game ", True, WHITE, COLOR4)
    textRect = text.get_rect()
    textRect.center = (new_entry_rect.x + new_entry_rect.width / 2, new_entry_rect.y + new_entry_rect.height / 2)
    screen.blit(text, textRect)

    font = pygame.font.Font('freesansbold.ttf', 32)
    if finished:
        text = font.render(" X ", True, pygame.Color('chartreuse2'), COLOR3)
    else:
        text = font.render("    ", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (finished_rect.x + finished_rect.width / 2, finished_rect.y + finished_rect.height / 2)
    screen.blit(text, textRect)

    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("Finished?", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (finished_rect.x - textRect.width / 2 - 30, finished_rect.y + finished_rect.height / 2)
    screen.blit(text, textRect)

    layer1 = pygame.Surface((comment_rect.width, comment_rect.height))
    layer1.fill(COLOR3)

    font = pygame.font.Font('freesansbold.ttf', 20)
    if comment_text != "a" and comment_text != "a|":
        try:
            blit_text(screen, comment_text, (comment_rect.x + 8, comment_rect.y + 8), font, WHITE)
        except:
            pass

    pygame.draw.rect(screen, COLOR2, delete_rect)
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("Delete Game", True, WHITE, RED)
    textRect = text.get_rect()
    textRect.center = (delete_rect.x + textRect.width / 2 + 5, delete_rect.y + textRect.height / 2 + 5)
    screen.blit(text, textRect)

    font = pygame.font.Font('freesansbold.ttf', 24)
    text = font.render("Sort By:", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (WIDTH // 2 - 200, 40)
    screen.blit(text, textRect)

    if sorting_by == "alphabetical":
        pygame.draw.rect(screen, COLOR2, alpha_rect)
    else:
        pygame.draw.rect(screen, WHITE, alpha_rect)
    font = pygame.font.Font('freesansbold.ttf', 24)
    text = font.render("Alphabetical", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (WIDTH // 2 - 50, 40)
    screen.blit(text, textRect)

    if sorting_by == "rating":
        pygame.draw.rect(screen, COLOR2, rating_rect)
    else:
        pygame.draw.rect(screen, WHITE, rating_rect)
    font = pygame.font.Font('freesansbold.ttf', 24)
    text = font.render("Rating", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (WIDTH // 2 + 100, 40)
    screen.blit(text, textRect)

    pygame.draw.rect(screen, COLOR2, next_image_rect)
    font = pygame.font.Font('freesansbold.ttf', 24)
    text = font.render("Update Image?", True, WHITE, COLOR3)
    textRect = text.get_rect()
    textRect.center = (WIDTH - 180, 40)
    screen.blit(text, textRect)

    pygame.display.flip()

pygame.quit()
