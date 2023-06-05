from bs4 import BeautifulSoup
import requests
import json
import time

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

def scrapeUrl(startUrl):  
    # Make a request to the website
    response = requests.get(url=startUrl)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    divColl = soup.body.find(id="initials")
    
    jsonString = json.loads(divColl.get_text())
    
    
    output = {}
    for obj in jsonString['smartRecruiterResult']['content']:
        department = ''
        if('label' not in obj['department'].keys()):
            department = "None Type"
        else:
            department = obj['department']['label']

        if(department not in output.keys()):
            output[department] = []
            
        job_info = obj['ref']
        
        output[department].append(scrapeJobInfo(job_info))
        print("Completed for: ",obj['name'])
    
    return output
    
    
def main():
    startURL = "https://www.cermati.com/karir/lowongan"
    
    print("Start Scraping for: ", startURL)
    result =  scrapeUrl(startURL)
    
    print("\n\n-------------------------\n\n Scraping Completed \n\n-------------------------\n\n")
    
    json_obj = json.dumps(result, indent=4)
    
    print("Writing File now")
    with open("sample_without_multiTasking.json", "w") as file:
        file.write(json_obj)
    print("COMPLETED: YOU CAN CHECK THE OUTPUT 'sample_without_multiTasking.json' NOW")


start = time.time()
if __name__ == "__main__":
    main()
end = time.time()

print(f'\n\nTOTAL TIME TAKEN: {end - start}\n\n')