import configparser
import json
import logging
import os
import re

from definitions import CONFIG_PATH
from lib.scraper_helper import Kirmi

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

cache_path = config.get('ncs', 'cache_path')
logname = config.get('ncs', 'log_path')
error_path = config.get('ncs', 'error_path')

logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logger = logging.getLogger(__name__)

scraper = Kirmi(caching=True, cache_path=cache_path, timeout=3)

website_baseurl="https://www.ncs.gov.in"


def clean_text(text):
    text = re.sub('(\r|\n|\t)', ' ', text)
    text = re.sub('\s+', ' ', text)
    text = text.strip()
    return text


def get_state_urls():
    """
    :return: dict : URL for job listings by state
    """

    if os.path.exists('state_links.json'):
        with open('state_links.json','r') as f:
            state_urls = json.load(f)

            return state_urls

    soup = scraper.get_soup(website_baseurl)
    urls = dict()
    states = soup.findAll('span', attrs={'stateName'})

    for state in states:
        urls[state.get_text()] = state.find_parent('a')['href']

    with open('state_links.json','w') as f:
        f.write(json.dumps(urls, indent = 4, sort_keys = True))

    return urls

def get_job_urls(soup):

    all_job_urls = soup.findAll('a', attrs={'onclick': re.compile('ViewJobPopup\(.*\)')})

    all_job_urls_list = []

    for element in all_job_urls:

        job_url = element['onclick']

        all_job_urls_list.append(re.search('.*(https\:.+)\'', job_url).group(1))

    return list(set(all_job_urls_list))


def get_landing_page_job_details(soup):
    """
    :param soup:
    :return: list of dictionaries

   {
	'Company:':
	'Job Location:':
	'Salary:':
	'Skill Required:':
	'Job Description:':
	}

    """

    job_details_list = []


    for tab_soup in soup.findAll('div', attrs={'class' : re.compile('row padding0-15'), 'id': 'mytab'}):

        job_details = dict()


        try:

            # Job URL
            job_url = tab_soup.find('a', attrs={'onclick': re.compile('ViewJobPopup\(.*\)')})
            job_url = job_url['onclick']
            job_details['job_url'] = re.search('.*(https\:.+)\'', job_url).group(1)

            job_details['posted_on'] = tab_soup.find_all('span', attrs={'class': 'text-muted pull-right'})[0].find_next().get_text()


            # Job Details from landing page
            text_info = tab_soup.find_all('span', attrs={'class': 'text-info'})

        except Exception:
            print("ERROR")


        for txt in text_info:
            job_details[clean_text(txt.get_text())] = clean_text(txt.find_next().get_text())

        job_details_list.append(job_details)


    return job_details_list


def run_process():
    state_urls = get_state_urls()

    for state, state_url in state_urls.items():


        print("starting scraping for state {}".format(state))

        # State landing Page
        soup = scraper.get_soup(state_url)

        #TODO ADD Pagenation

        job_details_list = get_landing_page_job_details(soup)

        for job_dict in job_details_list:

            job_url = job_dict['job_url']

            soup = scraper.get_soup(job_url)

            x = soup.findAll('label', attrs={'class': re.compile('control-label\scol-sm-\d{1,2}$')})

            job_details = dict()

            for y in x:

                text_label = clean_text(y.get_text())
                text_value = clean_text(y.find_next('label', attrs={'class': re.compile('control-label')}).get_text())

                if text_label == text_value or text_label.strip() == "Job Location":
                    continue

                if text_label.replace("\s+", "").strip() != '' or text_value.replace("\s+", "").strip() != "":
                    job_details[text_label] = text_value


            # print(job_details)
            # print(job_dict)
            # print("\n\n\n")

        print("completed scraping state {} \n\n".format(state))



if __name__ == "__main__":
    run_process()


