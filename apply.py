
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


import time
import yaml
import random
from bs4 import BeautifulSoup 
import csv
from datetime import datetime,timedelta
from pathlib import Path
import pandas as pd

from postioin_role import UI_roles,ML_roles,QA_roles

def Main():
    fileLocation ="configs/example(ML).yaml"  
    
    with open(fileLocation,'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc
    with open(fileLocation,'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc
    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0
    assert parameters['username'] is not None
    assert parameters['password'] is not None
    assert parameters['phone_number'] is not None
    username = parameters['username']
    password = parameters['password']
    #phonenumber = parameters['phone_number']
    locations = [l for l in parameters['locations'] if l is not None]
    role_type = parameters['role_type']
    if role_type == 'ML':
        positions = ML_roles
    elif role_type == "QA":
        positions = QA_roles
    elif role_type == "UI":
        positions = UI_roles

    # positions = [l for l in parameters['positions'] if l is not None]
    blacklist = parameters.get('blacklist',[])
    blacklisttitles = parameters.get('blackListTitles',[])
    uploads = {} if parameters.get('uploads', {}) is None else parameters.get('uploads', {})
    outputfilename = f"Output/Output_of_{parameters['username']}.csv"
    experiencelevel = parameters.get('experience_level',[])
    rate = parameters['rate']
    salary = parameters['salary']
    roletype = parameters.get('roletype',[])
    gender = parameters['gender']
    for key in uploads.keys():
        assert uploads[key] is not None
    
    ApplyBot(username=username,
             password=password,
             #phonenumber=phonenumber
             locations=locations,
             salary=salary,
             uploads=uploads,
             blacklist=blacklist,
             blacklisttitles=blacklisttitles,
             experiencelevel=experiencelevel,
             positions=positions,
             rate=rate,
             roletype=roletype,gender=gender,filename=outputfilename)
    

class ApplyBot():
    def __init__(self,
                 username,
                 password,
                 phonenumber,gender,
                 salary,rate,filename,uploads={},
                 blacklist=[],blacklisttitles=[],experiencelevel=[],locations=[],positions= [],roletype=[]):
        self.username = username
        self.password = password
        self.phonenumber = phonenumber
        self.salary = salary
        self.rate = rate
        self.uploads = uploads
        #self.resume_path = getFull_path_Resume(uploads["Resume"])
        self.roletype = roletype
        self.filename = filename
        self.blacklist = blacklist
        self.blacklisttitles = blacklisttitles
        self.experiencelevel = experiencelevel
        self.locations=locations
        self.positions=positions
        service = Service(ChromeDriverManager().install())
        
        self.driver = webdriver.Chrome(service=service)

        self.wait= WebDriverWait(self.driver,30)
        self.gender = gender
        self.qa_file = Path(f"Qa/qa_{self.username}.csv")
        self.answer = {}

        if self.qa_file.is_file():
            df = pd.read_csv(self.qa_file)
            for index,row in df.iterrows():
                self.answer[row['Question']]= row["Answer"]
        else:
            df = pd.DataFrame(columns=["Question","Answer"])
            df.to_csv(self.qa_file,index=False,encoding='utf-8')

        
        self.locator = {
            "non_easy_apply_button": (By.XPATH, '//button[contains(@class, "jobs-apply-button")]'),
            "links": (By.XPATH, '//div[@data-job-id]'),
            "search": (By.CLASS_NAME, "jobs-search-results-list")
        }


        print(f"--------------------------the Candidate Selected for Marketing is {self.username}------------------------------")
        print(f'{self.phonenumber}\n')
        print(f'{self.salary}\n')
        print(f'{self.uploads}\n')
        print(f'{self.experiencelevel}\n')
        print(f'{self.locations}\n')
        print(f'{self.positions}\n')
        print('Linkedin Login is initiated')
        self.login_linkedin()
        

    def login_linkedin(self):
        self.driver.get('https://www.linkedin.com/login')
        self.sleep()
        self.driver.find_element(By.ID, 'username').send_keys(self.username)
        self.driver.find_element(By.ID, 'password').send_keys(self.password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        #sleeping for the page to load 
        self.sleep(10)
        self.findingCombos_postion_location()

    def sleep(self,sleeptime =random.randrange(3,6) ):
        #this function will sleep for a random amount of time between 0 - 5sec
        randomtime = sleeptime
        print(f"Application is sleeping for a random time of {randomtime} seconds")
        time.sleep(randomtime)
    
    def fill_data(self) -> None:
        self.driver.set_window_size(1, 1)
        self.driver.set_window_position(2000, 2000)

    def roletypestr_convertion(self):
        rolearr = self.roletype
        if rolearr==[]:
            return ""
        elif rolearr ==[1] or rolearr==[2] or rolearr==[3]:
            return f"&f_WT={str(rolearr[0])}"
        elif rolearr == [1,2]:
            return "&f_WT=1%2C3"
        elif rolearr == [1,3]:
            return "&f_WT=1%2C2"
        elif rolearr == [2,3]:
            return "&f_WT=3%2C2"
        elif rolearr == [1,2,3]:
            return "&f_WT=1%2C3%2C2"
    def findingCombos_postion_location(self):
        combolist : list = []
        while len(combolist)<len(self.positions)*len(self.locations):
            for i in self.positions:
                for j in self.locations:
                    combo: tuple = (i,j)
                    combolist.append(combo)
                    self.Get_job_application_page(position=i,location=j)
        
    def Get_job_application_page(self,location,position):
        # construct the experience level part of URL
        exp_lvl_str = ",".join(map(str,self.experiencelevel)) if self.experiencelevel else ""
        exp_lvl_param = f"&f_E={exp_lvl_str}" if exp_lvl_str else ""
        location_str = f"&location={location}"
        position_str = f"&keywords={position}"
        Job_per_page = 0
        self.sleep()
        rolestring = self.roletypestr_convertion()
        print(f"Searching for the location= {location} and job = {position} ")
        #URL = "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords="+position_str+str(rolestring)+location_str+exp_lvl_param+"&start="+str(Job_per_page)
        URL = "https://www.linkedin.com/jobs/search/?keywords="+position_str+str(rolestring)+location_str+exp_lvl_param+"&start="+str(Job_per_page)
        
        self.driver.get(URL)
        #sleeping for 10 sec for page load
        self.sleep(10)
        try:
            TotalresultsFound = self.driver.find_element(By.XPATH,"//*[@id='main']/div/div[2]/div[1]/header/div[1]/small/div/span")
            self.sleep(2)
            resultsFoundnumber = ''.join(re.findall(r'\d',TotalresultsFound.text))
            Job_Search_Results_count = int(resultsFoundnumber)
        except Exception as e:
            Job_Search_Results_count = 0
        print(f"-----------------------This is the total count fo the results that can be get --{Job_Search_Results_count}----------------------------------------------------")
        while Job_per_page<Job_Search_Results_count:
            #URL = "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords="+position_str+rolestring+location_str+exp_lvl_param+"&start="+str(Job_per_page)
            
            URL = "https://www.linkedin.com/jobs/search/?keywords="+position_str+rolestring+location_str+exp_lvl_param+"&start="+str(Job_per_page)
            self.driver.get(URL)
            self.sleep()
            self.Load_page_Scroll_page()
            if self.is_present(self.locator["search"]):
                scrollresult = self.get_elements("search")
                for i in range(300,3000,100):
                    self.driver.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollresult[0])
                scrollresult = self.get_elements("search")
                self.sleep(1)


            if self.is_present(self.locator["links"]):
                links = self.get_elements("links")
                jobIDs = {} #{Job id: processed_status}
            
                # children selector is the container of the job cards on the left
                for link in links:
                        print(f"the link.text is {link.text}")
                        if 'Applied' not in link.text: #checking if applied already
                            if link.text not in self.blacklist: #checking if blacklisted
                                jobID = link.get_attribute("data-job-id")
                                if jobID == "search":
                                    print("Job ID not found, search keyword found instead? {}")
                                    continue
                                else:
                                    jobIDs[jobID] = "To be processed"
                if len(jobIDs) > 0:
                    self.job_apply_loop(jobIDs)
            Job_per_page+=25
        return
    def job_apply_loop(self,jobIDS):
        for jobID in jobIDS:
            if jobIDS[jobID] == "To be processed":
                try:
                    applied = self.Start_applying_with_jobid(jobID)
                except Exception as e:
                    print(e)
                    continue

    def Start_applying_with_jobid(self,jobid):
        #navigating to the job page with the help of jobID 
        self.Get_Job_page_with_jobid(jobid)

        self.sleep(4)
        #find the easy apply  button in the page

        button = self.get_apply_button_urls()

    def Get_Job_page_with_jobid(self,jobID):
        joburl :str ="https://www.linkedin.com/jobs/view/"+str(jobID)
        self.driver.get(joburl)
        self.job_page = self.Load_page_Scroll_page()
        self.sleep(1)
        return self.job_page

    def Load_page_Scroll_page(self):
        scrollpage = 0
        while scrollpage<4000:
            self.driver.execute_script("window.scrollTo(0,"+str(scrollpage)+");")
            scrollpage+=500
            self.sleep(0.2)
        self.sleep()
        self.driver.execute_script("window.scrollTo(0,0);")
        page = BeautifulSoup(self.driver.page_source,'lxml')
        return page
    
    def is_present(self, locator):
        return len(self.driver.find_elements(locator[0],
                                              locator[1])) > 0
    
    def get_elements(self, type) -> list:
        elements = []
        element = self.locator[type]
        if self.is_present(element):
            elements = self.driver.find_elements(element[0], element[1])
        return elements
    
    def get_apply_button_urls(self):
        apply_urls = set()
        try:
            buttons = self.get_elements("non_easy_apply_button")
            for button in buttons:
                button_text = button.text.strip()
                if "Easy Apply" in button_text:
                    print("Ignoring button with text: 'Easy Apply'")
                    continue
                elif "Apply" in button_text:
                    print("Clicking button with text: 'Apply'")
                    original_url = self.driver.current_url
                    self.wait.until(EC.element_to_be_clickable(button)).click()
                    time.sleep(5)  # Wait longer for the new window to open

                    # Check if a new window/tab has opened
                    if len(self.driver.window_handles) > 1:
                        # Switch to the new window
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        new_url = self.driver.current_url
                        print(f"Extracted URL: {new_url}")

                        # Save the URL to urls.txt if it's different from the original
                        if new_url != original_url:
                            apply_urls.add(new_url)
                            with open("urls.txt", "a") as file:
                                file.write(new_url + "\n")

                        # Close the new window and switch back to the main window
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    else:
                        print("No new window opened after clicking 'Apply'.")
                time.sleep(2)  # Small delay between button clicks
        except Exception as e:
            print(f"Exception in get_apply_button_urls: {e}")
        return apply_urls

Main()
