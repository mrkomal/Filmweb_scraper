# -*- coding: utf-8 -*-
"""
Sracping on filmweb webiste with the selenimum. Saving info in Excel sheet 
with use of pandas.
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

###### Filmweb Scraping

RESULTS_PATH = 'C:/Users/admin/Desktop/filmweb_project'

DRIVER_PATH = 'C:\Program Files\chromedriver.exe'
driver = webdriver.Chrome(DRIVER_PATH)
number_of_movies = 1  # number of movies from the top

# attributes to find
movies_titles = []
actors = {}
directors = {}
screenwriters = {}
music = {}

driver.get('https://www.filmweb.pl/ranking/film')
time.sleep(3)  # wait until the page is loaded
driver.find_element_by_id('didomi-notice-agree-button').click()  # click agree button

try:
    # ranking website
    ranking = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ranking__list"))
    )
    movies_info = ranking.find_elements_by_tag_name("span")
    for _ in movies_info:
        if _.text != "" and _.get_attribute("itemprop") == "name":
            movies_titles.append(_.text)
        if len(movies_titles) == number_of_movies:
            break

    for title in movies_titles[:number_of_movies]:
        movie_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, title))
        )
        movie_button.click()  # see movie's website

        # movie website
        cast_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Zobacz pełną obsadę i twórców"))
        )
        cast_button.click()  # click the button that shows the cast

        # cast website
        cast_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filmFullCastSection__list"))
        )
        cast_info = cast_section.find_elements_by_class_name("castRoleListElement__info")
        for _ in cast_info:
            actor_name = _.find_element_by_tag_name("a").text
            if actor_name in actors.keys():
                actors[actor_name] += 1
            else:
                actors[actor_name] = 1

        driver.find_element_by_link_text("Twórcy").click()  # click button that show other info
        #  website with other information
        other_info_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filmFullCastSection__wrapper"))
        )
        other_info = other_info_section.text.split("\n")
        people = {'reżyser': directors,
                  'scenariusz': screenwriters,
                  'muzyka': music}  # people to find

        for job in people.keys():
            if job in other_info:
                dictionary = people[job]
                index = other_info.index(job)
                while other_info[index + 1][0].isupper():  # adding elements that starts with capital letter
                    if other_info[index + 1] in dictionary.keys():
                        dictionary[other_info[index + 1]] += 1
                    else:
                        dictionary[other_info[index + 1]] = 1
                    index += 1

        # going back to ranking
        for i in range(0, 3, 1):
            driver.back()
finally:
    driver.quit()

# report
print('Summary:')
print('Number of movies: ' + str(len(movies_titles)))
print('Movies: ' + str(movies_titles))
print('Number of actors: ' + str(len(actors.keys())))
print('Number of directors: ' + str(len(directors.keys())))
print('Number of screenwriters: ' + str(len(screenwriters.keys())))
print('Number of musicians ' + str(len(music.keys())))

###### Saving results to CSV files

data_dictionaries = [actors, directors, screenwriters, music]
file_names = 'actors, directors, screenwriters, music'
file_names = file_names.split(',')
file_names = [name.strip() for name in file_names]

headers = ['name', 'number of films']

i = 0
for job in data_dictionaries:
    df = pd.DataFrame.from_dict({'a':job}, orient='index')
    file_path = "{}/{}.csv".format(RESULTS_PATH, file_names[i])
    df.to_csv(file_path)
    i += 1
    
print('Saved.')