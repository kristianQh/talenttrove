import requests
import time
import csv
from bs4 import BeautifulSoup
from bs4.element import Comment
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from langdetect import detect
from selenium.common.exceptions import TimeoutException

options = Options()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

jobs = []

def scrape_jobs_hub(job):
    search_url = f"https://thehub.io/jobs?search={job}&location=Denmark&countryCode=DK&sorting=mostPopular&page={page}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    fetched_jobs = soup.find_all("div", {"class": "my-10"})
    job_listings = []
    for job_ad in fetched_jobs:
        title = job_ad.find("span", {"class": "card-job-find-list__position"}).text.strip()
        bullets = job_ad.find("div", {"class": "bullet-inline-list"})
        company, location = [span.text for span in bullets.find_all("span")][:2]
        url = "https://thehub.io" + soup.find("a", class_="card-job-find-list__link")["href"]
        print(title, company, location)

        driver.set_page_load_timeout(5)
        try:
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            description = soup.find("div", {"class": "text-block"}).text.strip()
            lang = detect(description)
            print(lang)
        except TimeoutException:
            print("TimeoutException")
            description = "Unknown"

            jobs.append({"title": title, "company": company, "location": location, "link": url, "description": description, "language": lang})

scrape_jobs_hub("Developer")

def scrape_jobs(job):
    for j in job:
        page = 1
        search_url = f"https://www.jobindex.dk/jobsoegning?page={page}&q={j}%27&subid=1&subid=3&subid=4&subid=6&subid=93"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        fetched_jobs = soup.find_all("div", {"class": ["PaidJob", "jix_robotjob"]})
        job_listings = []
        while fetched_jobs:
            search_url = f"https://www.jobindex.dk/jobsoegning?page={page}&q={j}%27&subid=1&subid=3&subid=4&subid=6&subid=93"
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, "html.parser")
            fetched_jobs = soup.find_all("div", {"class": ["PaidJob", "jix_robotjob"]})
            job_listings += fetched_jobs
            page += 1

        print(len(job_listings))
        # # TODO: Needs error handling
        for job_ad in job_listings:
            job = job_ad.find("h4")
            title = job.text.strip()
            url = job.find("a")["href"]

            try:
                company = job_ad.find("div", {"class": "jix-toolbar-top__company"}).text.strip()
            except:
                location = "Unknown"
            print(company)
            try:
                location = job_ad.find("span",  {"class": "jix_robotjob--area"}).text.strip()
            except:
                location = "Unknown"

            if title and company in jobs:
                continue

            driver.set_page_load_timeout(5)
            try:
                driver.get(url)
                time.sleep(1)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                texts = soup.findAll(text=True)
                visible_texts = filter(tag_visible, texts)
                description = " ".join(t.strip() for t in visible_texts)
                lang = detect(description)
                print(lang)
            except TimeoutException:
                print("TimeoutException")
                description = "Unknown"
            print("=====================================")

            jobs.append({"title": title, "company": company, "location": location, "link": url, "description": description, "language": lang})
    return jobs


def scrape_job_descriptions(urls):
    job_descriptions = []
    for url in urls:
        driver.get(url)
        time.sleep(0.2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        job_descriptions.append(" ".join(t.strip() for t in visible_texts))
    return job_descriptions

jobs = scrape_jobs(["\"Data+Science\"", "Softwareudvikler", "\"Machine+Learning\"", "Datalog"])
print(len(jobs)) 

csv_file = "job_info.csv"
with open(csv_file, mode="w", newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["title", "company", "location", "link", "description", "language"])
    writer.writeheader()
    for job in jobs:
        writer.writerow(job)
