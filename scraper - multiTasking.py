from bs4 import BeautifulSoup
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import time


#global variable that will hold the end result
output = {}


#this will scrape more details about the job
def scrapeJobInfo(job_info):
    
    job_deatils = {}
    
    title = ''
    location = ''
    description = []
    qualification = []
    job_type = ''
    postedBy = 'Not mentioned'
    company = ''
    
    response = requests.get(url=job_info)
    job_info_json = json.loads(response.content)
    
    
    title = job_info_json["name"]
    company = job_info_json["company"]["name"]
    job_type = job_info_json["typeOfEmployment"]["label"]
    location = job_info_json["location"]["city"]
    for x in job_info_json["customField"]:
        if(x["fieldId"] == "COUNTRY"):
            location = location + ', ' + x["valueLabel"]

    soup = BeautifulSoup(job_info_json["jobAd"]["sections"]["jobDescription"]["text"], 'html.parser')
    liTag = soup.find_all('li')
    for li in liTag:
        temp = str(li.get_text().encode("ascii", "ignore"))
        description.append(temp[2:-1])
        
    soup = BeautifulSoup(job_info_json["jobAd"]["sections"]["qualifications"]["text"], 'html.parser')
    liTag = soup.find_all('li')
    for li in liTag:
        temp = str(li.get_text().encode("ascii", "ignore"))
        qualification.append(temp[2:-1])
        

    job_deatils['title'] = title
    job_deatils['location'] = location
    job_deatils['description'] = description
    job_deatils['qualification'] = qualification
    job_deatils['job_type'] = job_type
    job_deatils['postedBy'] = postedBy
    job_deatils['company'] = company

    return job_deatils


# this function will divide the task in multiple executors
def multi_tasking(obj):
    print(' In progress: ' + obj['name'])
    department = ''
    if('label' not in obj['department'].keys()):
        department = "None Type"
    else:
        department = obj['department']['label']

    if(department not in output.keys()):
        output[department] = []
        
    job_info = obj['ref']
    
    # we will get a dictonary from the function and we will append that in our end result
    output[department].append(scrapeJobInfo(job_info))
    
    return obj['name']


def scrapeUrl(startUrl):  
    # Make a request to the website
    response = requests.get(url=startUrl)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    #found all the jobs inside this id
    divColl = soup.body.find(id="initials")
    
    #all jobs were combined in a JSON format so creating josn object out if it 
    jsonString = json.loads(divColl.get_text())
    
    
    # Create a ThreadPoolExecutor with a maximum of 5 threads
    with ThreadPoolExecutor(max_workers=6) as executor:
        # Submit the scraping tasks to the executor
        futures = [executor.submit(multi_tasking, jsonString) for jsonString in jsonString['smartRecruiterResult']['content']]

        # Wait for all tasks to complete
        for future in futures:
            print('completed for: ', future.result())
    
    
    
def main():
    startURL = "https://www.cermati.com/karir/lowongan"
    
    print("Start Scraping for: ", startURL)
    scrapeUrl(startURL)
    
    json_obj = json.dumps(output, indent=4)
    print("\n\n-------------------------\n\n Scraping Completed \n\n-------------------------\n\n")
    
    print("Writing File now")
    with open("sample_with_multiTasking.json", "w") as file:
        file.write(json_obj)
    print("COMPLETED: YOU CAN CHECK THE OUTPUT 'sample_with_multiTasking.json' NOW")
    

start = time.time()
if __name__ == "__main__":
    main()
end = time.time()

print(f'\n\nTOTAL TIME TAKEN: {end - start}\n\n')