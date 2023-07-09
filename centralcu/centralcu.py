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
def data_validation(dataDictList):
    url = "https://us-central1-lendmesh.cloudfunctions.net/data-validation"

    payload = json.dumps(dataDictList)
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

def get_personal_loan(url,  bankName, bankUrl, bankID):
    r  = get('https://www.centralcu.org/cu-info/rates/loan-rates/#l1')
    soup = bs(r.text,'html.parser')
    # print(soup)
    typ = 'personalLoan'
   

    tables = soup.find_all('table', class_='rates')

    table = tables[0]  # Get the second table

    rows = table.find_all('tr')
    for row in rows[3:4]:  # Skip the header row
        columns = row.find_all('td')
        loan_type = columns[0].text.strip()
        term = columns[1].text.strip()
        apr = columns[2].text.strip().replace("%","")
        if term=="n/a":
            min_term=1
            max_term=5
        pattern = r'\d+.\d'
   
    matches = re.findall(pattern, apr)
    
    if matches:
        rate = float(matches[0])
    

    info = { "type": typ, "urlLink": url,"minPeriod": int(min_term), "maxPeriod": max_term, "rateFrom": rate, "rateTo": '', "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'personalLoan', "itemType":[info]}}

    # json_str = json.dumps(dic)
    return dic


def get_auto_loan(url,  bankName, bankUrl, bankID):

    r  = get('https://www.centralcu.org/cu-info/rates/loan-rates/#l4')
    soup = bs(r.text,'html.parser')
    # print(soup)
    typ = 'mortgageLoan'
    min_term = float('inf')
    max_term = float('-inf')
    min_apr = float('inf')
    max_apr = float('-inf')

    tables = soup.find_all('table', class_='rates')

    table = tables[5]  

    rows = table.find_all('tr')
    for row in rows[1:6]:  # Skip the header row
        columns = row.find_all('td')
        
        term = columns[1].text.replace("Months",'').replace("(New purchases only)",'')
        
        apr = columns[2].text.strip().replace("%","")
        # print(term,apr)
        if term=="n/a":
            term=''
        else:
            term=int(term)/12
        pattern = r'\d+.\d+\d'
   
        matches = re.findall(pattern, apr)
        
        if matches:
            apr = float(matches[0])
        if term < min_term:
            min_term = term
        if term > max_term:
            max_term = term
        if apr < min_apr:
            min_apr = apr
        if apr > max_apr:
            max_apr = apr
    
    
    #used
    umin_term = float('inf')
    umax_term = float('-inf')
    umin_apr = float('inf')
    umax_apr = float('-inf')
    tables = soup.find_all('table', class_='rates')

    table = tables[5]  
    rows = table.find_all('tr')
    for row in rows[7:]:  # Skip the header row
        columns = row.find_all('td')
        
        term = columns[1].text.replace("Months",'')
        
        apr = columns[2].text.strip().replace("%","")
        # print(term,apr)
        if term=="n/a":
            term=''
        else:
            term=int(term)/12
        pattern = r'\d+.\d+\d'

        matches = re.findall(pattern, apr)
        
        if matches:
            apr = float(matches[0])
        if term < umin_term:
            umin_term = term
        if term > umax_term:
            umax_term = term
        if apr < umin_apr:
            umin_apr = apr
        if apr > umax_apr:
            umax_apr = apr

#print(umin_term,umax_term,umin_apr,umax_apr)
    info1 = { "type": "new", "urlLink": url,"minPeriod": int(min_term), "maxPeriod":  int(max_term),"rateFrom": min_apr, "rateTo": max_apr, "maxAmount": ""}
    info2 = { "type": "used", "urlLink": url,"minPeriod": int(umin_term), "maxPeriod":  int(umax_term),"rateFrom": umin_apr, "rateTo": umax_apr, "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1,info2]}}
    json_str = json.dumps(dic)
    # print(json_str)
    return dic
   


def get_home_Equity():
   
    r  = get('https://www.centralcu.org/cu-info/rates/loan-rates/')
    soup = bs(r.text,'html.parser')
    # print(soup)
    
   
    min_term = float('inf')
    max_term = float('-inf')
    min_rate = float('inf')
    max_rate = float('-inf')
    
    tables = soup.find_all('table', class_='rates')

    table = tables[1]  # Get the second table

    rows = table.find_all('tr')
    for row in rows[1:]:  # Skip the header row
        columns = row.find_all('td')
        loan_type = columns[0].text.strip()
        term = columns[1].text.strip().replace('months','')
        apr = columns[2].text.strip().replace("%","")
        term=int(term)/12
        pattern = r'\d+'
   
        rate=float(apr.replace('As low as','').strip('%'))
        
        if term < min_term:
            min_term = term
        if term > max_term:
            max_term = term
        if rate < min_rate:
            min_rate = rate
        if rate > max_rate:
            max_rate = rate
    # print(min_term,max_term)
    # print(min_rate,max_rate)
    info1 = {"type": "homeEquity",  "urlLink": "https://www.centralcu.org/cu-info/rates/loan-rates/#l2",  "minPeriod":min_term,  "maxPeriod": max_term,  "rateFrom": min_rate,  "rateTo": max_rate,  "maxAmount": "",  "ltvFrom": '80',  "ltvTo": "",  "description": "Up to 80%",  "default": True  }
    
    return [info1]

def get_heloc(url,  bankName, bankUrl, bankID):
    # print('heloc')
    #__________________________default_values
    loanType = "helocLoan"
    type1 = 'helocLoan'
    description = ' '
    r  = get('https://www.centralcu.org/cu-info/rates/loan-rates/#l2')
    soup = bs(r.text,'html.parser')
    # print(soup)
    
   
    min_rate = float('inf')
    max_rate = float('-inf')
  
    tables = soup.find_all('table', class_='rates')

    table = tables[2]  # Get the second table

    rows = table.find_all('tr')
    for row in rows[2:]:  # Skip the header row
        columns = row.find_all('td')
        loan_type = columns[0].text.strip()
        term = columns[1].text.strip()
        rate = columns[2].text.strip().replace("%","")
        
        if term=='n/a':
            min_term=1
            max_term=5
        else:
            term=int(term)/12
        pattern = r'.\d+\d'
        matches = re.findall(pattern, rate)
        if matches:
            rate = float(matches[0])
        else:
            rate=''
       
        # print(rate,term)
    
        if rate < min_rate:
            min_rate = rate
        if rate > max_rate:
            max_rate = rate
    # print(min_term,max_term)
    print('csdacsd',min_rate,max_rate) 
    itemType = []
    info = {"type": type1,
            "urlLink": "https://www.centralcu.org/cu-info/rates/loan-rates/#l2",
            "minPeriod":min_term,
            "maxPeriod":max_term ,
            "rateFrom": min_rate+8.0,
            "rateTo": max_rate+8.0,
            "maxAmount": 99000,
            "ltvFrom": description.replace("Up to ","").replace("%",""),
            "ltvTo": 80,
            "description": description,
            "default": True
            }

    itemType.append(info)
    itemType = itemType+get_home_Equity()
    dic = {"bankName": bankName, "bankID": bankID, "date": time.strftime("%m-%d-%Y"),
           "timestamp": time.strftime("%m-%d-%Y %H:%M:%S"), "bankUrl": bankUrl,
           "bankDetails": {"loanType": loanType, "itemType": itemType}}

    return dic
    

def get_mortgages_2(url,  bankName, bankUrl, bankID):

    # print('mortgages')
    r  = get('https://www.centralcu.org/cu-info/rates/loan-rates/#l3')
    soup = bs(r.text,'html.parser')
    # print(soup)
    typ = 'mortgageLoan'
    min_term = float('inf')
    max_term = float('-inf')
    min_apr = float('inf')
    max_apr = float('-inf')
    min_rate = float('inf')
    max_rate = float('-inf')

    tables = soup.find_all('table', class_='rates')

    table = tables[4]  

    rows = table.find_all('tr')
    for row in rows[1:]:  # Skip the header row
        columns = row.find_all('td')
        
        term = columns[0].text.replace("months",'')
        apr = columns[1].text.strip().replace("%","")
       
        if term=="n/a":
            term=''
        else:
            term=int(term)/12
        pattern = r'\d+.\d+\d'
        pattern2 = r'\d+.\d'
   
        matches = re.findall(pattern, apr)
        print(matches)
        # matches1 = re.findall(pattern, rate)
        if matches:
            rate = float(matches[0])
            print(rate)
        if matches:
            apr = float(matches[1])
            print(apr)
    
        if term < min_term:
            min_term = term
        if term > max_term:
            max_term = term
        if apr < min_apr:
            min_apr = apr
        if apr > max_apr:
            max_apr = apr
        if rate < min_rate:
            min_rate = rate
            # print(min_rate)
        if rate > max_rate:
            max_rate = rate
            # print(max_rate)
    
    
    # info1 = { "type": "purchase", "urlLink": url,"minPeriod": min_term, "maxPeriod":  max_term, "aprFrom": min_apr, "aprTo":max_apr,"rateFrom": '', "rateTo": '', "maxAmount": "","variableAPR":True, "fixedAPR": False}
    info2 = { "type": "purchase", "urlLink": url,"minPeriod": min_term, "maxPeriod":  max_term, "aprFrom": min_apr, "aprTo":max_apr,"rateFrom":min_rate, "rateTo": max_rate, "maxAmount": "","variableAPR":False, "fixedAPR": True}
    
    
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": typ, "itemType":[info2]}}
    # json_str = json.dumps(dic)
    return dic

def parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url):
    
    bankName = 'centralcu'
    bankUrl = 'https://www.centralcu.org/cu-info/rates'
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
      itemType3 = get_mortgages_2(mortgage_loan_url, bankName, bankUrl, bankID)
    except:
      itemType3 = {}
    try:
      itemType4 = get_heloc(heloc, bankName, bankUrl, bankID)
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

def fetch_data ():
   
    auto_loan_url = 'https://www.centralcu.org/cu-info/rates/loan-rates/#l4'
    mortgage_loan_url = 'https://www.centralcu.org/cu-info/rates/loan-rates/#l3'
    personal_loan_url = 'https://www.centralcu.org/cu-info/rates/loan-rates/#l1'
    heloc='https://www.centralcu.org/cu-info/rates/loan-rates/#l2'
    output = parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url)
    print(output)
    returnstr = "[" + ','.join(map(str, output))
    returnstr = returnstr + "]"
    return returnstr
    
fetch_data()