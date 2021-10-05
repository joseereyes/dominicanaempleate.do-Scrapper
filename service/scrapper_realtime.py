import enum
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import zipfile
import os, gc
import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

PATH = "service/chromedriver"
url = "https://www.tuempleord.do/"
exception_time = 10

cred = credentials.Certificate("service/config/files/realtime.json")
default_app = firebase_admin.initialize_app(
    cred, {'databaseURL': "https://jobs-realtime-default-rtdb.firebaseio.com"})


def realtime_scrapper():
    
    driver = webdriver.Chrome(PATH)

    try:
        driver.get(url)
        time.sleep(2)
        jobs_list = driver.find_elements_by_class_name("articulo")
    except:
        driver.close()
        time.sleep(exception_time)
        realtime_scrapper()

    
    jobs_arr = []

    for x in jobs_list:

        title = x.find_element_by_class_name("resumido").text
        category = x.find_element_by_class_name("categoria").text
        date = x.find_element_by_class_name("date").text
        desc = x.find_element_by_class_name("resumen").text
        loc = x.find_element_by_class_name("provincia").text
        href = x.find_element_by_class_name("ver-mas").get_attribute('href')

        object = {
            "title": title.replace("/"," "),
            "date": date,
            "desc": desc,
            "loc": loc,
            "href": href,
            "category": category
        }
        jobs_arr.append(object)
        


    time.sleep(1)
    driver.delete_all_cookies()
    driver.close()
    driver.quit()

    for i, item in enumerate(jobs_arr):

        try:
            index = webdriver.Chrome(PATH)
            index.get(item["href"])
            time.sleep(2)
            job_body = index.find_element_by_class_name("contenido")
            item["content"] = job_body.text
       
            email = re.findall(r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+",item["content"])

            if len(email) > 0:

                item["email"] = email[0]
                ref = db.reference('Jobs')
                item_title = str(item["title"].replace(".",""))
                data = ref.child(item_title).get()
                
                if data is None:
                
                    ref.child(str(item_title)).set(item)
                else:
                    if item["date"] != data["date"]:
                        item_title = str(item_title) + str(" dominicanaempleate do " + item["date"])
                        ref.child(item_title).set(item)

            else:
                del jobs_arr[i]
            
            index.delete_all_cookies()
            index.close()
            index.quit()
            
            del index
            gc.collect()
            
        except:
            index.close()
            time.sleep(exception_time)
            realtime_scrapper()
            
    
    time.sleep(300)
    realtime_scrapper()
