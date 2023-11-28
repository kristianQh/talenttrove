import requests
import time
import csv
from bs4 import BeautifulSoup
from bs4.element import Comment
from selenium import webdriver
from langdetect import detect
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

# TODO Remove all jobs with company name "Jobindex Kurser"
options = Options()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

def retrieve_jobs(job_keywords, job_tag, job_class, base_url):
    job_listings = []
    for job_keyword in job_keywords:
        page = 1

        while True:
            search_url = base_url.format(page=page, job=job_keyword)
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, "html.parser")
            fetched_jobs = soup.find_all(job_tag, job_class)
            if not fetched_jobs:
                break

            job_listings += fetched_jobs
            page += 1
    return job_listings

jobs = []
def scrape_jobindex(job_keywords):
    base_url = "https://www.jobindex.dk/jobsoegning?page={page}&q={job}%27&subid=1&subid=3&subid=4&subid=6&subid=93"
    job_listings = retrieve_jobs(job_keywords, "div", {"class": ["PaidJob", "jix_robotjob"]}, base_url)
    
    for job_ad in tqdm(job_listings):
        url = job_ad.find("a", text='Se jobbet')["href"]
        if url in jobs:
            continue
        title = find_element(job_ad, "h4", {"class": ""})
        company = find_element(job_ad, "div", {"class": "jix-toolbar-top__company"})
        location = find_element(job_ad, "span", {"class": "jix_robotjob--area"})
        description = find_description(url, None)
        if description == "Unknown":
            continue
        lang = detect(description)
        if lang == "da":
            continue
        jobs.append([title, company, location, url, description, lang])
    return jobs

def scrape_hub(job_keywords):
    base_url = "https://thehub.io/jobs?search={job}&location=Denmark&countryCode=DK&sorting=mostPopular&page={page}"
    job_listings = retrieve_jobs(job_keywords, "div", {"class": "my-10"}, base_url)
    
    for job_ad in tqdm(job_listings):
        url = "https://thehub.io" + job_ad.find("a", class_="card-job-find-list__link")["href"]
        if url in jobs:
            continue
        title = find_element(job_ad, "span", {"class": "card-job-find-list__position"})
        bullets = job_ad.find("div", {"class": "bullet-inline-list"})
        company, location = [span.text for span in bullets.find_all("span")][:2]
        description = find_description(url, {"tag": "div", "class": {"class": "text-block"}})
        if description == "Unknown":
            continue
        lang = detect(description)
        if lang == "da":
            continue
        jobs.append([title, company, location, url, description, lang])
    return jobs

def find_element(soup, tag, class_):
    element = soup.find(tag, class_)
    return element.text.strip() if element else "Unknown"

def find_description(url, desc_config):
    driver.set_page_load_timeout(3)
    try:
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        # print(soup)
        if desc_config:
            return find_element(soup, desc_config['tag'], desc_config['class'])
        else:
            texts = soup.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            return  " ".join(t.strip() for t in visible_texts)
    except TimeoutException:
        print("TimeoutException")
        return "Unknown"


scraped_jobs = scrape_jobindex(["\"Data+Science\"", "\"Machine+Learning\"", "\"Computer+Science\"", "\"Software+Developer\""])
scraped_jobs = scrape_hub(["\"Data Science\"", "\"Machine Learning\""])
print(len(scraped_jobs))
driver.quit()

csv_file = "job_info.csv"
with open(csv_file, mode="w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Company', 'Location', 'URL', 'Description', 'Language'])
    writer.writerows(scraped_jobs)
