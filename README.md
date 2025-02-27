
#  Apply Automation

Automate your job application process on LinkedIn using this Python-based tool powered by Selenium.



## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
    - [Clone the Repository](#1-clone-the-repository)
    - [Add Credentials in YAML File](#2-add-credentials-in-yaml-file)
    - [Place Resume in the `resume` Folder](#3-place-resume-in-the-resume-folder)
    - [Install Python 3.10.*](#4-install-python-310)
    - [Create and Activate Virtual Environment](#5-create-and-activate-virtual-environment)
    - [Install Required Dependencies](#6-install-required-dependencies)
    - [Run the Script](#7-run-the-script)
3. [Troubleshooting](#troubleshooting)
4. [Notes](#notes)


## Prerequisites
Before you begin, make sure you have the following installed:
- Python 3.10.* ([Download Python](https://www.python.org/downloads/))
- Git ([Download Git](https://git-scm.com/downloads))
- Google Chrome (latest version)
- A LinkedIn account with valid credentials



## Setup Instructions

### 1. Clone the Repository
Use the following commands to clone the repository and open it in Visual Studio Code:
```bash
git clone https://github.com/WhiteboxHub/linkedin-apply-extract.git
cd linkedin-apply-extract

```

### 2. Add Credentials in YAML File

Navigate to the `config` folder in the project directory.  
create a  `new_config_file.yaml` file and add your LinkedIn credentials and the path to your resume:

```yaml
username: "your_email@example.com"
password: "your_password"
role_type: 'QA' or "ML" or "UI"
locations:
- location1
- location2
uploads:
    resume_path: "./resume/your_resume.pdf"
```


### 3. Place Resume in the `resume` Folder

- Copy your resume file (e.g., `your_resume.pdf`) into the `resume` folder located in the root directory of the project.
- Ensure that the `resume_path` in the `config.yaml` file matches the file name and location.


### 4. Install Python 3.10.*

#### Windows:
- Download Python 3.10 from the [official Python website](https://www.python.org/downloads/) and install it.

#### Mac/Linux:
- Use a package manager like Homebrew:
  
```bash
brew install python@3.10
```

### Create and Activate Virtual Environment

- Create a virtual environment using the following command:

```bash
python3.10 -m venv venv
```

##### Windows:
```bash
venv\Scripts\activate
```

### install the required libraries:
 use the below command and run it in the terminal where the virtual environment is active.pip install numpy pandas PyYAML lxml beautifulsoup4 selenium webdriver-manager

```bash
pip install numpy pandas PyYAML lxml beautifulsoup4 selenium webdriver-manager
```

### 7. Run the Script
 run the `apply.py` script to extract rhe apply button urls in urls.txt :

```bash
python apply.py
```
 run the `jobs_url.py` script to separate the links to their platforms :

```bash
python apply.py
```
