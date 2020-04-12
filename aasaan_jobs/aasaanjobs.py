import configparser
import logging
import math
import os
import re

import bs4
import pandas as pd
from bs4 import BeautifulSoup

from definitions import CONFIG_PATH
from lib.scraper_helper import Kirmi

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

cache_path = config.get('aasaan', 'cache_path')
xml_path = config.get('aasaan', 'xml_path')
logname = config.get('aasaan', 'log_path')
error_path =config.get('aasaan', 'error_path')

website_baseurl = 'https://www.aasaanjobs.com'

logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logger = logging.getLogger(__name__)

scraper = Kirmi(caching=True, cache_path=cache_path)


def save_to_csv(job_details_list, filename, page_num):

    """
    :param job_details_list: lst List of Job details dict
    :param filename: str
    :param page_num: int
    :return:
    """

    logger.debug("Saving Job details list for {} - page {}".format(filename, str(page_num)))

    df = pd.DataFrame(job_details_list)

    filename = filename["category"].replace('/', "") + '.csv'

    # if file does not exist write header
    if not os.path.isfile(filename):
        df.to_csv(filename, header='column_names', index=False, sep="|")
    else:  # else it exists so append without writing the header
        df.to_csv(filename, mode='a', header=False, index=False, sep="|")


def get_job_categories(xml_path=None):
    """
    :param xml_path: path to xml with the state and assembly constituency mappings
    :return:
    """
    with open(xml_path) as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    return soup.find_all('job')


def get_number_of_jobs(jobs):
    try:
        number_of_jobs = jobs.find_all("span", string=re.compile("Showing\s+\d+.*jobs"))
        number_of_jobs = re.search('Showing.*of\s+(\d{1,5})\s+jobs', number_of_jobs[0].text).group(1)
        number_of_pages = math.ceil(int(number_of_jobs) / 10)

        return int(number_of_jobs), number_of_pages
    except Exception:
        logger.error("Could not obtain number of pages or jobs")



def get_job_details(job_url):
    try:
        soup = scraper.get_soup(website_baseurl + job_url)

        secs = soup.find('div', attrs={'id': 'job-details'})
        sections = [s for s in secs if s != '\n']
        job_details = dict()

        # Salary
        job_details['salary_min'] = soup.find_all('span', attrs={'itemprop': 'minValue'})[0].text
        job_details['salary_max'] = soup.find_all('span', attrs={'itemprop': 'maxValue'})[0].text

        # Experience
        job_exp = soup.find('img', attrs={'src': re.compile("https.*icon\-briefcase.*")})
        job_details['experience'] = job_exp.parent.parent.parent.find_all('div')[-1].find('p').text
        job_details['experience'] = re.sub(r'((\\n)|(\n))', " ", job_details['experience']).strip()

        # Location
        location = soup.find('img', attrs={'src': re.compile("https.*icon\-pin.*")})
        job_details['location'] = location.parent.parent.parent.find_all('div')[1].find('p').text
        job_details['location'] = re.sub(r'((\\n)|(\n))', " ", job_details['location']).strip()

        # Additional Details
        p_tags_ad = sections[1].div.div.children

        for s in p_tags_ad:
            if not isinstance(s, bs4.element.NavigableString):

                s_children = remove_blanks(s.children)
                c2_children = remove_blanks(s_children[1].children)

                for c2c in c2_children:
                    c3 = remove_blanks(c2c.children)
                    key_values = list(map(lambda x:x.text.strip('\n'), c3))
                    # Remove newline characters
                    job_details[key_values[0]] = re.sub(r'((\\n)|(\n))', " ", key_values[1])



        # Job Requirements
        p_tags_jr = sections[2].div.div.children

        for s in p_tags_jr:
            if not isinstance(s, bs4.element.NavigableString):
                s_children = remove_blanks(s.children)
                c2_children = remove_blanks(s_children[1].children)

                for c2c in c2_children:
                    c3 = remove_blanks(c2c.children)
                    key_values = list(map(lambda x:x.text.strip('\n'), c3))
                    # Remove newline characters
                    job_details[key_values[0]] = re.sub(r'((\\n)|(\n))', " ", key_values[1])


        # Job Description
        p_tags_jd = sections[2].div.div.children

        for s in p_tags_jd:
            if not isinstance(s, bs4.element.NavigableString):
                s_children = remove_blanks(s.children)
                c2_children = remove_blanks(s_children[1].children)

                for c2c in c2_children:
                    c3 = remove_blanks(c2c.children)
                    key_values = list(map(lambda x:x.text.strip('\n'), c3))
                    # Remove newline characters
                    job_details[key_values[0]] = re.sub(r'((\\n)|(\n))', " ", key_values[1])


    except Exception:
        logger.warning("Could not get job details for url {}".format(job_url))
        with open(error_path, 'a') as fd:
            fd.write('\n{} + {}'.format(website_baseurl, job_url))

        return

    return job_details


# Helper function
def convert_list_to_dict(lst): 
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

# Helper function
def find_stripped(soup, what):
  found = soup.find(what)
  if found is not None:
    return found.text.strip()


def remove_blanks(children):
    # will return a list of non-blank elements
    s_children = []
    for child in children:
        if not isinstance(child, bs4.element.NavigableString):
            s_children.append(child)
    return s_children

def process_job_url(jobs, job_category, number_of_pages):
    """
    :param jobs:
    :param job_category:
    :param number_of_pages:
    :return:
    """
    # get job details

    job_urls = jobs.find_all('div', attrs={'data-job-url': re.compile("\/job\/.*")})

    job_details_list = []

    for j in job_urls:
        job_url = j['data-job-url']
        job_details = get_job_details(job_url)
        if job_details:
            job_details_list.append(job_details)

    save_to_csv(job_details_list, job_category, 1)
    job_details_list = []

    if number_of_pages >= 2:
        for i in range(2, number_of_pages + 1):
            logger.debug(website_baseurl + job_category["url"] + "?page={}".format(i))

            jobs = scraper.get_soup(website_baseurl + job_category["url"] + "?page=" + str(i))
            job_urls = jobs.find_all('div', attrs={'data-job-url': re.compile("\/job\/.*")})

            for j in job_urls:
                job_url = j['data-job-url']
                job_details = get_job_details(job_url)
                if job_details:
                    job_details_list.append(job_details)

            save_to_csv(job_details_list, job_category, i)
            job_details_list = []


def run_process():
    job_categories = get_job_categories(xml_path=xml_path)

    for job_category in job_categories:
        jobs = scraper.get_soup(website_baseurl + job_category["url"])
        logger.debug("Getting job list for {}".format(job_category["category"]))

        # Identify the number of jobs and pages
        number_of_jobs, number_of_pages = get_number_of_jobs(jobs)

        process_job_url(jobs, job_category, number_of_pages)


if __name__ == "__main__":
    run_process()
