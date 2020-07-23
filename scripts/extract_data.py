import re
import string
import pickle
import numpy as np
import pandas as pd
from time import sleep
from datetime import date
from os import listdir, makedirs
from  bs4    import BeautifulSoup
from  urllib.request import Request,urlopen
from selenium import webdriver
from selenium.webdriver.support.ui import Select

def get_span(page):
    return int(page.find("table",attrs={"id":"grdFPISWH"}).findAll("td")[-1].get("colspan"))
def extract_table(driver,date):
    page=BeautifulSoup(driver.page_source,'lxml')
    table=page.find("table",attrs={"id":"grdFPISWH"}).findAll("td")[5:-1]       
    raw=[date]
    data=[]
    for i in table:
        if re.findall('IN',i.getText()):
            data.append(raw)
            raw=[date]
        raw.append(i.getText())       
    return data[1:]

login = "test"
chromeOptions = webdriver.ChromeOptions() 
chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) 
chromeOptions.add_argument("--no-sandbox") 
chromeOptions.add_argument("--disable-setuid-sandbox") 

chromeOptions.add_argument("--remote-debugging-port=9222")  # this

chromeOptions.add_argument("--disable-dev-shm-using") 
chromeOptions.add_argument("--disable-extensions") 
chromeOptions.add_argument("--disable-gpu") 
chromeOptions.add_argument("start-maximized") 
chromeOptions.add_argument("disable-infobars") 
chromeOptions.add_argument("--headless") 
chromeOptions.add_argument(r"user-data-dir=.\cookies\\" + login) 

deal_url="https://www.ccilindia.com/FPI_ARCV.aspx"
driver = webdriver.Chrome(chrome_options=chromeOptions)
driver.get(deal_url)

select = driver.find_element_by_id('drpArchival')
all_options=select.find_elements_by_tag_name("option")

select_list=[]
for i in all_options:
    select_list.append(i.get_attribute("value"))

result=[]
for date in select_list[1:]:
    Select(driver.find_element_by_id('drpArchival')).select_by_value(date)
    page=BeautifulSoup(driver.page_source,'lxml')
    print(date)
    colspan=get_span(page)
    result+=extract_table(driver,date)
    for i in range(1,colspan):
        driver.find_element_by_xpath("//table[@id='grdFPISWH']/tbody/tr/td/a[{}]".format(i)).click()
        result+=extract_table(driver,date)
datatable=pd.DataFrame(result,columns=['Date', 'ISIN', 'Security Description', 
                                 'Indicative Value Of Aggregate Holding Of FPIS (INR CR#)', 
                                  'Outstanding Position Of Govt# Securities (INR CR#)',
                                  'Sec Holdings (%)'
                                 ])
datatable.to_csv('datatable.csv', header=False, index=False)

driver.quit()

