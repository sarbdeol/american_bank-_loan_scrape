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

def data_validation(dataDictList):
    url = "https://us-central1-lendmesh.cloudfunctions.net/data-validation"

    payload = json.dumps(dataDictList)
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)


def get_auto_loan(auto_loan_url, bankName, bankUrl, bankID,driver):
   
    typ = 'autoLoan'

    driver.get('https://www.bayfed.com/products-services/rates/loan-rates')
    # Wait for the dynamic content to load
    driver.implicitly_wait(10)

        # find the rate table
    # find the table element by class name
    table = driver.find_element_by_class_name("ratetable")

    # find all the rows in `the table
    rows = table.find_elements_by_tag_name("tr")

    rates = []
    # iterate through each row starting from the second row
    for row in rows[1:]:
        # find all the cells in the row
        cells = row.find_elements_by_tag_name("td")
        # get the minimum and maximum rates from the second to last cell
        rate1 = cells[1].text.strip()
        rate2 = cells[2].text.strip()
        rate3 = cells[3].text.strip()
        rate4 = cells[-1].text.strip()

        if rate1:
            rates.append(float(rate1.replace('%', '')))
        if rate2:
            rates.append(float(rate2.replace('%', '')))
        if rate3:
            rates.append(float(rate3.replace('%', '')))
        if rate4:
            rates.append(float(rate4.replace('%', '')))

    # remove any empty values
    rates = [r for r in rates if r]
    # print(rates)

    # print the result
    min_rate = min(rates)
    max_rate = max(rates)
    # print("Minimum rate: {}%".format(min_rate))
    # print("Maximum rate: {}%".format(max_rate))


    info1 = { "type": "new", "urlLink": 'https://www.bayfed.com/products-services/rates/loan-rates',"minPeriod": 4, "maxPeriod":7,"rateFrom": min_rate, "rateTo": max_rate, "maxAmount":  "70,000"}

    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1]}}
    
    return dic


def get_personal_loan(url,  bankName, bankUrl, bankID,driver):
    
    # print(r.text)
    typ = 'personalLoan'
    

    driver.get('https://www.bayfed.com/products-services/rates/loan-rates')

    # Wait for the dynamic content to load
    driver.implicitly_wait(20)

    # Open the web page
    
    driver.save_screenshot('k.png')
    # Find the table element
    table = driver.find_element_by_xpath('//*[@id="PageContent"]/div[10]/div[3]/table')
    
    # Find the rows of the table
    rows = table.find_elements_by_tag_name("tr")

    # Skip the first row (header)
    for row in rows[1:]:
        # Find the columns of the row
        cols = row.find_elements_by_tag_name("td")
        
        # Extract the rate, amount, and period in years
        rate = float(cols[2].text[:-1])
        amount = int(cols[1].text[1:].replace(",", "").replace("$","").strip())
 
        
        # Update the minimum and maximum values
        if not "min_rate" in locals() or rate < min_rate:
            min_rate = rate
        if not "max_rate" in locals() or rate > max_rate:
            max_rate = rate
        if not "max_amount" in locals() or amount > max_amount:
            max_amount = amount


    # Close the webdriver
    

    # Print the results
    # print("Minimum rate:", min_rate)
    # print("Maximum rate:", max_rate)
   
    # print("Maximum amount:", max_amount)

    info = { "type": typ, "urlLink": url,"minPeriod": '', "maxPeriod": 5, "rateFrom": min_rate, "rateTo":max_rate, "maxAmount": max_amount}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'personalLoan', "itemType":[info]}}
    return dic

def get_student_loan():
   pass
