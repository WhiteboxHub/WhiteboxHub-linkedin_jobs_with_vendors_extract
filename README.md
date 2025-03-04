# LinkedIn Jobs with Vendors Extract

## Overview
`linkedin_jobs_with_vendors_extract` is a Python-based automation tool that uses **Selenium** to search for job listings on LinkedIn, extract job application links, and categorize them based on external vendor platforms like **Lever, Greenhouse, jobvite, workable,ashbyhq etc.**

## Features
- **Automated LinkedIn Login**
- **Job Search Automation** (based on YAML configuration)
- **Filtering of "Apply" Jobs**
- **Extraction of External Job Application Links**
- **Categorization of Links by Vendor Platform**

## Prerequisites
Make sure you have the following installed:
- **Python 3.8+**
- **Google Chrome** (latest version)
- **Chrome WebDriver** (managed via `webdriver_manager`)

## Installation & Setup
### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/linkedin_jobs_with_vendors_extract.git
cd linkedin_jobs_with_vendors_extract
```

### 2. Create and Activate a Virtual Environment
#### On Windows:
```sh
python -m venv venv
venv\Scripts\activate
```
#### On macOS/Linux:
```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

## Configuration
Before running the bot, update the **YAML configuration file** (`configs/example(ML).yaml`) with your LinkedIn credentials and job search parameters:
```yaml
username: "your-email@example.com"
password: "yourpassword"
locations: ["New York, NY", "San Francisco, CA"]
role_type: "ML"
salary: "100000"
rate: "hourly"
experience_level: [2, 3]
blacklist: []
blackListTitles: []
uploads: {}
```

## Running the Bot
```sh
python main.py
```

## File Structure
```
linkedin_jobs_with_vendors_extract/
│── configs/
│   ├── example(ML).yaml  # Configuration file
│── Output/               # Extracted job application links
│── Qa/                   # QA data for question-answer handling
│── postioin_role.py      # Defines ML/UI/QA roles (ensure it's present)
│── main.py               # Main bot script
│── requirements.txt      # Dependencies
│── README.md             # Documentation
```


