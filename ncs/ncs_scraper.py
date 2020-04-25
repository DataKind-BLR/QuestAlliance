import configparser
import json
import logging
import os
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver

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

website_baseurl = "https://www.ncs.gov.in"


def clean_text(text):
    """
    :param text: str
    :return: str
    """
    text = re.sub('(\r|\n|\t)', ' ', text)
    text = re.sub('\s+', ' ', text)
    text = text.strip()
    return text


def get_state_urls():
    """
    :return: dict : URL for job listings by state
    """

    if os.path.exists('state_links.json'):
        with open('state_links.json', 'r') as f:
            state_urls = json.load(f)

            return state_urls

    soup = scraper.get_soup(website_baseurl)
    urls = dict()
    states = soup.findAll('span', attrs={'stateName'})

    for state in states:
        urls[state.get_text()] = state.find_parent('a')['href']

    with open('state_links.json', 'w') as f:
        f.write(json.dumps(urls, indent=4, sort_keys=True))

    return urls


def get_job_urls(soup):
    """
    :param soup:
    :return:
    """

    all_job_urls = soup.findAll(
        'a', attrs={'onclick': re.compile('ViewJobPopup\(.*\)')})

    all_job_urls_list = []

    for element in all_job_urls:

        job_url = element['onclick']

        all_job_urls_list.append(
            re.search('.*(https\:.+)\'', job_url).group(1))

    return list(set(all_job_urls_list))


def get_landing_page_job_details(soup):
    """
    :param soup:
    :return: list of dictionaries

    {
        'Company:': '',
        'Job Location:': '',
        'Salary:': '',
        'Skill Required:': '',
        'Job Description:': '',
    }

    """

    job_details_list = []

    for tab_soup in soup.findAll('div', attrs={'class': re.compile('row padding0-15'), 'id': 'mytab'}):

        job_details = dict()

        try:

            # Job URL
            job_url = tab_soup.find(
                'a', attrs={'onclick': re.compile('ViewJobPopup\(.*\)')})
            job_url = job_url['onclick']
            job_details['job_url'] = re.search(
                '.*(https\:.+)\'', job_url).group(1)

            job_details['posted_on'] = tab_soup.find_all(
                'span', attrs={'class': 'text-muted pull-right'})[0].find_next().get_text()

            # Job Details from landing page
            text_info = tab_soup.find_all('span', attrs={'class': 'text-info'})

            for txt in text_info:
                job_details[clean_text(txt.get_text())] = clean_text(
                    txt.find_next().get_text())

        except Exception:
            logger.exception("Error getting page")

        job_details_list.append(job_details)

    return job_details_list


def get_number_of_pages(driver):
    """
    :param driver:
    :return:
    """
    # FINDING: total number of pages
    # the total pages in written in the form of text below the page buttons list

    try:
        getelementbyxpath = driver.find_element_by_xpath(
            '/html/body/form/div[4]/div/div[4]/div[1]/div/span/div[1]/div/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div/div[1]/div/div[2]/nav[1]/div[2]')
        s = getelementbyxpath.find_elements_by_xpath(".//*")[0].text
        number_of_pages = [int(i) for i in s.split() if i.isdigit()][0]

        return number_of_pages

    except Exception as err:
        logger.exception("Error getting number of pages : \n {}".format(err))


def get_job_details_list_by_page(driver):
    """
    :param driver:
    :return:
    """

    # Relative Xpath of the page grid
    getelementbyxpath = driver.find_element_by_xpath(
        '//*[@id="ctl00_SPWebPartManager1_g_5f765d3f_f705_4af4_83e7_cd16b175ab26_ctl00_MainDivSearchResult"]/div[2]/nav[1]/div[1]')
    # putting all elements of the page grid into a list
    l = getelementbyxpath.find_elements_by_xpath(".//*")

    # the last page button
    # logger.info("pages length", len(l), l[-1].text)
    driver.execute_script("arguments[0].click();", l[-1])

    # New pagesource and job listings
    soup = BeautifulSoup(driver.page_source, 'lxml')
    job_details_list = get_landing_page_job_details(soup)

    return job_details_list


def get_job_details(job_dict):
    """
    :param job_dict:
    :return:
    """

    job_url = job_dict['job_url']

    soup = scraper.get_soup(job_url)

    x = soup.findAll('label', attrs={'class': re.compile(
        'control-label\scol-sm-\d{1,2}$')})

    job_details = dict()

    for y in x:

        text_label = clean_text(y.get_text())
        text_value = clean_text(y.find_next(
            'label', attrs={'class': re.compile('control-label')}).get_text())

        if text_label == text_value or text_label.strip() == "Job Location":
            continue

        if text_label.replace("\s+", "").strip() != '' or text_value.replace("\s+", "").strip() != "":
            job_details[text_label] = text_value

    return job_details


def run_process():
    state_urls = get_state_urls()

    for state, state_url in state_urls.items():

        logger.info("starting scraping for state {}".format(state))

        # State landing Page
        driver = webdriver.Chrome()
        driver.get(state_url)

        number_of_pages = get_number_of_pages(driver)

        # Pagination
        for page in range(1, number_of_pages):
            logger.info("Fetching page {}".format(page))

            job_details_list = get_job_details_list_by_page(driver)

            for job_dict in job_details_list:
                job_details = get_job_details(job_dict)
                outdict = {**job_details, **job_dict}

                print(outdict)

            time.sleep(3)
        logger.info("completed scraping state {} \n\n".format(state))

        time.sleep(5)


if __name__ == "__main__":
    run_process()
