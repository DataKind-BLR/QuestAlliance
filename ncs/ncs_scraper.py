import configparser
import logging
import math
import os
import re

import urllib.request
import bs4
import pandas as pd
from bs4 import BeautifulSoup


from definitions import CONFIG_PATH
from lib.scraper_helper import Kirmi

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

cache_path = config.get('ncs', 'cache_path')
xml_path = config.get('ncs', 'xml_path')
logname = config.get('ncs', 'log_path')
error_path =config.get('ncs', 'error_path')

#Karnataka
website_baseurl='https://www.ncs.gov.in/Pages/ViewJobDetails.aspx?A=w1BcJXzB%2BW4%3D&U=&JSID=7uYU41Gnn8I%3D&RowId=7uYU41Gnn8I%3D&OJ='

logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logger = logging.getLogger(__name__)

scraper = Kirmi(caching=True, cache_path=cache_path)

# Empty dict to hold the scraped details
job_details = {}

user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent}
def create_soup(url, header):
    request=urllib.request.Request(url,None,header)
    response=urllib.request.urlopen(request)
    data=response.read()
    soup=BeautifulSoup(data,"html.parser")
    return soup

#Part 1: Basic information
def scrape_basic_info(basic_details):
    print(basic_details)
    for span in basic_details:
        print('Span is {}'.format(span))
        label=span['strong'].strip().replace(' ','_').lower()
        job_details[label]=span['strong'].text()

#Part 2: 
def scrape_job_details(job_details):
    details_rows=job_details.find_all('div', class_='row')
    for row in details_rows:
        title=row.find_all('label')[0].text().strip().replace(' ','_').lower()
        value=row.find_all('label')[1].text()
        job_details[title]=value

#Part 3:
def scrape_qualifications(quals):
    qual_rows=quals.find_all('div',class_='row')
    for row in qual_rows:
        title=row.find_all('div', class_='row')
        value=row.find_all('label')[1].text()
        job_details[title] = value


if __name__ == "__main__":
   
   soup=create_soup(website_baseurl,headers)   
   panel_body = soup.find('div', class_='panel-body')
  
   basic_info = panel_body.find('div', attr={'class':"col-xs-9 col-md-10 paddingBottom5-Mobile"}) 
   print('Basic info is {}'.format(type(basic_info)))
   scrape_basic_info(basic_info)
  
   details=panel_body.find_all('div', class_="lightGrayBG paddingTop10")
   scrape_basic_info(details)

   qualifications=panel_body.find_all('div')[3]
   scrape_qualifications(qualifications)
   
   print(job_details)
 
  
