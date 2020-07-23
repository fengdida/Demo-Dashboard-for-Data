import re
import pyodbc
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
login = "test2"
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
chromeOptions.add_argument("--no-sandbox")
chromeOptions.add_argument("--disable-setuid-sandbox")

#chromeOptions.add_argument("--remote-debugging-port=9900")  

chromeOptions.add_argument("--disable-dev-shm-usage")
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

update_date=all_options[1].get_attribute("value")
Select(driver.find_element_by_id('drpArchival')).select_by_value(update_date)
page=BeautifulSoup(driver.page_source,'lxml')
colspan=get_span(page)

result=[]
result+=extract_table(driver,update_date)
for i in range(1,colspan):
    driver.find_element_by_xpath("//table[@id='grdFPISWH']/tbody/tr/td/a[{}]".format(i)).click()
    result+=extract_table(driver,update_date)

ISIN_update=pd.DataFrame(result)[1]
  
server = 'Modular'
database = 'MODULAR'
username = 'SA'
password = 'King.62033600'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

cursor = cnxn.cursor()  
cursor.execute('SELECT DISTINCT(DATE) FROM DATA;')
raw=cursor.fetchone()
list_date=[]
while raw:
    list_date.append(raw[0]) 
    raw=cursor.fetchone()
cursor.execute("SELECT DISTINCT(ISIN) FROM DATA where date='{}';".format(update_date))
raw=cursor.fetchone()
list_ISIN=[]
while raw:
    list_ISIN.append(raw[0])
    raw=cursor.fetchone()
if update_date in list_date:
    for i in range(len(ISIN_update)):
        if ISIN_update[i] not in list_ISIN:
            print(ISIN_update[i])
            cursor.execute('INSERT INTO DATA VALUES '+str(tuple(result[i])))
            cnxn.commit()
else:
    for i in result:
        print(i[1])
        cursor.execute('INSERT INTO DATA VALUES '+str(tuple(i)))
        print('INSERT INTO DATA VALUES '+str(tuple(i)))
        cnxn.commit()

cnxn.close()

driver.quit()
print("done")
