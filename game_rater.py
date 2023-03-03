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
import Game
import multiprocessing as mp
from threading import Thread

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
    "PS5": "https://www.mobygames.com/game/playstation-5/",
    "Nintendo Switch": "https://www.mobygames.com/game/nintendo-switch/",
    "DS": "https://www.mobygames.com/game/nintendo-ds/"
    
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

#game = Game("The Elder Scrolls V: Skyrim", 20, "0/0/0/0", "PC", True)
#game.get_image()
#os._exit()
# Global Params
WIDTH = 1500
HEIGHT = 700
FPS = 30
DEFAULT_IMAGE_SIZE = (280, 280)
RADIUS = 70
split_names = ["Absorption: ", "Gameplay Balance: ", "Environment: ", "Social/Story: "]

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

# Initial States
alpha_toggle = False
rating_toggle = False
scroll_count = 0
running = True
new_entry_active = False
title_active = True
sorting_by = "rating"
comment_active = False
loaded = False
temp_stars = [0, 0, 0, 0]

## initialize pygame and create window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE, pygame.FULLSCREEN)
pygame.display.set_caption("Game Ratings")
clock = pygame.time.Clock()  ## For syncing the FPS

# Define Fonts
FONT1 = pygame.font.Font('freesansbold.ttf', 16)
FONT2 = pygame.font.Font('freesansbold.ttf', 20)
FONT3 = pygame.font.Font('freesansbold.ttf', 24)
FONT4 = pygame.font.Font('freesansbold.ttf', 32)
FONT5 = pygame.font.Font('freesansbold.ttf', 48)

color_active = pygame.Color('chartreuse1')
color_passive = pygame.Color('chartreuse4')
color = color_passive

