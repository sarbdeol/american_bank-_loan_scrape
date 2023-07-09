import requests
from scrapy.http import HtmlResponse
import json
import pprint
import re
import time
import datetime
import threading
from time import sleep
from google.cloud import firestore
import time
from requests import get
from bs4 import BeautifulSoup as bs
from pickle import TUPLE2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def data_validation(dataDictList):
    url = "https://us-central1-lendmesh.cloudfunctions.net/data-validation"

    payload = json.dumps(dataDictList)
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)



def get_auto_loan(auto_loan_url, bankName, bankUrl, bankID):
   
    
    
    options =Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('disable-infobars')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument(f'--remote-debugging-port=9221')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=f"E:/Bank project/ncsecu/chrome/chromedriver.exe", options=options)
    driver.get("https://www.becu.org/loans-and-mortgages/auto")
    typ = 'autoLoan'
    driver.execute_script("window.scrollTo(0, 200);")
    zip=driver.find_element_by_xpath('//*[@id="zip-text-box"]')
    time.sleep(2)
    zip.clear()
    # print('click')
    time.sleep(1)
    zip.send_keys('12345')
    
    driver.find_element_by_xpath('//*[@id="maincontent"]/article/div/div[1]/div[1]/div[3]/div[2]/div[1]/form/button').click()
    time.sleep(3)
    newrate=driver.find_element_by_xpath('//*[@id="maincontent"]/article/div/div[1]/div[1]/div[2]/div[2]/span[1]').text
    
    usedrate=driver.find_element_by_xpath('//*[@id="maincontent"]/article/div/div[1]/div[1]/div[2]/div[3]/span[1]').text
    info1 = { "type": "new", "urlLink": "https://www.becu.org/loans-and-mortgages/recreational-vehicle","minPeriod": '', "maxPeriod": '',"rateFrom":newrate, "rateTo":'', "maxAmount": ""}
    info2 = { "type": "used", "urlLink": "https://www.becu.org/loans-and-mortgages/recreational-vehicle","minPeriod": '', "maxPeriod":  '',"rateFrom":usedrate, "rateTo": '', "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1,info2]}}
    return dic
    

def get_personal_loan(url,  bankName, bankUrl, bankID):
    
   
  
    r  = get("https://www.becu.org/loans-and-mortgages/personal")
    soup = bs(r.content,'html.parser')
    
    typ = 'personalLoan'
    h3_tag = soup.find('h3', class_='text-h1')
    rate_text = h3_tag.text.strip()
    rate_value = rate_text.split()[0]    
    
    info = { "type": typ, "urlLink": "https://www.becu.org/loans-and-mortgages/personal","minPeriod": '', "maxPeriod": '6', "rateFrom": rate_value, "rateTo": '', "maxAmount": "30,000"}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'personalLoan', "itemType":[info]}}
    return dic

def get_student_loan(url, bankName, bankUrl, bankID):
    
    r1  = get('https://www.becu.org/loans-and-mortgages/student-loans/private-student-loans')
    soup = bs(r1.content,'html.parser')
    h3_tag = soup.find('h3', class_='text-h1')
    rate_text = h3_tag.text.strip()
    rate_value1 = rate_text.split()[0]

    r2  = get('https://www.becu.org/loans-and-mortgages/student-loans/refinance-student-loans')
    soup = bs(r2.content,'html.parser')
    h3_tag = soup.find('h3', class_='text-h1')
    rate_text = h3_tag.text.strip()
    rate_value2 = rate_text.split()[0]

    info1 = { "type": "newLoan", "urlLink":"https://www.becu.org/loans-and-mortgages/student-loans/private-student-loans","minPeriod": '', "maxPeriod":  '', "rateFrom": rate_value1, "rateTo": '', "maxAmount": "100,000", "variableAPR":False, "fixedAPR": True}
    info2 = { "type": "refinance", "urlLink":"https://www.becu.org/loans-and-mortgages/student-loans/refinance-student-loans","minPeriod": '', "maxPeriod": '', "rateFrom": rate_value2, "rateTo": '', "maxAmount": "125,000", "variableAPR":False, "fixedAPR": True}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'studentLoan', "itemType":[info1,info2]}}
    return dic

def get_mortgages_2(url, bankName, bankUrl, bankID):
  
    url = 'https://www.becu.org/rates/mortgage-rates'

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = bs(response.content, 'html.parser')

    rates = soup.select('div.no-pluses:nth-of-type(5) .rate')


    min_rate = float('inf')
    max_rate = float('-inf')

    for rate in rates:
        rate_text = rate.get_text().strip() # extract the text and remove any whitespace
        rate_percent = re.findall(r'\d+\.\d+', rate_text)[0] # use regex to find the percentage value
        
        rate_value_str = rate_percent
        rate_value_num = float(re.findall(r'\d+\.\d+', rate_value_str)[0])
        min_rate = min(min_rate, rate_value_num)
        max_rate = max(max_rate, rate_value_num)

    print('Minimum rate:', min_rate)
    print('Maximum rate:', max_rate)

  #
    rates = soup.select('div.no-pluses:nth-of-type(4) .rate')


    rmin_rate = float('inf')
    rmax_rate = float('-inf')

    for rate in rates:
        rate_text = rate.get_text().strip() # extract the text and remove any whitespace
        rate_percent = re.findall(r'\d+\.\d+', rate_text)[0] # use regex to find the percentage value
        
        rate_value_str = rate_percent
        rate_value_num = float(re.findall(r'\d+\.\d+', rate_value_str)[0])
        rmin_rate = min(rmin_rate, rate_value_num)
        rmax_rate = max(rmax_rate, rate_value_num)

    print('Minimum rate:', rmin_rate)
    print('Maximum rate:', rmax_rate)
    info1 = { "type": 'refinance', "urlLink": url,"minPeriod": 15, "maxPeriod": 30, "aprFrom": rmin_rate, "aprTo": rmax_rate, "rateFrom": '', "rateTo": '', "maxAmount": "", "variableAPR":False, "fixedAPR": True}
    info2 = { "type": 'purchase', "urlLink": url,"minPeriod": 5, "maxPeriod": 7, "aprFrom": min_rate, "aprTo": max_rate, "rateFrom": '', "rateTo": '', "maxAmount": "", "variableAPR":True, "fixedAPR": False}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": "mortgageLoan", "itemType":[info1,info2]}}
    return dic
