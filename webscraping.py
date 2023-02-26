## Webscraping progrram that will download the RealEstate data from MagicBricks website
## and store the results as a CSV file with nname final.csv
## Format of data is 
## 'name','location','builder', 'bhk', 'bedroom', 'housetype', 'price', 'price in Lac', 'carpet area', 'status', 'transatcion', 'furnishing', 
## 'parking', 'park_count','bath', "balcony", "ownership", "facing", "society"

from logging import exception
from typing import Dict
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, re, csv, traceback, datetime, shutil , os
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

p_start = start = int(time.time())
def wait_for_ajax(driver):
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        print ("Exception in wait_for_ajax")
        print(e)
        pass


def merge_files(source, target):
    data = data2 = "" 
    
    # Reading data from file1 
    with open(source) as fp: 
        data = fp.read() 
    
    # Reading data from file2 
    with open(target) as fp: 
        data2 = fp.read() 
    
    # Merging 2 files 
    # To add the data of file2 
    # from next line 
    #data += "\n"
    data += data2 
    
    with open ("tmp.txt", 'w') as fp: 
        fp.write(data) 
    
    # Delete xfile.txt
    os.remove(target)
    shutil.move("tmp.txt", target)

#Initialize Final.csv file
data = ""
with open ("Final.csv", 'w') as fp: 
    fp.write(data) 

def get_location_from_name(name,society):
    #t1=name.strip().split(" in ")
    location = "NA"
    name = name.replace('in ','')
    name = name.replace(society, "")
    location = name;
    return location

def info_extract_from_container2(container):
    
    bldr_elem_div = (container.find_all("div",class_="m-srp-card__summary__item")) 
    attributes = dict({})
    for idx, container in enumerate(bldr_elem_div):
        try:
            title_elem_div = (container.find_all("div",class_="m-srp-card__summary__title")) 
            bldr = title_elem_div[0].text.replace('\n', ' ').replace('\r', '').replace("  ", " ")
            bldr = bldr.replace('\u20b9','')
            bldr = bldr.strip().encode("utf-8").decode("utf-8")
            #any letter that is not a nummber, word or . is blaked out below
            title = re.sub(r"[^\w\s.]", '', bldr)
            #print ("\t\t" + title)
            
            info_elem_div = (container.find_all("div",class_="m-srp-card__summary__info")) 
            bldr = info_elem_div[0].text.replace('\n', ' ').replace('\r', '').replace("  ", " ")
            bldr = bldr.replace('\u20b9','')
            bldr = bldr.strip().encode("utf-8").decode("utf-8")
            #any letter that is not a nummber, word or . is blaked out below
            info = re.sub(r"[^\w\s.]", '', bldr)
            #print (title+"\t\t" + info)
            attributes[title] = info
        except Exception as e:
            print ("Exception in info_extract_from_container2")
            print(e)
            traceback.print_exc() 
        pass  
    return attributes


'''
From the container, extract the relevant value based on class_id
Example: area = info_extract_from_container(container,class_id="m-srp-card__summary__info")
'''
def info_extract_from_container(container, class_id, id=0):
    bldr = ""
    try:
        bldr_elem_div = (container.find_all("div",class_=class_id)) 
        bldr_elem_span = (container.find_all("span",class_=class_id))
        if bldr_elem_div:
            bldr = bldr_elem_div[id]
        elif bldr_elem_span:
            bldr = bldr_elem_span[id]
        bldr = bldr.text.replace('\n', ' ').replace('\r', '').replace("  ", " ")
        bldr = re.sub(r'\s+',' ',bldr)
        bldr = bldr.replace('\u20b9','')
        bldr = bldr.strip().encode("utf-8").decode("utf-8")
        #any letter that is not a nummber, word or . is blaked out below
        bldr = re.sub(r"[^\w\s.]", '', bldr)
    except Exception as e:
       print ("\tException in info_extract_from_container")
       print(e)
       pass  
    return bldr


        
