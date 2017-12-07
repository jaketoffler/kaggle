# Author: Jake Toffler
# GitHub: https://github.com/jaketoffler
# Date: 11/21/2017
"""
Kaggle Scoreboard

The purpose of this program is to calculate the number of Kaggle points for given users at any moment.  Specifically,
this author is using this program to calculate a scoreboard for the USF MSAN Machine Learning I class.

As of 12/5/2017, this program does not penalize for being on a team and it incorrectly counts points for kernels that
were written before the recognized start date.  This may also fail to count points if a user has entered more
competitions than can be displayed on a single page, but in testing I did not see this issue.
"""

import pandas as pd
import re
import math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a Chrome webdriver with Selenium
driver = webdriver.Chrome('/usr/local/bin/chromedriver')

# Initialize a list that will store (username, points) tuples
allStudents = []

# Load a CSV with student names and their respective Kaggle usernames
students = pd.read_csv("/Users/jtoffler/Desktop/MSAN_Kaggle_Usernames.csv")
usernames = students['Username']

# Create a list of competitions that are valid for scoring
validCompetitions = [u'Corporaci\xf3n Favorita Grocery Sales Forecasting',
                     u'Cdiscount\u2019s Image Classification Challenge',
                     u'Porto Seguro\u2019s Safe Driver Prediction',
                     u'Statoil/C-CORE Iceberg Classifier Challenge',
                     u'Text Normalization Challenge - Russian Language',
                     u'Text Normalization Challenge - English Language',
                     u'WSDM - KKBox\u2019s Churn Prediction Challenge',
                     u'WSDM - KKBox\u2019s Music Recommendation Challenge']


def kaggleScoreboard(usernames):
    """
    This function calculates the number of points for each username in the list of usernames.  It uses Selenium to open
    each user's profile page, finds the total number of kernel votes (given that the kernel was posted in the appropriate
    timeframe) and multiplies by 80, in accordance with our particular scoring metric.  It then moves to the competitions
    tab and calculates the number of Kaggle points (based on the formula found here: https://www.kaggle.com/progression as
    of 11/30/2017) for valid competitions.  It then outputs a list of (username, points) tuples.
    """
    for username in usernames:
        # Initialize the score for each user
        totalPoints = 0

        # Open a user's kernels page
        driver.get("https://www.kaggle.com/" + username + "/kernels")

        # When the vote count appears, grab the number of votes.  If a user has no kernels, pass.
        try:
            try:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@class='vote-button__vote-count']")))
            except:
                kernelVotes = driver.find_elements_by_xpath("//*[@class='vote-button__vote-count']")
            finally:
                kernelVotes = driver.find_elements_by_xpath("//*[@class='vote-button__vote-count']")

            for vote in kernelVotes:
                totalPoints += 80*int(vote.text)
        except:
            totalPoints = totalPoints

        # Open a user's "Completed" competitions page
        try:
            driver.find_element_by_xpath("//*[@id='pageheader-nav-item--competitions']").click()

            # When the rank appears, grab the rank, the total number of teams, and the competition name
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")))
            except:
                standings = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")
                totalTeams = driver.find_elements_by_xpath("//*[@class='profile-competitions__list-item-medal-teams']")
                competitions = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-name']")
            finally:
                standings = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")
                totalTeams = driver.find_elements_by_xpath("//*[@class='profile-competitions__list-item-medal-teams']")
                competitions = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-name']")

            # Strip all unnecessary characters from the ranks and teams and add the points in accordance with the
            # scoring formula, if the competition name is in the list of valid competitions
            comps = []
            for i in range(0, len(standings)):
                place = int(re.sub('[^0-9]+', '', standings[i].text))
                teams = int(re.sub('[^0-9]+', '', totalTeams[i].text))
                competition = competitions[i].text
                standing = (place, teams, competition)
                comps.append(standing)
            for comp in comps:
                if comp[2] in validCompetitions:
                    totalPoints += 100000 * (comp[0] ** -0.75) * math.log(1 + math.log(comp[1], 10), 10)
        except:
            totalPoints = totalPoints

        # Repeat the step from above, but for "Active" competitions
        try:
            driver.find_element_by_link_text("Active").click()

            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")))
            except:
                standings = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")
                totalTeams = driver.find_elements_by_xpath("//*[@class='profile-competitions__list-item-medal-teams']")
                competitions = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-name']")
            finally:
                standings = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")
                totalTeams = driver.find_elements_by_xpath("//*[@class='profile-competitions__list-item-medal-teams']")
                competitions = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-name']")

            comps = []
            for i in range(0,len(standings)):
                place = int(re.sub('[^0-9]+', '', standings[i].text))
                teams = int(re.sub('[^0-9]+', '', totalTeams[i].text))
                competition = competitions[i].text
                standing = (place, teams, competition)
                comps.append(standing)
            for comp in comps:
                if comp[2] in validCompetitions:
                    totalPoints += 100000*(comp[0]**-0.75)*math.log(1+math.log(comp[1], 10), 10)
        except:
            totalPoints = totalPoints

        # Repeat the step from above, but for "Active" competitions
        try:
            driver.find_element_by_link_text("Tutorial").click()

            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")))
            except:
                standings = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")
                totalTeams = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-medal-teams']")
                competitions = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-name']")
            finally:
                standings = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-medal-rank']/span/span[1]")
                totalTeams = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-medal-teams']")
                competitions = driver.find_elements_by_xpath(
                    "//*[@class='profile-competitions__list-item-name']")

            comps = []
            for i in range(0, len(standings)):
                place = int(re.sub('[^0-9]+', '', standings[i].text))
                teams = int(re.sub('[^0-9]+', '', totalTeams[i].text))
                competition = competitions[i].text
                standing = (place, teams, competition)
                comps.append(standing)
            for comp in comps:
                if comp[2] in validCompetitions:
                    totalPoints += 100000 * (comp[0] ** -0.75) * math.log(1 + math.log(comp[1], 10), 10)
        except:
            totalPoints = totalPoints

        # Store the username and the score for each user and append it to the master list
        userScore = (username, totalPoints)
        allStudents.append(userScore)
    return allStudents

# Put the results into a dataframe and merge it back with the students dataframe
scoreboard = pd.DataFrame(kaggleScoreboard(usernames), columns = ['Username', 'Points'])
standings = pd.merge(students, scoreboard, on='Username')

# Spit out CSV
standings.to_csv("/Users/jtoffler/Desktop/standings.csv", index = False)

driver.quit()