# get_mortgages_2('url', 'bankName', 'bankUrl', 'bankID')

def get_home_Equity():
    r  = ("https://www.becu.org/loans-and-mortgages/home-loans/fixed-rate")
    response = requests.get(r)
    soup = bs(response.content, "html.parser")

    rates = []
    for rate in soup.find_all("h3", {"class": "text-h1"}):
        rate_text = rate.text.strip()
        if "%" in rate_text:
            rates.append(rate_text)

    print(rates)
        
    rates1 = []
    for rate_with_apr in rates:
        # Use regular expression to extract only the rate value from the string
        rate_match = re.search(r'\d+\.\d+', rate_with_apr)
        if rate_match:
            rates1.append(rate_match.group())
    print(rates1[1])
    
   
    info1 = {"type": "homeEquity",  "urlLink": "https://www.becu.org/loans-and-mortgages/home-loans/fixed-rate",  "minPeriod":'',  "maxPeriod": 30,  "rateFrom": '',  "rateTo": rates1[1],  "maxAmount": 726200,  "ltvFrom": '',  "ltvTo": "",  "description": "",  "default": True  }
    return [info1]
    


def get_heloc(url, bankName, bankUrl, bankID):
    
    #__________________________default_values
    loanType = "helocLoan"
    type1 = 'helocLoan'
    description = ''

    #__________________________scraping
    soup = bs(requests.get('https://www.becu.org/loans-and-mortgages/home-loans/home-equity').content,'html.parser')
    apr_list = []
    for h3 in soup.find_all('h3', class_= 'text-h1'):
       
        apr_value = h3.get_text(strip=True).replace('%APR','')
        apr_list.append(apr_value)

    itemType = []
    info = {"type": type1,
            "urlLink": "https://www.becu.org/loans-and-mortgages/home-loans/home-equity",
            "minPeriod": '',
            "maxPeriod": '',
            "rateFrom": min(apr_list),
            "rateTo": min(apr_list),
            "maxAmount": "",
            "ltvFrom": '',
            "ltvTo": "80",
            "description": description,
            "default": True
            }

    itemType.append(info)
    itemType = itemType+get_home_Equity()
    dic = {"bankName": bankName, "bankID": bankID, "date": time.strftime("%m-%d-%Y"),
          "timestamp": time.strftime("%m-%d-%Y %H:%M:%S"), "bankUrl": bankUrl,
          "bankDetails": {"loanType": loanType, "itemType": itemType}}

    return dic
def parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url, student_loan_url):
    
    bankName = 'becu'
    bankUrl = 'https://www.becu.org/loans-and-mortgages'
    bankID = 787995
    

    try:
      itemType1 = get_auto_loan(auto_loan_url, bankName, bankUrl, bankID)
    except :
      itemType1 = {}
    try:
      itemType2 = get_personal_loan(personal_loan_url, bankName, bankUrl, bankID)
    except:
      itemType2 = {}
    try:
        itemType3 = get_student_loan(student_loan_url, bankName, bankUrl, bankID)
    except:
      itemType3 = {}
        
    try:
      itemType4 = get_mortgages_2(mortgage_loan_url, bankName, bankUrl, bankID)
    except:
      itemType4 = {}
    try:
      itemType5 = get_heloc(heloc, bankName, bankUrl, bankID)
    except:
      itemType5 = {}

    dic = [itemType1, itemType2, itemType3, itemType4,itemType5] 
    # dic = json.dumps(dic)

    print('dic')
    print(dic)
    validatedDictList = data_validation(dic)
    print('validatedDictList')
    print(validatedDictList)
    
    return validatedDictList

def fetch_data():
   
    auto_loan_url = 'https://www.becu.org/loans-and-mortgages/recreational-vehicle'
    mortgage_loan_url = 'https://www.becu.org/rates/mortgage-rates'
    personal_loan_url = 'https://www.becu.org/loans-and-mortgages/personal'
    student_loan_url = "https://www.becu.org/loans-and-mortgages/student-loans/private-student-loans"
    get_heloc='https://www.becu.org/loans-and-mortgages/home-loans/home-equity'
    output = parse(get_heloc, auto_loan_url,mortgage_loan_url, personal_loan_url, student_loan_url)
    print(output)
    returnstr = "[" + ','.join(map(str, output))
    returnstr = returnstr + "]"
    return returnstr
fetch_data()