def get_mortgages_2(url, bankName, bankUrl, bankID,driver):
    driver.get("https://www.bayfed.com/products-services/rates/mortgage-rates")
    typ = 'mortgageLoan'

    #     # find the table with the desired title
    table_title = driver.find_element_by_xpath("//div[@class='ratetabletitle'][contains(text(), 'Conforming - Fixed Rate')]/following-sibling::div[@class='table-container']/table")

    # get all the rows except the header
    table_rows = table_title.find_elements_by_xpath(".//tr[position()>1]")

    # initialize the min and max values
    min_year = float('inf')
    max_year = float('-inf')
    min_rate = float('inf')
    max_rate = float('-inf')
    min_apr = float('inf')
    max_apr = float('-inf')

    # loop through the rows and update the min and max values
    for row in table_rows:
        # extract the values from the row
        year = int(row.find_element_by_xpath(".//td[1]").text.split()[0])
        rate = float(row.find_element_by_xpath(".//td[2]").text.strip('%'))
        apr = float(row.find_element_by_xpath(".//td[4]").text.strip('%'))

        # update the min and max values
        if year < min_year:
            min_year = year
        if year > max_year:
            max_year = year
        if rate < min_rate:
            min_rate = rate
        if rate > max_rate:
            max_rate = rate
        if apr < min_apr:
            min_apr = apr
        if apr > max_apr:
            max_apr = apr


    info1 = { "type": "purchase", "urlLink": url,"minPeriod": min_year, "maxPeriod":  max_year, "aprFrom": min_apr, "aprTo": max_apr,"rateFrom": min_rate, "rateTo": max_rate, "maxAmount": "","variableAPR":False, "fixedAPR": True}
    print(info1)
    time.sleep(2)
    table_title = driver.find_element_by_xpath("//div[@class='ratetabletitle'][contains(text(), 'Conforming - Adjustable Rate')]/following-sibling::div[@class='table-container']/table")

    # get all the rows except the header
    table_rows = table_title.find_elements_by_xpath(".//tr[position()>1]")

    # initialize the min and max values
    min_year = float('inf')
    max_year = float('-inf')
    min_rate = float('inf')
    max_rate = float('-inf')
    min_apr = float('inf')
    max_apr = float('-inf')

    # loop through the rows and update the min and max values
    for row in table_rows:
        # extract the values from the row
        # year = (row.find_element_by_xpath(".//td[1]").text.split()[0])
        rate_element = row.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ratetable-container", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "col-1", " " ))]')
        if rate_element.text:
            rate = float(rate_element.text.strip('%'))
            if rate < min_rate:
                min_rate = rate
            if rate > max_rate:
                max_rate = rate
        
        apr_element = row.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ratetable-container", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "col-3", " " ))]')
        if apr_element.text:
            apr = float(apr_element.text.strip('%'))
            if apr < min_apr:
                min_apr = apr
            if apr > max_apr:
                max_apr = apr

    info2 = { "type": "purchase", "urlLink": url,"minPeriod":'5/5', "maxPeriod":'10/6', "aprFrom": min_apr, "aprTo": max_apr,"rateFrom": min_rate, "rateTo": max_rate, "maxAmount": "","variableAPR":True, "fixedAPR": False}
    print(info2)
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": typ, "itemType":[info1,info2]}}
    # json_str = json.dumps(dic)
    return dic


def get_heloc():
   pass



def parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url, student_loan_url):
    
    bankName = 'Bay Federal Credit Union'
    bankUrl = 'https://www.bayfed.com/products-services/rates'
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
    driver = webdriver.Chrome(executable_path=f"E:\\Bank project\\ncsecu\\chrome\\chromedriver.exe", options=options)

    try:
      itemType1 = get_auto_loan(auto_loan_url, bankName, bankUrl, bankID,driver)
    except :
      itemType1 = {}
        
    try:
      itemType2 =get_personal_loan(personal_loan_url, bankName, bankUrl, bankID,driver)
    except:
      itemType2 = {}
    try:
        itemType3 = get_student_loan(student_loan_url, bankName, bankUrl, bankID,driver)
    except:
      itemType3 = {}
        
    try:
      itemType4 = get_mortgages_2(mortgage_loan_url, bankName, bankUrl, bankID,driver)
    except :
      itemType4 = {}
     
    try:
      itemType5 = get_heloc(heloc, bankName, bankUrl, bankID,driver)
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
   
    auto_loan_url = 'https://www.bayfed.com/products-services/rates/loan-rates'
    mortgage_loan_url = 'https://www.bayfed.com/products-services/rates/mortgage-rates'
    personal_loan_url = 'https://www.bayfed.com/products-services/rates/loan-rates'
    student_loan_url = "https://www.salliemae.com/landing/student-loans/?__hstc=236286046.7c672951a96099eb0e61adb73b2aefb2.1677262052961.1677334423704.1677338582694.5&__hssc=236286046.1.1677338582694&__hsfp=1483251232&submissionGuid=d003d643-b105-4e8e-ac5f-b9c68124fe65&MPID=3000000007&dtd_cell=SMLRSOPACUCURCOTAAM0847N010000"
    heloc='https://www.americanheritagecu.org/rates#homeEquity'
    output = parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url, student_loan_url)
    print(output)
    returnstr = "[" + ','.join(map(str, output))
    returnstr = returnstr + "]"
    return returnstr
fetch_data()