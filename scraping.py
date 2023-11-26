import requests
import time
import csv
from bs4 import BeautifulSoup
from bs4.element import Comment
from selenium import webdriver
from langdetect import detect
from selenium.common.exceptions import TimeoutException


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

# TODO Remove all jobs with company name "Jobindex Kurser"

jobs = []

def retrieve_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def scrape_jobs(job_keywords, config, base_url):
    jobs = []
    job_listings = []
    for job_keyword in job_keywords:
        page = 1

        while True:
            search_url = base_url.format(page=page, job=job_keyword)
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, "html.parser")
            fetched_jobs = soup.find_all(config['job_container']['tag'], config['job_container']['class'])
            if not fetched_jobs:
                break

            job_listings += fetched_jobs
            page += 1
    
    for job_ad in job_listings:
        title = find_element(job_ad, config['title'])
        print(title)
        url = find_element_attribute(job_ad, config['url'], 'href')
        company = find_element(job_ad, config['company'])
        location = find_element(job_ad, config['location'])
        description = find_description(url, config['description'])
        lang = detect(description)
        if title and company not in jobs:
            jobs.append({"title": title, "company": company,
                         "location": location, "link": url, 
                         "description": description, "language": lang})

    return jobs

def find_element(soup, element_config):
    element = soup.find(element_config['tag'], element_config['class'])
    return element.text.strip() if element else "Unknown"

def find_element_attribute(soup, element_config, attribute):
    element = soup.find(element_config['tag'], element_config['class'])
    return element[attribute] if element and attribute in element.attrs else "Unknown"

def find_description(url, element_config):
    driver = webdriver.Firefox()
    driver.set_page_load_timeout(3)
    try:
        driver.get(url)
        time.sleep(0.2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if element_config == None:
            texts = soup.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            return  " ".join(t.strip() for t in visible_texts)
        else:
            return find_element(soup, element_config)
    except TimeoutException:
        print("TimeoutException")
        return "Unknown"
    finally:
        driver.quit()

config = {
    'job_container': {'tag': 'div', 'class': {'class': ["PaidJob", "jix_robotjob"]}},
    'title': {'tag': 'h4', 'class': {'class': ""}},
    'url': {'tag': 'a', 'class': {'class': ""}},
    'company': {'tag': 'div', 'class': {'class': 'jix-toolbar-top__company'}},
    'location': {'tag': 'span', 'class': {'class': 'jix_robotjob--area'}},
    'description': None
}

base_url = "https://www.jobindex.dk/jobsoegning?page={page}&q={job}%27&subid=1&subid=3&subid=4&subid=6&subid=93"
jobs = scrape_jobs(["\"Data+Science\"", "Softwareudvikler", "\"Machine+Learning\"", "Datalog"], config, base_url)
print(len(jobs))


# def scrape_jobs_hub(job):
#     search_url = f"https://thehub.io/jobs?search={job}&location=Denmark&countryCode=DK&sorting=mostPopular&page={page}"
#     soup = retrieve_html(search_url)
#     fetched_jobs = soup.find_all("div", {"class": "my-10"})
#     job_listings = []
#     for job_ad in fetched_jobs:
#         title = job_ad.find("span", {"class": "card-job-find-list__position"}).text.strip()
#         bullets = job_ad.find("div", {"class": "bullet-inline-list"})
#         company, location = [span.text for span in bullets.find_all("span")][:2]
#         url = "https://thehub.io" + soup.find("a", class_="card-job-find-list__link")["href"]
#         print(title, company, location)

#         driver.set_page_load_timeout(5)
#         try:
#             driver.get(url)
#             html = driver.page_source
#             soup = BeautifulSoup(html, "html.parser")
#             description = soup.find("div", {"class": "text-block"}).text.strip()
#             lang = detect(description)
#             print(lang)
#         except TimeoutException:
#             print("TimeoutException")
#             description = "Unknown"

#             jobs.append({"title": title, "company": company, "location": location, "link": url, "description": description, "language": lang})

# scrape_jobs_hub("Developer")

# def scrape_jobs(job):
#     for j in job:
#         page = 1
#         search_url = f"https://www.jobindex.dk/jobsoegning?page={page}&q={j}%27&subid=1&subid=3&subid=4&subid=6&subid=93"
#         response = requests.get(search_url)
#         soup = BeautifulSoup(response.text, "html.parser")

#         fetched_jobs = soup.find_all("div", {"class": ["PaidJob", "jix_robotjob"]})
#         job_listings = []
#         while fetched_jobs:
#             search_url = f"https://www.jobindex.dk/jobsoegning?page={page}&q={j}%27&subid=1&subid=3&subid=4&subid=6&subid=93"
#             response = requests.get(search_url)
#             soup = BeautifulSoup(response.text, "html.parser")
#             fetched_jobs = soup.find_all("div", {"class": ["PaidJob", "jix_robotjob"]})
#             job_listings += fetched_jobs
#             page += 1

#         print(len(job_listings))
#         # # TODO: Needs error handling
#         for job_ad in job_listings:
#             job = job_ad.find("h4")
#             title = job.text.strip()
#             url = job.find("a")["href"]

#             try:
#                 company = job_ad.find("div", {"class": "jix-toolbar-top__company"}).text.strip()
#             except:
#                 location = "Unknown"
#             print(company)
#             try:
#                 location = job_ad.find("span",  {"class": "jix_robotjob--area"}).text.strip()
#             except:
#                 location = "Unknown"

#             if title and company in jobs:
#                 continue

#             driver.set_page_load_timeout(5)
#             try:
#                 driver.get(url)
#                 time.sleep(1)
#                 html = driver.page_source
#                 soup = BeautifulSoup(html, "html.parser")
#                 texts = soup.findAll(text=True)
#                 visible_texts = filter(tag_visible, texts)
#                 description = " ".join(t.strip() for t in visible_texts)
#                 lang = detect(description)
#                 print(lang)
#             except TimeoutException:
#                 print("TimeoutException")
#                 description = "Unknown"
#             print("=====================================")

#             jobs.append({"title": title, "company": company, "location": location, "link": url, "description": description, "language": lang})
#     return jobs

# jobs = scrape_jobs(["\"Data+Science\"", "Softwareudvikler", "\"Machine+Learning\"", "Datalog"])
# print(len(jobs)) 

# csv_file = "job_info.csv"
# with open(csv_file, mode="w", newline='', encoding='utf-8') as file:
#     writer = csv.DictWriter(file, fieldnames=["title", "company", "location", "link", "description", "language"])
#     writer.writeheader()
#     for job in jobs:
#         writer.writerow(job)
