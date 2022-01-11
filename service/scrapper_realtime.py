import firebase_admin
from firebase_admin import db
from firebase_admin import credentials


import re
import enum
import time
import os, gc
import zipfile
from selenium import webdriver
import dateutil.parser as parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains



PATH = "service\chromedriver"
url = "https://www.tuempleord.do/"
exception_time = 10

cred = credentials.Certificate("service/config/files/realtime.json")
default_app = firebase_admin.initialize_app(
    cred, {'databaseURL': "https://jobs-realtime-default-rtdb.firebaseio.com"})


def realtime_scrapper():

    from datetime import datetime
    todayDate = datetime.now()

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(PATH,options=options)
   
    
    jobs_arr = []
    
    driver.get(url)
    time.sleep(4)
    jobs_list = driver.find_elements(By.CLASS_NAME, "job_listing")
    time.sleep(2)
    
    for x in jobs_list:

        each_List = x.find_elements(By.TAG_NAME, "a")

        for y in each_List:

            href = y.get_attribute('href')

            object = {"href": href}
            jobs_arr.append(object)
            
    
    
    
    driver.delete_all_cookies()
    driver.close()
    driver.quit()
    time.sleep(2)
    
    
    for y in jobs_arr:
        
        driver_2 = webdriver.Chrome(PATH,options=options)
        action = ActionChains(driver_2)
        driver_2.get(y["href"])
        time.sleep(3)
        
        
        job_title = driver_2.find_element(By.ID,"title").find_element(By.TAG_NAME,"h1").text
        job_category = ''.join([i for i in str(driver_2.find_element(By.ID,"title").find_element(By.CLASS_NAME,"job-type").text) if not i.isdigit()])
        job_date = driver_2.find_element(By.CLASS_NAME,"posted-date").text
        job_description = driver_2.find_element(By.CLASS_NAME,"job_description").text
        job_location = str(driver_2.find_element(By.CLASS_NAME,"location").text).split(":")[1]
        
        time.sleep(10)
        driver_2.execute_script("window.scrollTo(0, 768)")
        driver_2.execute_script('document.getElementsByClassName("application_button")[0].click()')
        time.sleep(2)
        
        job_email = driver_2.find_element(By.CLASS_NAME,"job_application_email").text
        time.sleep(2)

        y["title"]    = job_title
        y["date"]     = str(todayDate)
        y["desc"]     = job_description
        y["loc"]      = job_location
        y["category"] = job_category
        y["dateReg"]  = str(todayDate)
        y["email"]    = job_email
        y["content"]  = job_description

        driver_2.close()
        
  
    time.sleep(2)

    
    for i, item in enumerate(jobs_arr):

        try:
            time.sleep(2)

            
            ref = db.reference('Jobs')

            data = ref.order_by_child("title").equal_to(item["title"]).get()

            if data:
                for key,values in data.items():
                    
                    old_job_date = parser.parse(values["date"])
                    new_job_date = parser.parse(item["date"])

                    resutl1 = datetime.strftime(old_job_date, '%m-%d-%Y')
                    resutl2 = datetime.strftime(new_job_date, '%m-%d-%Y')

                    if (resutl1 != resutl2):
                        ref.push(item)
            else:
                    ref.push(item)


           

        except:
            time.sleep(exception_time)
            realtime_scrapper()


    gc.collect()
    time.sleep(300)
    realtime_scrapper()