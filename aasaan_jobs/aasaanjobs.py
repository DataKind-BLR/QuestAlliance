import logging
import os
import re
import math
from time import strptime
from bs4 import BeautifulSoup
from kirmi import Kirmi

website_baseurl = 'https://www.aasaanjobs.com'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

scraper = Kirmi(caching=True, cache_path="./aasan_cache.sqlite3")


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

    # Location
    location = soup.find('img', attrs={'src': re.compile("https.*icon\-pin.*")})
    job_details['location'] = location.parent.parent.parent.find_all('div')[1].find('p').text

    # Additional Details
    # p_tags_ad = sections[1].div.div.div.find_all('p')
    p_tags_ad = [s for s in sections[1].div.div.children if s != '\n']
    # p_values_ad = [p.text for p in p_tags_ad]

    # Level 1 - .row
    for child1 in p_tags_ad:
        child1_children = [s for s in child1.children if s != '\n']

        # Level 2 - .p-bottom-sm
        for child2 in child1_children:
            child2_children = [s for s in child2.children if s != '\n']
            
            # Level 3 - .row
            for child3 in child2_children:

                # print(child3)
                # print(type(child3))
                # print(child3.strip(''))
                # child3 = find_stripped(child3, ' ')
                # print(child3)
                # print('*******************')

                if child3 != '\n' or child3.find(' ') != None:
                    labels = child3.find_all('p', attrs={'class': re.compile(".*lighter")})
                    values = child3.find_all('p', attrs={'class': re.compile(".*text-gray$")})

                    try:
                        if len(values) > 1:
                            # merge them
                            x = [v.text for v in values]
                            vvvvvv = ','.join(x)

                            job_details[labels[0].text] = vvvvvv
                        else:
                            job_details[labels[0].text] = values[0].text

                    except:
                        print('')

                    print('-----------------------')
                    print(labels)
                    print('-----------------------')
                    print(values)
                    print('-----------------------')

    import pdb
    pdb.set_trace()

    if len(p_values_ad) % 2 != 0:
        ad = convert_list_to_dict(p_values_ad[:-1])
    else:
        ad = convert_list_to_dict(p_values_ad)
    
    job_details.update(ad)


    # Job Requirements
    p_tags_jr = sections[2].div.div.div.find_all('p')
    p_values_jr = [p.text for p in p_tags_jr]

    if len(p_values_jr) % 2 != 0:
        jr = convert_list_to_dict(p_values_jr[:-1])
    else:
        jr = convert_list_to_dict(p_values_jr)

    job_details.update(jr)


    # Job Description
    p_tags_jd = sections[3].div.div.div.find_all('p')
    p_values_jd = [p.text for p in p_tags_jd]

    job_details['job_description'] = ''.join(p_values_jd)

    print(job_details)
    print('\n----------------------------------\n')


# Helper function
def convert_list_to_dict(lst): 
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

# Helper function
def find_stripped(soup, what):
  found = soup.find(what)
  if found is not None:
    return found.text.strip()


def process_job_url(jobs, job_category, number_of_pages):
    # get job details

    job_urls = jobs.find_all('div', attrs={'data-job-url': re.compile("\/job\/.*")})

    for j in job_urls:
        job_url = j['data-job-url']
        get_job_details(job_url)

        if number_of_pages >= 2:
            for i in range(2, number_of_pages + 1):
                print(website_baseurl + job_category["url"] + "?page={}".format(i))

                jobs = scraper.get_soup(website_baseurl + job_category["url"] + "?page=" + str(i))
                job_urls = jobs.find_all('div', attrs={'data-job-url': re.compile("\/job\/.*")})

                for j in job_urls:
                    job_url = j['data-job-url']
                    get_job_details(job_url)


def run_process():
    job_categories = get_job_categories(
        xml_path='job_categories.xml')

    for job_category in job_categories:
        jobs = scraper.get_soup(website_baseurl + job_category["url"])
        # logger.debug("Getting job list for {}".format(job_category["category"]))

        # Identify the number of jobs and pages
        number_of_jobs, number_of_pages = get_number_of_jobs(jobs)

        process_job_url(jobs, job_category, number_of_pages)


if __name__ == "__main__":
    run_process()
