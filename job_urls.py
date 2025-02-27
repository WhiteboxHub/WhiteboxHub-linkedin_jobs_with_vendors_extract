import os
from urllib.parse import urlparse

def detect_platform(domain):
    
    platforms = {"lever": "lever_set.txt",
                  "jobvite": "jobvite_set.txt",
                  "greenhouse": "greenhouse_set.txt",
                  "workable": "workable_set.txt",
                  "iCIMS" : "iCIMS_set.txt",
                  "SmartRecruiters":"SmartRecruiters_set.txt",
                  "BambooHR" : "BambooHR_set.txt",
                  "ashbyhq" : "ashbyhq_set.txt"


                  }
    
    for platform, filename in platforms.items():
        if platform in domain:
            return filename
    return None

def categorize_links(input_file, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    categorized_links = {
        "lever_set.txt": set([]),
        "jobvite_set.txt": set([]),
        "greenhouse_set.txt": set([]),
        "workable_set.txt" : set([]),
        "iCIMS_set.txt" : set([]),
        "SmartRecruiters_set.txt" : set([]),
        "BambooHR_set.txt" :set([]),
        "ashbyhq_set.txt" :set([])
        }
    
    with open(input_file, 'r') as file:
        links = file.readlines()
    
    for link in links:
        link = link.strip()
        if not link:
            continue
        
        domain = urlparse(link).netloc
        filename = detect_platform(domain)
        
        if filename:
            categorized_links[filename].append(link)
    
    for filename, links in categorized_links.items():
        output_path = os.path.join(output_folder, filename)
        with open(output_path, 'w') as txtfile:
            txtfile.write("\n".join(links))


categorize_links("urls.txt", "output")



