# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 22:42:51 2020

@author: shass
"""

#TODO: Make the code more modular
#TODO: Add logger

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time

website_url = "https://www.kaam24.com/Jobs/jobs-in-India"

def scroll_down(D):
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = D.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down to the bottom.
        D.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = D.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            break

        last_height = new_height

driver = webdriver.Chrome()
driver.get(website_url)
time.sleep(5)
scroll_down(driver)


job_heading = []
position = []
data = []
content = driver.page_source
soup = BeautifulSoup(content)

for a in soup.findAll('div',href=False, attrs={'class':'center-outer card'}):
    job_title = a.find('div', attrs={'class':'nameheading'})
    position_ = a.find('div', attrs={'class':'namecat'})
    L = a.find('div', attrs={'class':'secondouter'})
    job_heading.append(job_title.text)
    position.append(position_.text)
    data.append(L.text.split("\n"))


for a in soup.findAll('div',href=False, attrs={'class':'center-outer card ng-scope'}):
    job_title =a.find('div', attrs={'class':'nameheading'})
    position_ =a.find('div', attrs={'class':'namecat'})
    L = a.find('div', attrs={'class':'secondouter'})
    job_heading.append(JT.text)
    position.append(position_.text)
    data.append(L.text.split("\n"))


df=pd.DataFrame({'job':job_heading,'position':position,'data':data})

# Below line has been updated to have a unique CSV delimiter `|||`
df.to_csv('kaam_24.csv', sep='|||', index=False)
