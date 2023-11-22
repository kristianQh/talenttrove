import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def scrape_jobs(job):
    search_url = f"https://www.jobindex.dk/jobsoegning?q={job}&subid=1&subid=2&subid=3&subid=4&subid=6&subid=93&subid=116"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # TODO: Needs error handling
    job_listings = soup.find_all("div", {"class": "PaidJob"})
    jobs = []
    for job_ad in job_listings:
        job = job_ad.find("h4")
        title = job.text
        link = job.find("a")["href"]

        company = job_ad.find("div", {"class": "jix-toolbar-top__company"}).find("a").text

        try:
            location = job_ad.find("span",  {"class": "jix_toolbar--location"}).text
        except:
            location = "Unknown"
        jobs.append({"title": title, "company": company, "location": location, "link": link})

    return jobs


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

options = Options()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

## !! OCR MAYBE??

def scrape_job_descriptions(urls):
    job_descriptions = []
    for url in urls:
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        job_descriptions.append(" ".join(t.strip() for t in visible_texts))
    return job_descriptions

jobs = scrape_jobs("\"machine+learning\"")
descriptions = scrape_job_descriptions([job["link"] for job in jobs[:6]])
print(descriptions[2])