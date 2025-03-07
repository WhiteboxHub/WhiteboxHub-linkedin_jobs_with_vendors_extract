from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time
import yaml
import random
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
import re
import os
from urllib.parse import urlparse, urlunparse
import csv
from position_role import ML_roles, UI_roles, QA_roles

def detect_platform(domain):
    platforms = {
        "lever": "lever",
        "jobvite": "jobvite",
        "greenhouse": "greenhouse",
        "workday": "workday"  
    }
    for platform, platform_name in platforms.items():
        if platform in domain:
            return platform_name
    
def remove_query_parameters(url):
    parsed_url = urlparse(url)
    return urlunparse(parsed_url._replace(query='', fragment=''))

def append_link_to_csv(link, platform, company, job_id, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    csv_filename = "linkedin_jobs_date_time.csv"
    csv_path = os.path.join(output_folder, csv_filename)
    file_exists = os.path.isfile(csv_path)

    if file_exists:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            if rows:
                last_id = int(rows[-1]['id'])
                next_id = last_id + 1
            else:
                next_id = 1
    else:
        next_id = 1

    with open(csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'platform', 'company', 'job_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'id': next_id,
            'platform': platform,
            'company': company,
            'job_id': job_id
        })
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
            "non_easy_apply_button": (By.XPATH, '//button[contains(@class, "jobs-apply-button")]'),
            "links": (By.XPATH, '//div[@data-job-id]'),
            "search": (By.CLASS_NAME, "jobs-search-results-list")
        }

        self.login_to_linkedin()

    def login_to_linkedin(self):
        
        self.driver.get('https://www.linkedin.com/login')
        self.sleep(120)
        self.driver.find_element(By.ID, 'username').send_keys(self.username)
        self.driver.find_element(By.ID, 'password').send_keys(self.password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.sleep(10)
        self.findingCombos_postion_location()

    def sleep(self, sleeptime=random.randrange(3, 6)):
        randomtime = sleeptime
        print(f"Application is sleeping for a random time of {randomtime} seconds")
        time.sleep(randomtime)

    def roletypestr_convertion(self):
        rolearr = []
        if rolearr == []:
            return ""
        elif rolearr == [1] or rolearr == [2] or rolearr == [3]:
            return f"&f_WT={str(rolearr[0])}"
        elif rolearr == [1, 2]:
            return "&f_WT=1%2C3"
        elif rolearr == [1, 3]:
            return "&f_WT=1%2C2"
        elif rolearr == [2, 3]:
            return "&f_WT=3%2C2"
        elif rolearr == [1, 2, 3]:
            return "&f_WT=1%2C3%2C2"

    def findingCombos_postion_location(self):
        combolist = []
        while len(combolist) < len(self.positions) * len(self.locations):
            for i in self.positions:
                for j in self.locations:
                    combo = (i, j)
                    combolist.append(combo)
                    self.Get_job_application_page(position=i, location=j)

    def Get_job_application_page(self, location, position):
        exp_lvl_str = ",".join(map(str, self.experiencelevel)) if self.experiencelevel else ""
        exp_lvl_param = f"&f_E={exp_lvl_str}" if exp_lvl_str else ""
        location_str = f"&location={location}"
        position_str = f"&keywords={position}"
        Job_per_page = 0
        self.sleep()
        rolestring = self.roletypestr_convertion()
        print(f"Searching for the location= {location} and job = {position} ")
        
        
        URL = "https://www.linkedin.com/jobs/search/?keywords=" + position_str + str(rolestring) + location_str + exp_lvl_param +"&start=" + str(Job_per_page)

        self.driver.get(URL)
        self.sleep(10)
        try:
            TotalresultsFound = self.driver.find_element(By.XPATH, "//*[@id='main']/div/div[2]/div[1]/header/div[1]/small/div/span")
            self.sleep(2)
            resultsFoundnumber = ''.join(re.findall(r'\d', TotalresultsFound.text))
            Job_Search_Results_count = int(resultsFoundnumber)
        except Exception as e:
            Job_Search_Results_count = 0
        print(f"-----------------------This is the total count fo the results that can be get --{Job_Search_Results_count}----------------------------------------------------")
        while Job_per_page < Job_Search_Results_count:
            URL = "https://www.linkedin.com/jobs/search/?keywords=" + position_str + rolestring + location_str + exp_lvl_param  + "&start=" + str(Job_per_page)
            self.driver.get(URL)
            self.sleep()
            self.load_and_scroll_page()
            if self.is_present(self.locator["search"]):
                scrollresult = self.get_elements("search")
                for i in range(300, 3000, 100):
                    self.driver.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollresult[0])
                scrollresult = self.get_elements("search")
                self.sleep(1)

            if self.is_present(self.locator["links"]):
                links = self.get_elements("links")
                jobIDs = {}
                for link in links:
                    print(f"the link.text is {link.text}")
                    if 'Applied' not in link.text:
                        if link.text not in self.blacklist:
                            jobID = link.get_attribute("data-job-id")
                            if jobID == "search":
                                print("Job ID not found, search keyword found instead? {}")
                                continue
                            else:
                                jobIDs[jobID] = "To be processed"
                if len(jobIDs) > 0:
                    self.job_apply_loop(jobIDs)
            Job_per_page += 25
        return

    def job_apply_loop(self, jobIDS):
        for jobID in jobIDS:
            if jobIDS[jobID] == "To be processed":
                try:
                    self.Start_extracting_links_with_jobid(jobID)
                except Exception as e:
                    print(e)
                    continue

    def Start_extracting_links_with_jobid(self, jobid):
        self.Get_Job_page_with_jobid(jobid)
        self.sleep(4)
        apply_urls = self.get_apply_button_urls()
        for url in apply_urls:
            cleaned_url = remove_query_parameters(url)
            platform = detect_platform(urlparse(cleaned_url).netloc)
            if platform:
                company = self.extract_company_name(cleaned_url)  
                append_link_to_csv(cleaned_url, platform, company, jobid, "output")


    def Get_Job_page_with_jobid(self, jobID):
        joburl = "https://www.linkedin.com/jobs/view/" + str(jobID)
        self.driver.get(joburl)
        self.job_page = self.load_and_scroll_page()
        self.sleep(1)
        return self.job_page

    def load_and_scroll_page(self):
        scrollpage = 0
        while scrollpage < 4000:
            self.driver.execute_script("window.scrollTo(0," + str(scrollpage) + ");")
            scrollpage += 500
            self.sleep(0.2)
        self.sleep()
        self.driver.execute_script("window.scrollTo(0,0);")
        page = BeautifulSoup(self.driver.page_source, 'lxml')
        return page

    def is_present(self, locator):
        return len(self.driver.find_elements(locator[0], locator[1])) > 0

    def get_elements(self, type) -> list:
        elements = []
        element = self.locator[type]
        if self.is_present(element):
            elements = self.driver.find_elements(element[0], element[1])
        return elements
    def extract_company_name(self, url):
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            if "lever.co" in domain:
                company_name = parsed_url.path.split('/')[1]
            elif "greenhouse.io" in domain:
                company_name = parsed_url.path.split('/')[1]
            elif "jobvite.io" in domain:
                company_name = parsed_url.path.split('/')[1]
            elif "workdayjobs.com" in domain or "myworkdayjobs.com" in domain:
                
                subdomain = domain.split('.')[0]
                if subdomain.startswith("wd"):
                    company_name = domain.split('.')[0]
                else:
                   company_name = subdomain            
                
            return company_name                    
        except Exception as e:
            print(f"Error extracting company name from URL: {e}")
            
            
    def get_apply_button_urls(self):
        apply_urls = set()
        try:
            buttons = self.get_elements("non_easy_apply_button")
            for button in buttons:
                button_text = button.text.strip()
                if "Easy Apply" in button_text:
                
                    continue
                elif "Apply" in button_text:
                    
                    original_url = self.driver.current_url
                    self.wait.until(EC.element_to_be_clickable(button)).click()
                    time.sleep(5)

                    if (len(self.driver.window_handles)) > 1 :
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        new_url = self.driver.current_url
                        
                        if new_url != original_url:
                            apply_urls.add(new_url)

                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])                        
                time.sleep(2)
        except Exception as e:
            print(f"Exception in get_apply_button_urls: {e}")
        print(f"Extracted URLs: {apply_urls}")
        return list(apply_urls)

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
    elif role_type == "UI" :
        positions = UI_roles
    elif role_type == "QA" :
        positions = QA_roles
    blacklist = parameters.get('blacklist', [])
    blacklisttitles = parameters.get('blackListTitles', [])   
    outputfilename = f"Output/Output_of_{parameters['username']}.csv"
    experiencelevel = parameters.get('experience_level', [])
    
    ApplyBot(
        username=username,
        password=password,
        locations=locations,        
        blacklist=blacklist,
        blacklisttitles=blacklisttitles,
        experiencelevel=experiencelevel,
        positions=positions,
        filename=outputfilename
    )

Main()