# Create rectangle objects for each of the buttons on the screen
comment_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT - 120, 600, 100)
comment_rect_2 = pygame.Rect(WIDTH // 2 - 298, HEIGHT - 118, 596, 96)

delete_rect = pygame.Rect(WIDTH * .88 - 105, HEIGHT - 50, 212, 40)

platform_rect_l = pygame.Rect(WIDTH // 2 - 160, 140, 25, 25)
platform_rect_r = pygame.Rect(WIDTH // 2 + 138, 140, 25, 25)

new_entry_rect = pygame.Rect(WIDTH * .88 - 97, HEIGHT - 100, 194, 40)

alpha_rect = pygame.Rect(WIDTH // 2 - 129, 26, 158, 30)
rating_rect = pygame.Rect(WIDTH // 2 + 58, 26, 84, 30)

finished_rect = pygame.Rect(WIDTH * .94, 250, 45, 35)

discard_rect = pygame.Rect(WIDTH * .88 - 150, HEIGHT - 150, 300, 40)

save_rect = pygame.Rect(WIDTH * .88 - 130, HEIGHT - 200, 255, 40)

next_image_rect = pygame.Rect(WIDTH - 271, 15, 182, 30)

next_cover_rect = pygame.Rect(WIDTH - 271, 50, 182, 30)

## Game loop
# Read in data from CSV, if NaN, create empty CSV
try:
    data = pd.read_csv("updated_data.csv")
except:
    data = pd.DataFrame()
    data = data.append([{"Title": "New Game", "Score": 0, "Splits": "0/0/0/0", "Platform": "PC", "Finished": "N", "Comments": "a"}])
    data.to_csv("updated_data.csv", index=False)
    new_entry_active = True
    title_active = True

game_list = {}
args_list = []

def create_game(arg_list):
    row[0], row[1], row[2], row[3], row[4], row[5] = arg_list[0], arg_list[1], arg_list[2], arg_list[3], arg_list[4], arg_list[5]
    game = Game.Game(row[0], row[1], row[2], row[3], row[4], row[5])
    if not isinstance(row[5], str):
        game.comments = "a"
    return game
    
# Populate game dictionary with CSV data
for index, row in data.iterrows():
    args_list.append([row[0], row[1], row[2], row[3], row[4], row[5]])

new_args_list = sorted(args_list,key=lambda x: x[1])
new_args_list.reverse()
num_workers = mp.cpu_count()  
with mp.Pool(num_workers) as mp_pool:
    try:
        results = mp_pool.imap(create_game, new_args_list)
        for i in results:
            game_list[i.name] = i
            #print(i.name)
    except:
        mp_pool.close()



# List of game names for sorting purposes. Either alphabetical or by rating
sorted_games = sorted(game_list.keys(), key=lambda x: game_list[x].rating)
sorted_games.reverse()

# Define list of the pygame.rect objects for each game in the list of games
game_rects = {}
for title in sorted_games:
    font = FONT3
    width, height = font.size(title)

    n = sorted_games.index(title)
    rect = pygame.Rect(21, 14 + (40 * n), width + 8, height + 8)

    text = font.render(title, True, WHITE, COLOR4)
    textRect = text.get_rect()
    textRect.center = (width // 2 + 25, 30 + (40 * n))

    game_rects[title] = [rect, textRect, text]

# Create rectangle objects for rating plus sign buttons
plus_list = []
for i in range(4):
    rect = pygame.Rect(WIDTH * .93 - 10, (HEIGHT / 2) - 28 + (40 * i), 42, 35)
    plus_list.append(rect)

# Create rectangle objects for rating minus sign buttons
minus_list = []
for i in range(4):
    rect = pygame.Rect(WIDTH * .93 + 48, (HEIGHT / 2) - 28 + (40 * i), 36, 35)
    minus_list.append(rect)

# Select the first game to be rendered from the top of the list
# Initialize the name, finished status, and platform of the selected game
selected_game = game_list[sorted_games[0]]
finished = selected_game.finished

new_title = selected_game.name
text = font.render(new_title, True, WHITE, COLOR3)
new_title_rect = text.get_rect()
new_title_rect.width = FONT5.size(new_title)[0]
new_title_rect.width += 12
new_title_rect.height += 36
new_title_rect.center = (WIDTH/2, 100)

font = FONT4
platform_text = font.render(selected_game.platform, True, WHITE, COLOR3)
platform_textRect = platform_text.get_rect()
platform_textRect.center = (WIDTH / 2, 150)

comment_text = selected_game.comments

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

def reload_structures(sort_by, reverse=False):
    data = pd.read_csv("updated_data.csv")
    new_sorted_list = []
    new_game_rects = {}
    if sort_by == "alphabetical":
        new_sorted_list = sorted(game_list.keys())
    if sort_by == "rating":
        new_sorted_list = sorted(game_list.keys(), key=lambda x: game_list[x].rating)
        new_sorted_list.reverse()
    if reverse:
        new_sorted_list.reverse()
    for title in new_sorted_list:
        font = FONT3
        width, height = font.size(title)
        n = new_sorted_list.index(title)
        rect = pygame.Rect(23, 16 + (40 * n), width + 4, height + 4)
        text = font.render(title, True, WHITE, COLOR4)
        textRect = text.get_rect()
        textRect.center = (width // 2 + 25, 30 + (40 * n))
        new_game_rects[title] = [rect, textRect, text]

    return (new_sorted_list, new_game_rects)

def clear_folder(dir):
    if os.path.exists(dir):
        for the_file in os.listdir(dir):
            file_path = os.path.join(dir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                else:
                    clear_folder(file_path)
                    os.rmdir(file_path)
            except Exception as e:
                print(e)
                
def get_file_count(directory):
    count = 0

    for entry in os.scandir(directory):
        if entry.is_file():
            count += 1

        elif entry.is_dir():
            count += get_file_count(os.path.join(directory, entry.name))

    return count
    
    
def draw_text_rect(rect_color, rectangle, font, text, text_color, text_background, center):
    if rect_color is not None and rectangle is not None:
        pygame.draw.rect(screen, rect_color, rectangle)
    text = font.render(text, True, text_color, text_background)
    textRect = text.get_rect()
    textRect.center = center
    screen.blit(text, textRect)

while running:
    WIDTH, HEIGHT = pygame.display.get_surface().get_size()
    # Create rectangle objects for rating plus sign buttons
    plus_list = []
    for i in range(4):
        rect = pygame.Rect(WIDTH * .93 - 10, (HEIGHT / 2) - 28 + (40 * i), 42, 35)
        plus_list.append(rect)

    # Create rectangle objects for rating minus sign buttons
    minus_list = []
    for i in range(4):
        rect = pygame.Rect(WIDTH * .93 + 48, (HEIGHT / 2) - 28 + (40 * i), 36, 35)
        minus_list.append(rect)

    text = font.render(new_title, True, WHITE, COLOR3)
    new_title_rect = text.get_rect()
    new_title_rect.width = FONT5.size(new_title)[0]
    new_title_rect.width += 12
    new_title_rect.height += 36
    new_title_rect.center = (WIDTH/2, 100)

    font = FONT4
    platform_text = font.render(selected_game.platform, True, WHITE, COLOR3)
    platform_textRect = platform_text.get_rect()
    platform_textRect.center = (WIDTH / 2, 150)


    # Create rectangle objects for each of the buttons on the screen
    comment_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT - 120, 600, 100)
    comment_rect_2 = pygame.Rect(WIDTH // 2 - 298, HEIGHT - 118, 596, 96)

    #comment_text = selected_game.comments

    delete_rect = pygame.Rect(WIDTH * .88 - 105, HEIGHT - 50, 212, 40)

    platform_rect_l = pygame.Rect(WIDTH // 2 - 160, 140, 25, 25)
    platform_rect_r = pygame.Rect(WIDTH // 2 + 138, 140, 25, 25)

    new_entry_rect = pygame.Rect(WIDTH * .88 - 97, HEIGHT - 100, 194, 40)

    alpha_rect = pygame.Rect(WIDTH // 2 - 129, 26, 158, 30)
    rating_rect = pygame.Rect(WIDTH // 2 + 58, 26, 84, 30)

    finished_rect = pygame.Rect(WIDTH * .92, 270, 45, 35)

    discard_rect = pygame.Rect(WIDTH * .88 - 150, HEIGHT - 150, 300, 40)

    save_rect = pygame.Rect(WIDTH * .88 - 130, HEIGHT - 200, 255, 40)
    # For each clock tick, process logic first:
    # Check for any keyboard/mouse events
    # Execute function related to mouse/keyboard click, scroll, or press
    # Draw the updated state
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Left Click Events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # If comment box is clicked, set the box to active and load the game's comments to be
            # viewed or edited. If already active when clicked, deactivate. Comment active and title
            # active are mutually exclusive so that text isn't typed to both at the same time.
            if comment_rect.collidepoint(event.pos):
                comment_active = True
                title_active = False
                comment_text = selected_game.comments
            else:
                comment_active = False
            # If alphabetical is clicked, reload data structures to be sorted alphabetically.
            # If sorting was already done alphabetically, reverse the order.
            # After sorting, select the first game in the list and render the title appropriately
            
            if next_image_rect.collidepoint(event.pos):
                selected_game.next_image()
                #game_list, sorted_games, game_rects = reload_structures(sorting_by)

            if next_cover_rect.collidepoint(event.pos):
                selected_game.next_cover()
                #game_list, sorted_games, game_rects = reload_structures(sorting_by)


            if alpha_rect.collidepoint(event.pos):
                if sorting_by == "rating":
                    sorted_games, game_rects = reload_structures("alphabetical")
                    sorting_by = "alphabetical"
                    loaded = False
                    selected_game = game_list[sorted_games[0]]
                    comment_text = selected_game.comments
                    new_title = selected_game.name
                    text = font.render(new_title, True, WHITE, COLOR3)
                    new_title_rect = text.get_rect()
                    new_title_rect.width = FONT5.size(new_title)[0]
                    new_title_rect.width += 12
                    new_title_rect.height += 36
                    new_title_rect.center = (WIDTH/2, 100)
                else:
                    alpha_toggle = not alpha_toggle
                    sorted_games, game_rects = reload_structures("alphabetical", alpha_toggle)
                    sorting_by = "alphabetical"
                    loaded = False
                    selected_game = game_list[sorted_games[0]]
                    comment_text = selected_game.comments
                    new_title = selected_game.name
                    text = font.render(new_title, True, WHITE, COLOR3)
                    new_title_rect = text.get_rect()
                    new_title_rect.width = FONT5.size(new_title)[0]
                    new_title_rect.width += 12
                    new_title_rect.height += 36
                    new_title_rect.center = (WIDTH/2, 100)
                    
            # Same as the alphabetical section above. Sorts by rating instead of alphabetically
            # and reverses the order if already selected. Selects the first game and renders the title
            if rating_rect.collidepoint(event.pos):
                if sorting_by == "alphabetical":
                    sorted_games, game_rects = reload_structures("rating")
                    sorting_by = "rating"
                    loaded = False
                    selected_game = game_list[sorted_games[0]]
                    comment_text = selected_game.comments
                    new_title = selected_game.name
                    text = font.render(new_title, True, WHITE, COLOR3)
                    new_title_rect = text.get_rect()
                    new_title_rect.width = FONT5.size(new_title)[0]
                    new_title_rect.width += 12
                    new_title_rect.height += 36
                    new_title_rect.center = (WIDTH/2, 100)
                else:
                    rating_toggle = not rating_toggle
                    sorted_games, game_rects = reload_structures("rating", rating_toggle)
                    sorting_by = "rating"
                    loaded = False
                    selected_game = game_list[sorted_games[0]]
                    comment_text = selected_game.comments
                    new_title = selected_game.name
                    text = font.render(new_title, True, WHITE, COLOR3)
                    new_title_rect = text.get_rect()
                    new_title_rect.width = FONT5.size(new_title)[0]
                    new_title_rect.width += 12
                    new_title_rect.height += 36
                    new_title_rect.center = (WIDTH/2, 100)
            
            # If either of the arrow keys adjacent to the platform are clicked, switch the currently
            # selected game platform
            if platform_rect_r.collidepoint(event.pos):
                selected_game.platform = platforms[(platforms.index(selected_game.platform) + 1) % len(platforms)]

            if platform_rect_l.collidepoint(event.pos):
                selected_game.platform = platforms[(platforms.index(selected_game.platform) - 1) % len(platforms)]

            # If the delete game button is pressed, remove the entry from the csv file
            # Remove the entry from all of the data structures. If this causes the data
            # Structures to be empty, populate with a blank game to be edited
            if delete_rect.collidepoint(event.pos):
                data = remove_data(data, selected_game.name.replace(":", ""))
                game_list.pop(selected_game.name)
                clear_folder("covers/" + selected_game.name.replace(":", ""))
                os.rmdir("covers/" + selected_game.name.replace(":", ""))
                popped_game = sorted_games.index(selected_game.name)
                sorted_games.remove(selected_game.name)
                game_rects.pop(selected_game.name)
                
                for g in sorted_games[popped_game:]:
                    game_rects[g][0] = game_rects[g][0].move(0, -40)
                    game_rects[g][1] = game_rects[g][1].move(0, -40)
                selected_game = game_list[sorted_games[popped_game]]
                comment_text = selected_game.comments
                #sorted_games, game_rects = reload_structures(sorting_by)
                if len(sorted_games) == 0:
                    data = data.append([{"Title": "New Game", "Score": 0, "Splits": "0/0/0/0", "Platform": "PC",\
                                         "Finished": "N", "Comments": ""}])
                    data.to_csv("updated_data.csv", index=False)
                    new_entry_active = True
                    title_active = True
                    new_title = "New Game"
                    comment_text = ""
                    finished = False
                    game_list["New Game"] = Game.Game("New Game", 0, "0/0/0/0", "PC", False)
                    sorted_games, game_rects = reload_structures(sorting_by)
                    selected_game = game_list[sorted_games[0]]
                new_title = selected_game.name
                text = font.render(new_title, True, WHITE, COLOR3)
                new_title_rect = text.get_rect()
                new_title_rect.width = FONT5.size(new_title)[0]
                new_title_rect.width += 12
                new_title_rect.height += 36
                new_title_rect.center = (WIDTH/2, 100)
                loaded = False

            # If the new entry button is clicked, create a blank game template to be filled out
            # Reset all of the titles, comments, ratings, booleans, etc.
            if new_entry_rect.collidepoint(event.pos):
                selected_game = Game.Game("New Game", 0, "0/0/0/0", "PC", "N", "")
                new_title = "New Game"
                comment_text = ""
                splits = "0/0/0/0"
                temp_stars = [0, 0, 0, 0]
                loaded = False
                finished = False
                new_entry_active = True
                title_active = True
                font = FONT1
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
                    selected_game.rating = sum(temp_stars)
                    selected_game.splits = temp_stars

                else:
                    selected_game.edit_entry("Splits", splits)
                    selected_game.edit_entry("Score", sum(temp_stars))
                    if not isinstance(comment_text, str):
                        comment_text = "a"
                    if comment_text != "a":
                        if len(comment_text) > 0:
                            selected_game.edit_entry("Comments", comment_text)
                    selected_game.edit_entry("Finished", finished)
                    selected_game.edit_entry("Title", new_title)
                    selected_game.edit_entry("Platform", selected_game.platform)
                    selected_game.edit_entry("Title", new_title)

                selected_game.comments = comment_text
                selected_game.finished = finished
                selected_game.rating = sum(temp_stars)
                
                if not new_entry_active:
                    try:
                        os.rename("covers/" + selected_game.name.replace(":", '') + "/" + str(selected_game.image_index) + "/" + str(selected_game.cover_index) + ".jpg",
                                  "covers/" + new_title.replace(":", '') + "/" + str(selected_game.image_index) + "/temp.jpg")
                                  
                        os.rename("covers/" + new_title.replace(":", '') + "/" + str(selected_game.image_index) + "/0.jpg",
                                  "covers/" + new_title.replace(":", '') + "/" + str(selected_game.image_index) + "/" + str(selected_game.cover_index) + ".jpg")
                                  
                        os.rename("covers/" + new_title.replace(":", '') + "/" + str(selected_game.image_index) + "/temp.jpg",
                                  "covers/" + new_title.replace(":", '') + "/" + str(selected_game.image_index) + "/0.jpg")
                        selected_game.cover_index = 0
                        selected_game.image = "covers/" + selected_game.name.replace(":", "") + "/" + str(selected_game.image_index) + "/" + str(selected_game.cover_index) + ".jpg"
                    
                    except FileNotFoundError:
                        pass
                                 
                    
                else:
                    image = pygame.image.load("covers/New Game/0/0.jpg")
                    clear_folder("covers/" + selected_game.name.replace(":", "") + "/")
                    p = mp.Process(target=selected_game.get_image)
                    p.start()
                    selected_game.image = "covers/" + selected_game.name.replace(":", "") + "/" + str(selected_game.image_index) + "/" + str(selected_game.cover_index) + ".jpg"
                    found = False
                    while not found:
                        try:
                            image = pygame.image.load(selected_game.image)
                        except:
                            continue
                        found = True
                game_list[selected_game.name] = selected_game
 
                try:
                    if sorting_by == "alphabetical":
                        inserted_game = sorted_games.index(selected_game.name)
                        if sorted_games[0] < sorted_games[-1]:
                            sorted_games.append(selected_game.name)
                            sorted_games.sort()
                        else:
                            sorted_games.append(selected_game.name)
                            sorted_games.sort()
                            sorted_games.reverse()
                    else:
                        if game_list[sorted_games[0]].rating < game_list[sorted_games[-1]].rating:
                            for i in range(len(sorted_games)):
                                if selected_game.rating < game_list[sorted_games[i]].rating:
                                    inserted_game = i
                                    break
                            sorted_games.append(selected_game.name)
                            sorted_games.sort(key = lambda x: game_list[x].rating)
                        else:
                            for i in range(len(sorted_games)):
                                if selected_game.rating > game_list[sorted_games[i]].rating:
                                    inserted_game = i
                                    break
                            sorted_games.append(selected_game.name)
                            sorted_games.sort(key = lambda x: game_list[x].rating)
                            sorted_games.reverse()
                except IndexError:
                    pass
                
                next_game = sorted_games[sorted_games.index(selected_game.name)+1]
                next_game_index = list(game_rects.keys()).index(next_game)
                font = FONT3
                width, height = font.size(selected_game.name)
                n = game_rects[next_game]
                rect = pygame.Rect(21, n[0].y, width + 8, height + 8)
                text = font.render(selected_game.name, True, WHITE, COLOR4)
                textRect = text.get_rect()
                textRect.center = (width // 2 + 25, n[1].centery)
                game_rects[selected_game.name] = [rect, textRect, text]


                for g in list(game_rects.keys())[next_game_index:]:
                    game_rects[g][0] = game_rects[g][0].move(0, 40)
                    game_rects[g][1] = game_rects[g][1].move(0, 40)
                    
                for y in list(game_rects.keys()):
                    print(y, game_rects[y][0].x, game_rects[y][0].y)

                selected_game = game_list[selected_game.name]

                if "New Game" in sorted_games:
                    data = remove_data(data, "New Game")
                    sorted_games, game_rects = reload_structures(sorting_by)
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
                new_title = selected_game.name
                text = font.render(new_title, True, WHITE, COLOR3)
                new_title_rect = text.get_rect()
                new_title_rect.width = FONT5.size(new_title)[0]
                new_title_rect.width += 12
                new_title_rect.height += 36
                new_title_rect.center = (WIDTH/2, 100)
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
                    new_title_rect.width = FONT5.size(new_title)[0]
                    new_title_rect.width += 12
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
                        new_title_rect.width = FONT5.size(new_title)[0]
                        new_title_rect.width += 12
                        new_title_rect.height += 36
                        new_title_rect.center = (WIDTH/2, 100)
                    else:
                        new_title = new_title[:-1]
                        text = font.render(new_title, True, WHITE, COLOR3)
                        commentWidth = text.get_width()
                        new_title_rect = text.get_rect()
                        new_title_rect.width = FONT5.size(new_title)[0]
                        new_title_rect.width += 12
                        new_title_rect.height += 36
                        new_title_rect.center = (WIDTH/2, 100)
                


            else:
                if comment_active:
                    if not isinstance(comment_text, str):
                        comment_text = ""
                    if comment_text == "a" or comment_text == "a|":
                        comment_text = comment_text.replace("a", '', 1)
                    comment_text += event.unicode
                    font = FONT1
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
                        font = FONT1
                        text = font.render(new_title, True, WHITE, COLOR3)
                        titleWidth = text.get_width()
                        new_title_rect = pygame.Rect(WIDTH // 2 - (titleWidth * 3) // 2 - 5, 70, (titleWidth * 3) + 10, 60)

                    else:
                            if new_title == "New Game":
                                    new_title = event.unicode
                            else:
                                    new_title += event.unicode
                                    font = FONT1
                                    text = font.render(new_title, True, WHITE, COLOR3)
                                    commentWidth = text.get_width()
                                    new_title_rect = pygame.Rect(WIDTH // 2 - (commentWidth * 3) // 2 - 5, 70, (commentWidth * 3) + 10, 60)

        if event.type == MOUSEWHEEL and event.type != MOUSEBUTTONDOWN:
            if event.y < 0 and game_rects[sorted_games[-1]][0].y + 30 > HEIGHT:
                for title in sorted_games:
                    game_rects[title][0] = game_rects[title][0].move(0, event.y * 30)
                    game_rects[title][1] = game_rects[title][1].move(0, event.y * 30)
            if event.y > 0 and game_rects[sorted_games[0]][0].y < 16:
                for title in sorted_games:
                    game_rects[title][0] = game_rects[title][0].move(0, event.y * 30)
                    game_rects[title][1] = game_rects[title][1].move(0, event.y * 30)
                    
                    
    screen.fill(COLOR3)
    
    for title in sorted_games:
        pygame.draw.rect(screen, COLOR4, game_rects[title][0])
        screen.blit(game_rects[title][2], game_rects[title][1])
        
    if title_active:
        pygame.draw.rect(screen, pygame.Color('chartreuse4'), new_title_rect)
    else:
        if new_entry_active == True:
            pygame.draw.rect(screen, WHITE, new_title_rect)
            
    if get_file_count("covers/" + selected_game.name.replace(":", "")) > 0:
        image = pygame.image.load(selected_game.image)
    else:
        image = pygame.image.load("covers/New Game/0/0.jpg")
        clear_folder("covers/" + selected_game.name.replace(":", "") + "/")
        p = mp.Process(target=selected_game.get_image)
        p.start()
        selected_game.image = "covers/" + selected_game.name.replace(":", "") + "/" + str(selected_game.image_index) + "/" + str(selected_game.cover_index) + ".jpg"
        found = False
        while not found:
            try:
                image = pygame.image.load(selected_game.image)
            except:
                continue
            found = True
        
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

    draw_text_rect(None, None, FONT4, selected_game.platform, WHITE, COLOR3, (WIDTH / 2, 150))

    draw_text_rect(COLOR3, platform_rect_l, FONT4, "<", WHITE, COLOR3, (WIDTH // 2 - 150, 150))

    draw_text_rect(COLOR3, platform_rect_r, FONT4, ">", WHITE, COLOR3, (WIDTH // 2 + 150, 150))

    if title_active:
        draw_text_rect(None, None, FONT5, new_title, WHITE, COLOR3, (WIDTH / 2, 100))

    else:
        draw_text_rect(None, None, FONT5, new_title, WHITE, COLOR3, (WIDTH / 2, 100))

    for rect in plus_list:
        draw_text_rect(pygame.Color('GREEN'), rect, FONT4, " + ", pygame.Color('GREEN'), COLOR3, (rect.x + 20, rect.y + 17))

    for rect in minus_list:
        draw_text_rect(pygame.Color('RED'), rect, FONT4, " - ", pygame.Color('RED'), COLOR3, (rect.x + 18, rect.y + 18))

    if comment_active:
        comment_color = pygame.Color('chartreuse4')
    else:
        comment_color = WHITE

    pygame.draw.rect(screen, comment_color, comment_rect)
    draw_text_rect(COLOR3, comment_rect_2, FONT1, "Comments:", WHITE, COLOR3, (comment_rect.x + textRect.width // 2, comment_rect.y - 20))
    

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

        draw_text_rect(None, None, FONT3, name, WHITE, COLOR3, (WIDTH * .75, (HEIGHT / 2) - 8 + (40 * n)))

        for i in range(temp_stars[n]):
            screen.blit(star, (WIDTH * .83 + (i * 25), (HEIGHT / 2) - 25 + (40 * n)))

        for j in range(empty_stars):
            screen.blit(empty_star, (WIDTH * .83 + (temp_stars[n] * 25) + (j * 25), (HEIGHT / 2) - 25 + (40 * n)))

    score = sum(temp_stars) * 5
    
    green = 0
    if score < 50:
        green = 255 * (score / 100)
    else:
        green = 255

    red = 255
    if score > 50:
        red = 255 * (abs(score - 100) / 50)
    color = (red, green, 0)
    drawArc(screen, color, (WIDTH * .88, 170), RADIUS, 10, 6.28 * (score / 100))

    draw_text_rect(None, None, FONT5, str(sum(temp_stars)), WHITE, COLOR3, (WIDTH * .88, 170))
    
    draw_text_rect(COLOR2, save_rect, FONT4, " Save Changes ", WHITE, pygame.Color("chartreuse4"), (save_rect.x + save_rect.width / 2, save_rect.y + save_rect.height / 2))
    
    draw_text_rect(COLOR2, discard_rect, FONT4, " Discard Changes ", WHITE, pygame.Color("firebrick3"), (discard_rect.x + discard_rect.width / 2, discard_rect.y + discard_rect.height / 2))

    draw_text_rect(COLOR2, new_entry_rect, FONT4, " New Game ", WHITE, COLOR4, (new_entry_rect.x + new_entry_rect.width / 2, new_entry_rect.y + new_entry_rect.height / 2))

    if finished:
        draw_text_rect(WHITE, finished_rect, FONT4, " X ", pygame.Color('chartreuse2'), COLOR3, (finished_rect.x + finished_rect.width / 2, finished_rect.y + finished_rect.height / 2))
    else:
        draw_text_rect(WHITE, finished_rect, FONT4, "    ", pygame.Color('chartreuse2'), COLOR3, (finished_rect.x + finished_rect.width / 2, finished_rect.y + finished_rect.height / 2))


    draw_text_rect(None, None, FONT4, "Finished?", WHITE, COLOR3, (finished_rect.x - 90, finished_rect.y + finished_rect.height / 2))

    layer1 = pygame.Surface((comment_rect.width, comment_rect.height))
    layer1.fill(COLOR3)

    font = FONT2
    if comment_text != "a" and comment_text != "a|":
        try:
            blit_text(screen, comment_text, (comment_rect.x + 8, comment_rect.y + 8), font, WHITE)
        except:
            pass
    
    draw_text_rect(COLOR2, delete_rect, FONT4, "Delete Game", WHITE, RED, (delete_rect.x + 105, delete_rect.y + 20))

    draw_text_rect(None, None, FONT3, "Sort By:", WHITE, COLOR3, (WIDTH // 2 - 200, 40))

    if sorting_by == "alphabetical":
        draw_text_rect(COLOR2, alpha_rect, FONT3, "Alphabetical", WHITE, COLOR3, (WIDTH // 2 - 50, 40))
    else:
        draw_text_rect(WHITE, alpha_rect, FONT3, "Alphabetical", WHITE, COLOR3, (WIDTH // 2 - 50, 40))

    if sorting_by == "rating":
        draw_text_rect(COLOR2, rating_rect, FONT3, "Rating", WHITE, COLOR3, (WIDTH // 2 + 100, 40))
    else:
        draw_text_rect(WHITE, rating_rect, FONT3, "Rating", WHITE, COLOR3, (WIDTH // 2 + 100, 40))

    pygame.draw.rect(screen, WHITE, next_image_rect)
    font = pygame.font.Font('freesansbold.ttf', 24)
    text = font.render("Update Image?", True, WHITE, pygame.Color('darkslategray'))
    textRect = text.get_rect()
    textRect.center = (WIDTH - 180, 30)
    screen.blit(text, textRect)

    pygame.draw.rect(screen, WHITE, next_cover_rect)
    font = pygame.font.Font('freesansbold.ttf', 24)
    text = font.render("Update Cover?", True, WHITE, pygame.Color('darkslategray'))
    textRect = text.get_rect()
    textRect.center = (WIDTH - 180, 65)
    screen.blit(text, textRect)
    
    pygame.display.flip()

pygame.quit()

