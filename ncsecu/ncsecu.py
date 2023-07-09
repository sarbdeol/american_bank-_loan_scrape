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
import os
var=os.getcwd()
print(var)
def data_validation(dataDictList):
    url = "https://us-central1-lendmesh.cloudfunctions.net/data-validation"

    payload = json.dumps(dataDictList)
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

def get_personal_loan():
    
    pass
get_personal_loan()
  


def get_auto_loan(url,  bankName, bankUrl, bankID):

    options =Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('disable-infobars')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument(f'--remote-debugging-port=9221')
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=f"ncsecu/chrome/chromedriver.exe", options=options)

    
    driver.get("https://www.ncsecu.org/AutoLoans/VehicleLoans.html#newcar")
    #new loans
    min_rate=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[5]/div[3]/div[2]').text
    max_rate=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[5]/div[8]/div[2]').text

    min_term=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[5]/div[3]/div[3]').text.replace('Months','')
    max_term=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[5]/div[8]/div[3]').text.replace('Months','')
    min_term=int(min_term)/12
    max_term=int(max_term)/12
    #used
    umin_rate=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[6]/div[3]/div[2]').text
    umax_rate=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[6]/div[6]/div[2]').text
    umin_term=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[6]/div[3]/div[3]').text.replace('Months','')
    umax_term=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div[6]/div[6]/div[3]').text.replace('Months','')
    umin_term=int(umin_term)/12
    umax_term=int(umax_term)/12


    info1 = { "type": "new", "urlLink": "https://www.ncsecu.org/AutoLoans/VehicleLoans.html#newcar","minPeriod": min_term, "maxPeriod": max_term,"rateFrom":min_rate, "rateTo":max_rate, "maxAmount": ""}
    info2 = { "type": "used", "urlLink": "https://www.ncsecu.org/AutoLoans/VehicleLoans.html#newcar","minPeriod": umin_term, "maxPeriod":umax_term,"rateFrom":umin_rate, "rateTo":umax_rate, "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1,info2]}}
    return dic

def get_student_loan(url,  bankName, bankUrl, bankID):
    pass


def get_home_Equity():
   
    pass
        
def get_heloc(url,  bankName, bankUrl, bankID):
    
    pass

def get_mortgages():


    options =Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('disable-infobars')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument(f'--remote-debugging-port=9221')
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=f"ncsecu/chrome/chromedriver.exe", options=options)

    
    driver.get("https://www.ncsecu.org/Mortgages/AdjustableMortgage.html")
    #new loans
    min_rate=driver.find_element_by_xpath('//*[@id="5YrARM"]/div[1]/div[1]/h4/a/span[1]/strong').text
    max_rate=driver.find_element_by_xpath('//*[@id="5YrARM"]/div[3]/div[1]/h4/a/span[1]/strong').text
    min_apr=driver.find_element_by_xpath('//*[@id="5YrARM"]/div[1]/div[1]/h4/a/span[1]').text.split()
    max_apr=driver.find_element_by_xpath('//*[@id="5YrARM"]/div[3]/div[1]/h4/a/span[1]').text.split()
    print(min_rate,max_rate)
    print(min_apr[8].replace('(',''),max_apr[8].replace('(',''))
get_mortgages()
def parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url, student_loan_url):
    
    bankName = 'americanheritagecu'
    bankUrl = 'https://www.americanheritagecu.org/rates'
    bankID = 787995

    try:
      itemType1 = get_auto_loan(auto_loan_url, bankName, bankUrl, bankID)
    except:
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
      itemType4 = get_mortgages(mortgage_loan_url, bankName, bankUrl, bankID)
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

def fetch_data ():
   
    auto_loan_url = 'https://www.ncsecu.org/AutoLoans/VehicleLoans.html#newcar'
    mortgage_loan_url = 'https://www.americanheritagecu.org/loans/mortgages'
    personal_loan_url = 'https://www.sefcu.com/sefcu-resources-rates?f%5B0%5D=l2_category_taxonomy_term_name%3APersonal%20Loans'
    student_loan_url = "https://www.salliemae.com/landing/student-loans/?__hstc=236286046.7c672951a96099eb0e61adb73b2aefb2.1677262052961.1677334423704.1677338582694.5&__hssc=236286046.1.1677338582694&__hsfp=1483251232&submissionGuid=d003d643-b105-4e8e-ac5f-b9c68124fe65&MPID=3000000007&dtd_cell=SMLRSOPACUCURCOTAAM0847N010000"
    heloc='https://www.americanheritagecu.org/rates#homeEquity'
    output = parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url, student_loan_url)
    print(output)
    returnstr = "[" + ','.join(map(str, output))
    returnstr = returnstr + "]"
    return returnstr
    
fetch_data()