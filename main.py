import os
import time
import random
import yaml
import pandas as pd
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from postioin_role import ML_roles

OUTPUT_FOLDER = "output"
OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, "links_extracted.csv")


class ApplyBot:
    def __init__(self, username, password, filename,
                 blacklist=[], blacklisttitles=[], experiencelevel=[], locations=[], positions=[]):
        self.username = username
        self.password = password
        self.filename = filename
        self.blacklist = blacklist
        self.blacklisttitles = blacklisttitles
        self.experiencelevel = experiencelevel
        self.locations = locations
        self.positions = positions

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 30)

        self.locator = {
            "non_easy_apply_button": (By.XPATH, '//button[contains(@class, "jobs-apply-button")]')
        }

        print(f"Candidate: {self.username} | Experience: {self.experiencelevel} | Locations: {self.locations} | Positions: {self.positions}")
        self.login_linkedin()

    def login_linkedin(self):
        self.driver.get('https://www.linkedin.com/login')
        self.sleep()
        self.driver.find_element(By.ID, 'username').send_keys(self.username)
        self.driver.find_element(By.ID, 'password').send_keys(self.password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.sleep(10)
        self.process_job_search()

    def sleep(self, sleeptime=random.randrange(3, 6)):
        print(f"Sleeping for {sleeptime} seconds...")
        time.sleep(sleeptime)

    def process_job_search(self):
        for position in self.positions:
            for location in self.locations:
                self.search_and_extract(position, location)

    def search_and_extract(self, position, location):
        print(f"Searching for jobs: {position} in {location}")
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={position}&location={location}"
        self.driver.get(search_url)
        self.sleep(5)

        self.scroll_and_load_page()

        job_links = self.extract_apply_links()
        for job_url in job_links:
            self.process_and_save_job_info(job_url)

    def scroll_and_load_page(self):
        for i in range(0, 3000, 500):
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            self.sleep(1)

    def extract_apply_links(self):
        apply_urls = set()
        try:
            buttons = self.driver.find_elements(*self.locator["non_easy_apply_button"])
            for button in buttons:
                button_text = button.text.strip()
                if "Apply" in button_text and "Easy Apply" not in button_text:
                    original_url = self.driver.current_url
                    self.wait.until(EC.element_to_be_clickable(button)).click()
                    time.sleep(3)

                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        new_url = self.driver.current_url
                        if new_url != original_url:
                            apply_urls.add(new_url)
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            print(f"Error extracting Apply links: {e}")
        return list(apply_urls)

    def process_and_save_job_info(self, job_url):
        platform, company, job_id = extract_platform_company_jobid(job_url)
        save_extracted_data(platform, company, job_id)


def extract_platform_company_jobid(url):
    """Extracts platform, company name, and job ID from the given URL."""
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')

    if "greenhouse" in domain_parts:
        platform = "Greenhouse"
    elif "lever" in domain_parts:
        platform = "Lever"
    elif "ashbyhq" in domain_parts:
        platform = "AshbyHQ"
    elif "jobvite" in domain_parts:
        platform = "Jobvite"
    else:
        platform = domain_parts[-2] if len(domain_parts) > 1 else parsed_url.netloc

    path_parts = parsed_url.path.strip('/').split('/')
    company_name, job_id = "Unknown", "Unknown"

    if platform in ["Greenhouse", "Lever", "AshbyHQ", "Jobvite"]:
        if len(path_parts) >= 3:
            company_name = path_parts[0]
            job_id = path_parts[-1]
    else:
        if len(path_parts) >= 2:
            company_name = path_parts[0]
            job_id = path_parts[-1]

    return platform, company_name, job_id


def save_extracted_data(platform, company, job_id):
    """Saves extracted job data in a structured table format (Excel-compatible CSV)"""

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0

    if file_exists:
        df = pd.read_csv(OUTPUT_CSV)
        new_id = len(df) + 1
    else:
        new_id = 1

    data = pd.DataFrame([[new_id, platform, company, job_id]], 
                         columns=["ID", "Platform Name", "Company Name", "Job ID"])

    data.to_csv(OUTPUT_CSV, mode='a', header=not file_exists, index=False, encoding="utf-8-sig")

    print(f" Saved: ID={new_id}, Platform={platform}, Company={company}, Job ID={job_id}")


def Main():
    fileLocation = "configs/user_auth.yaml"

    with open(fileLocation, 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0
    assert parameters['username'] is not None
    assert parameters['password'] is not None

    username = parameters['username']
    password = parameters['password']
    locations = [l for l in parameters['locations'] if l is not None]
    role_type = parameters['role_type']

    if role_type == 'ML':
        positions = ML_roles

    blacklist = parameters.get('blacklist', [])
    blacklisttitles = parameters.get('blackListTitles', [])
    experiencelevel = parameters.get('experience_level', [])

    ApplyBot(
        username=username,
        password=password,
        filename=OUTPUT_CSV,
        blacklist=blacklist,
        blacklisttitles=blacklisttitles,
        experiencelevel=experiencelevel,
        positions=positions,
        locations=locations
    )


Main()
