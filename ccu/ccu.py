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



def get_auto_loan(auto_loan_url, bankName, bankUrl, bankID,driver):
   
    
    driver.get("https://www.ccuflorida.org/home/rates/loan")
    
    
    #new
    year=driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[13]/td[2]').text
    rate=driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[13]/td[3]').text
    
    pattern = r'\d+'
    pattern2 = r'\d+\.\d+'
    matches = re.findall(pattern, year)
    matches2=re.findall(pattern2, rate)
    if matches:
        nmax_year = int(matches[0])/12
        nmin_rate=float(matches2[0])
        print(nmax_year)
        print(nmin_rate)
    else:
        print("No integer found")


    #used
    year = []
    rate = []

    year17 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[14]/td[2]').text
    year20 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[15]/td[2]').text
    year22 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[16]/td[2]').text
    year.append([year17, year20, year22])

    rate17 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[14]/td[3]').text
    rate20 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[15]/td[3]').text
    rate22 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[16]/td[3]').text
    rate.append([rate17, rate20, rate22])
    print(year)
    print(rate)
    # Extracting year and rate from the lists
    year_list = [re.findall(r'\d+', y)[0] for y in year[0]]
    rate_list = [float(re.findall(r'\d+\.\d+', r)[0]) for r in rate[0]]

    # Finding minimum and maximum year and rate
    min_year = min([int(y)/12 for y in year_list])
    max_year = max([int(y)/12 for y in year_list])
    min_rate = min(rate_list)
    max_rate = max(rate_list)

    # Printing the results
    print(f"Minimum year: {min_year}")
    print(f"Maximum year: {max_year}")
    print(f"Minimum rate: {min_rate:.2f}%")
    print(f"Maximum rate: {max_rate:.2f}%")
    
    info1 = { "type": "new", "urlLink": "https://www.ccuflorida.org/home/rates/loan","minPeriod": '', "maxPeriod": nmax_year,"rateFrom":nmin_rate, "rateTo":'', "maxAmount": ""}
    info2 = { "type": "used", "urlLink": "https://www.ccuflorida.org/home/rates/loan","minPeriod":int(min_year), "maxPeriod":  int(max_year),"rateFrom":min_rate, "rateTo": max_rate, "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1,info2]}}
    return dic
    

def get_personal_loan(url, bankName, bankUrl, bankID,driver):
    
   
    
    driver.get("https://www.ccuflorida.org/home/rates/loan")
    
    
    typ = 'personalLoan'
    year = []
    rate = []

    year1 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[3]/td[2]').text
    year2 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[6]/td[2]').text
    year.append([year1, year2])

    rate1 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[3]/td[3]').text
    rate2 = driver.find_element_by_xpath('//*[@id="rates_loan"]/tbody/tr[6]/td[3]').text

    rate.append([rate1, rate2])
    
    # Extracting year and rate from the lists
    year_list = [re.findall(r'\d+', y)[0] for y in year[0]]
    rate_list = [float(re.findall(r'\d+\.\d+', r)[0]) for r in rate[0]]

    # Finding minimum and maximum year and rate
    min_year = min([int(y)/12 for y in year_list])
    max_year = max([int(y)/12 for y in year_list])
    min_rate = min(rate_list)
    max_rate = max(rate_list)

    # Printing the results
    print(f"Minimum year: {min_year}")
    print(f"Maximum year: {max_year}")
    print(f"Minimum rate: {min_rate:.2f}%")
    print(f"Maximum rate: {max_rate:.2f}%")
       
    
    
    info = { "type": typ, "urlLink": "https://www.ccuflorida.org/home/rates/loan","minPeriod": '', "maxPeriod": max_year, "rateFrom": min_rate, "rateTo": '', "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'personalLoan', "itemType":[info]}}
    return dic


def get_mortgages_2(url, bankName, bankUrl, bankID,driver):
    
    driver.get("https://www.ccuflorida.org/home/rates/mortgage")
    
    min_term = float('inf')
    max_term = float('-inf')
    min_rate = float('inf')
    max_rate = float('-inf')
    min_apr = float('inf')
    max_apr = float('-inf')

    rmin_term = float('inf')
    rmax_term = float('-inf')
    rmin_rate = float('inf')
    rmax_rate = float('-inf')
    rmin_apr = float('inf')
    rmax_apr = float('-inf')
  
    # find all rows with PURCHASE in the Term column
    rows = driver.find_elements_by_xpath("//tr[contains(td[1], 'PURCHASE')]")
    rows2 = driver.find_elements_by_xpath("//tr[contains(td[1], 'REFINANCE')]")
    # extract data for each row
    for row in rows:
        term = row.find_element_by_xpath("td[1]").text
        rate = row.find_element_by_xpath("td[2]").text
        apr = row.find_element_by_xpath("td[3]").text
        # print(term.replace('YEAR FIXED - PURCHASE',''), rate, apr)
        term = int(term.replace('YEAR FIXED - PURCHASE',''))
        rate = float(rate.rstrip('%'))
        apr = float(apr.rstrip('%'))
        if term < min_term:
            min_term = term
        if term > max_term:
            max_term = term
        if rate < min_rate:
            min_rate = rate
        if rate > max_rate:
            max_rate = rate
        if apr < min_apr:
            min_apr = apr
        if apr > max_apr:
            max_apr = apr
    for row in rows2:
        rterm = row.find_element_by_xpath("td[1]").text
        rrate = row.find_element_by_xpath("td[2]").text
        rapr = row.find_element_by_xpath("td[3]").text
        # print(term.replace('YEAR FIXED - PURCHASE',''), rate, apr)
        rterm = int(rterm.replace('YEAR FIXED - REFINANCE',''))
        rrate = float(rrate.rstrip('%'))
        rapr = float(rapr.rstrip('%'))
        if rterm < rmin_term:
            rmin_term = rterm
        if rterm > rmax_term:
            rmax_term = rterm
        if rrate < rmin_rate:
            rmin_rate = rrate
        if rrate > rmax_rate:
            rmax_rate = rrate
        if rapr < rmin_apr:
            rmin_apr = rapr
        if rapr > rmax_apr:
            rmax_apr = rapr
    
    info1 = { "type": 'refinance', "urlLink": url,"minPeriod": rmin_term, "maxPeriod": rmax_term, "aprFrom": rmin_apr, "aprTo": rmax_apr, "rateFrom": rmin_rate, "rateTo": rmax_rate, "maxAmount": "", "variableAPR":False, "fixedAPR": True}
    info2 = { "type": 'purchase', "urlLink": url,"minPeriod": min_term, "maxPeriod":  max_term, "aprFrom": min_apr, "aprTo": max_apr, "rateFrom":min_rate, "rateTo": max_rate, "maxAmount": "", "variableAPR":False, "fixedAPR": True}
    
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": "mortgageLoan", "itemType":[info1,info2]}}
    return dic
# get_mortgages_2('url', 'bankName', 'bankUrl', 'bankID')




def get_heloc(url, bankName, bankUrl, bankID,driver):
    
    #__________________________default_values
    loanType = "helocLoan"
    type1 = 'helocLoan'
    description = ''
    itemType=[]
    #__________________________scraping
    driver.get("https://www.ccuflorida.org/home/rates/home")
    
    
  
    year=driver.find_element_by_xpath('//*[@id="rates_home_primeHeloc"]/tbody/tr[2]/td[1]').text
    rate=driver.find_element_by_xpath('//*[@id="rates_home_primeHeloc"]/tbody/tr[2]/td[2]').text.split('-')
    # print(rate)
    min_rate=rate[0]
    max_rate=rate[1]
    pattern = r'\d+'
   
    matches = re.findall(pattern, year)
   
    if matches:
        max_year = int(matches[0])
        
        # print(max_year)
       
    else:
        print("No integer found")


    
    info = {"type": type1,
            "urlLink": "https://www.ccuflorida.org/home/rates/home",
            "minPeriod": '',
            "maxPeriod": max_year,
            "rateFrom": min_rate,
            "rateTo": max_rate,
            "maxAmount": "",
            "ltvFrom": '',
            "ltvTo": 80,
            "description": year,
            "default": True
            }
    
    itemType.append(info)
    
  
    dic = {"bankName": bankName, "bankID": bankID, "date": time.strftime("%m-%d-%Y"),
          "timestamp": time.strftime("%m-%d-%Y %H:%M:%S"), "bankUrl": bankUrl,
          "bankDetails": {"loanType": loanType, "itemType": itemType}}

    return dic
def parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url):
    
    bankName = 'ccu'
    bankUrl = 'https://www.ccuflorida.org/home/rates'
    bankID = 787995
    options =Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('disable-infobars')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument(f'--remote-debugging-port=9221')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=f"ncsecu\chrome\chromedriver.exe", options=options)
    driver.maximize_window()
    try:
      itemType1 = get_auto_loan(auto_loan_url, bankName, bankUrl, bankID,driver)
    except:
      itemType1 = {}
    try:
      itemType2 = get_personal_loan(personal_loan_url, bankName, bankUrl, bankID,driver)
    except:
      itemType2 = {}
        
    try:
      itemType3 = get_mortgages_2(mortgage_loan_url, bankName, bankUrl, bankID,driver)
    except:
      itemType3 = {}
    try:
      itemType4 = get_heloc(heloc, bankName, bankUrl, bankID,driver)
    except:
      itemType4 = {}

    dic = [itemType1, itemType2, itemType3, itemType4] 
    # dic = json.dumps(dic)

    print('dic')
    print(dic)
    validatedDictList = data_validation(dic)
    print('validatedDictList')
    print(validatedDictList)
    
    return validatedDictList

def fetch_data():
   
    auto_loan_url = 'https://www.ccuflorida.org/home/rates/loan'
    mortgage_loan_url = 'https://www.ccuflorida.org/home/rates/mortgage'
    personal_loan_url = 'https://www.ccuflorida.org/home/rates/loan'
   
    get_heloc='https://www.ccuflorida.org/home/rates/home'
    output = parse(get_heloc, auto_loan_url,mortgage_loan_url, personal_loan_url)
    print(output)
    returnstr = "[" + ','.join(map(str, output))
    returnstr = returnstr + "]"
    return returnstr
fetch_data()