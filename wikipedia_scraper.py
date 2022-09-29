import requests
from bs4 import BeautifulSoup as bs
import re
from functools import lru_cache
import json
from concurrent.futures import ThreadPoolExecutor

cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

#@hashable_cache
@lru_cache(maxsize = None)
def get_first_paragraph(wikipedia_url, session_param):
#     print(wikipedia_url)
    req= session_param.get(wikipedia_url) # requests changed by session_param
    content = req.text
    soup = bs(content, 'html')
    
    #remove all the text link
    for a in soup.findAll('a', href=True):
        a.extract()
        
    paragraphs = soup.find_all('p')

    #looking for first paragraph
    first_paragraph_index = 0
    i = 0   
    for paragraph in soup.find_all("p"):   
        if paragraph.find('b') != None:
            first_paragraph_index = i            
            break
        i+=1
    
    #use first_paragraph_index to access the first paragraph
    first_paragraph = paragraphs[first_paragraph_index].text
    
    if wikipedia_url.startswith('https://en.'): #to reduce conflict with other language characters
        first_paragraph = re.sub(r'[();{}[\]]+', "", first_paragraph)
        sanitized_paragraph = ' '.join(first_paragraph.strip().split())
    else:
        sanitized_paragraph = first_paragraph
   
    return sanitized_paragraph


def get_leaders():
    global countries
    
    root_url = "https://country-leaders.herokuapp.com"
    cookie_url = root_url + "/cookie"
    country_url = root_url + "/countries"
    leaders_url = root_url + "/leaders"

    req_cookies = requests.get(cookie_url)
    cookies=req_cookies.cookies
   
    req_countries = requests.get(country_url, cookies = cookies)
    countries = req_countries.text
#     print(countries)
    
    countries = countries.strip('[, ]')
    countries = countries.split(",")    
    
    session = requests.Session()

    global leaders_per_country
    leaders_per_country = {}
    for country in countries:
        country = country.replace('\"', "")
        param = {'country': country}
        
        req_leaders = requests.get(leaders_url, cookies =cookies, params = param)
        
        #check if cookies expired, if so creat it again
        if req_leaders.status_code == 403:
            cookies=req_cookies.cookies
            req_leaders = requests.get(leaders_url, cookies =cookies, params = param)
            
        content = req_leaders.text    
        content = content.strip('[, ]')
        list_leaders_currentcountry = content.split('}')

        with ThreadPoolExecutor() as pool:
            clean_leader_info_percountry = list(pool.map(get_simplified_info, list_leaders_currentcountry, session))

        leaders_per_country[country] = clean_leader_info_percountry
    return leaders_per_country     




def get_simplified_info(list_leaders_currentcountry, session):
    #         print(".......... \nleaders info started here \n")
        clean_leader_info_percountry = []
        for leader_info in list_leaders_currentcountry:
            leader_info_clean = leader_info.strip('{, }')
            list_leader_info = leader_info_clean.split(',')
            leader_fname = ""
            leader_lname = ""
            wiki_url = ""
            
            leader_info_dict={}
            
            for info in list_leader_info:                
                if 'wikipedia' in info:
                    wiki_split = info.split(':')
                    wiki_url = (wiki_split[1] + ":" + wiki_split[2]).replace("\"", "")
                elif "first_name" in info:
                    leader_fname = info.split(':')[1].replace("\"", "")
                    
                elif "last_name" in info:
                    leader_lname = info.split(':')[1].replace("\"", "")
                    
                
                if leader_fname == "" or leader_lname == "" or wiki_url == "":
                    continue
                else:
                    break #has to break out from this loop because no neet to travel to all information
            
            #break
            try: 
                first_paragraph = get_first_paragraph(wiki_url, session)  
            except:
                first_paragraph = "first paragraph could not be extracted. Either link not found or link has error"
                  
            print(leader_fname + " " + leader_lname + ",  " + wiki_url )
            print(first_paragraph)
            leader_info_dict['first_name'] = leader_fname
            leader_info_dict['last_name'] = leader_lname
            leader_info_dict['wikipedia_url'] = wiki_url
            leader_info_dict['first_paragraph'] = first_paragraph
            
            clean_leader_info_percountry.append(leader_info_dict) #list of leaders info for current country under the loop

        return clean_leader_info_percountry




#save generated dictionary of files into the given directory
def save(dir = "C:/BeCode/LocalRepos/output_all_country/"):
    for country in countries:
        try:
            country = country.replace('\"', "")
            file_name = dir + country + "_leaders.json"
            json_file = open(file_name, 'w')
            json_file.write(json.dumps(leaders_per_country.get(country)))
            json_file.close()
        except IOError:
            print("cant write the file content in the country: " + country)
        else:
            print("file successfully written")
            
    
def read_leaders_info(country='us'):
    try:
        file_name = "C:/BeCode/LocalRepos/Wikipedea_Scrapper/output/" + country + "_leaders.json"
        file_json = open(file_name, 'r')
        data = json.load(file_json)
        file_json.close()
    except IOError:
        print("problem with reading file, check if it exists")
    else:
        return data



# def main():
#     get_leaders()
#     save()


# if __name__ == "__main__":
#     main()

get_leaders()
save()