def write_container_to_csv(i, house_containers, file_name):
    with open(file_name, mode='w', newline='') as re_file:
        re_writer = csv.writer(re_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if i == 0:
            re_writer.writerow(['name','location','builder', 'bhk', 'bedroom', 'housetype', 'price', 'price in Lac', 'carpet area', 'status', 'transatcion', 'furnishing', 
                            'parking', 'park_count',
                            'bath', "balcony", "ownership", "facing", "society"])   
        if house_containers:
            #row = [] 
            for idx, container in enumerate(house_containers):
                row = [] 
                attributes = info_extract_from_container2(container)
                bhk = info_extract_from_container(container,"m-srp-card__title__bhk")
                name = info_extract_from_container(container,class_id="m-srp-card__title")
                name = re.sub(r'\d\s+BHK\s+(Flat|Apartment|Villa)\s+for Sale','',name)
                society =  attributes.get("society","NA")
                location = get_location_from_name(name,society)
                row.append(name)
                row.append(location)
                #print("-----")
                tmp = re.findall('\d*',bhk)
                bedroom=0     
                if tmp[0]: 
                    bedroom =  int(tmp[0])
                
                tmp = re.findall('(Apartment|Flat|Floor|Penthouse)',bhk)
                housetype=''
                if tmp and tmp[0]: 
                    housetype =  'Flat'
                tmp = re.findall('(Villa|House)',bhk)
                if tmp and tmp[0]: 
                    housetype =  'House'

                
                #print("-----")
                bldr = info_extract_from_container(container,class_id="m-srp-card__advertiser__name")
                row.append(bldr)
                row.append(bhk)
                row.append(bedroom)
                row.append(housetype)
                price = info_extract_from_container(container,"m-srp-card__price")
                price_value = 0
                try:
                    price_value =  float(re.findall('\d*\.?\d*',price)[0])
                    if re.search("Cr", price ): 
                        price_value = price_value * 100
                except Exception as ex:
                    print(ex)
                    pass
                row.append(price)
                row.append(price_value)

                attributes = info_extract_from_container2(container)

                area = info_extract_from_container(container,class_id="m-srp-card__summary__info")
                area = attributes.get("carpet area","NA")
                area = area.encode("utf-8").decode("utf-8")
                if (len(re.findall(r'\d+', area))):
                    area = re.findall(r'\d+', area)[0]
                row.append(area)

                #possession_by = info_extract_from_container(container,class_id="m-srp-card__summary__info",id=1)
                possession_by =  attributes.get("status","NA")
                row.append(possession_by)

                #transaction = info_extract_from_container(container,class_id="m-srp-card__summary__info",id=2)
                transaction =  attributes.get("transaction","NA")
                row.append(transaction)

                #furnishing = info_extract_from_container(container,class_id="m-srp-card__summary__info",id=3)
                furnishing =  attributes.get("furnishing","NA")
                row.append(furnishing)

                #parking = info_extract_from_container(container,class_id="m-srp-card__summary__info",id=5)
                parking =  attributes.get("car parking","NA")
                row.append(parking)
                tmp = re.findall('\d*',parking)
                park_count=0     
                if tmp[0]: 
                    park_count =  int(tmp[0])
                row.append(park_count)

                #bath = info_extract_from_container(container,class_id="m-srp-card__summary__info",id=6)
                bath =  attributes.get("bathroom","NA")
                row.append(bath)

                balcony =  attributes.get("balcony","NA")
                row.append(balcony)

                ownership =  attributes.get("ownership","NA")
                row.append(ownership)

                facing =  attributes.get("facing","NA")
                row.append(facing)

                society =  attributes.get("society","NA")   
                row.append(society)
                #print("\tprocessing:" + str(idx))
                #print(str(idx) + "|\t" + name + "|\t" + bhk + "|\t" + bldr + "|\t" + area + "|\t" + price + "|\t" + possession_by +
                #            "|\t" + transaction  + "|\t" + furnishing + "|\t" + parking + "|\t" + bath )
                re_writer.writerow(row)
            #print("----------------------------------")

options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--incognito");

#options.headless = True
pause = 10
driver = webdriver.Chrome(chrome_options=options)
#driver.set_window_position(10, 10)
#driver.set_window_size(500, 500)
driver.get("https://www.magicbricks.com/property-for-sale/residential-real-estate?proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName=Pune")
#This code will scroll down to the end
no_of_pagedowns = 250
prev_house_container_count = 0
while no_of_pagedowns:
    try:
        doc_height = driver.execute_script("return document.documentElement.scrollHeight")
        print("\t" + str(no_of_pagedowns) + "<-- Page down count down | Doc Size --> " + str(doc_height))
        #driver.execute_script("window.scrollTo(0," + str(doc_height - 750 ) + ")")
        print( "Pull of browser  down")
        driver.execute_script("window.scrollTo(0," + str(doc_height)  + ")")
        wait_for_ajax(driver)
        driver.execute_script("window.scrollTo(0," + str(doc_height - 750)  + ")")
        wait_for_ajax(driver)
    except Exception as e:
        print ("Exception in when dragging scroller down")
        print(e)
        pass

    print( "AJAX Wait Done")
    time.sleep(5)
    no_of_pagedowns -= 1
    start = int(time.time())
    TIMEOUT = 10
    print( "Check of browser pulled down")
    while True:   
        html_soup = BeautifulSoup(driver.page_source, 'html.parser')
        house_containers = html_soup.find_all('div', class_="m-srp-card__container")
        house_containers_count = len(house_containers)
        #print( "Check of new entries old --> new ["  + str(prev_house_container_count) + "-->" +  str(house_containers_count) + "]")
        if house_containers_count > prev_house_container_count:
            break
        time.sleep(1)
        if int(time.time()) > start + TIMEOUT:
            print("Timeout from scroll")
            break
    print(  str(prev_house_container_count) + "|" +  str(house_containers_count))
    subset_house_container = house_containers[prev_house_container_count:house_containers_count]
    file_name = "tmp\\RE-" + str(no_of_pagedowns) + ".csv"
    write_container_to_csv(no_of_pagedowns, subset_house_container, file_name)
    merge_files(file_name,"final.csv")
    prev_house_container_count = house_containers_count

html_soup = BeautifulSoup(driver.page_source, 'html.parser')
house_containers = html_soup.find_all('div', class_="m-srp-card__container")
print(len(house_containers))



driver.close()
driver.quit()
p_stop = start = int(time.time())
n = p_stop - p_start
print ("Program Exec Time:" + str(datetime.timedelta(seconds = n)))


