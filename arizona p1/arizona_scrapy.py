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
    r  = get(url)
    soup = bs(r.content,'html.parser')
     
    typ = 'personalLoan'
    itemType = []

    url = "https://www.arizonafinancial.org/personal-loans"
    # Find the element using XPath
    element = soup.find_all('div', {'class': 'row-content'})
    data=[]
    for i in element:
        a=i.text
        data.append(a)

    # print(data)
    minperiod=int(int(data[0].split( )[0])/12)
    maxperiod=int(int(data[6].split( )[0])/12)
    fromrate=(data[1].split('%')[0])
    torate=(data[7].split('%')[0])
    # fromrate=(data[1][0])
    # torate=(data[7][0])


    info = { "type": typ, "urlLink": "https://www.arizonafinancial.org/personal-loans","minPeriod": minperiod, "maxPeriod": maxperiod, "rateFrom": eval(fromrate), "rateTo": eval(torate), "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'personalLoan', "itemType":[info]}}

    json_str = json.dumps(dic)
    return dic
    # print(json_str) 

# get_personal_loan()



def get_student_loan(url,  bankName, bankUrl, bankID):
    r  = get(url)
    soup = bs(r.content,'html.parser')
    
     
    typ = 'stundetLoan'
    itemType = []

    variable_rates_text = ''
    for p in soup.find_all('p'):
        if p.find('b', text=re.compile('^Variable rates:')):
            variable_rates_text = p.find('b', text=re.compile('^Variable rates:')).next_sibling.strip()
            print(variable_rates_text)
            fixed_rates_text = p.find('b', text=re.compile('^Fixed rates:')).next_sibling.strip()
            
            break
    variable_rates_text = variable_rates_text.replace('\xa0', ' ')
    variable_rates_text = variable_rates_text.replace('APR', '')
    variable_rates = variable_rates_text.split(' – ')
    
    variable_rates = variable_rates[0].split(' ')
    # print(variable_rates)
    var_min=variable_rates[0].replace('%','')
    var_max=variable_rates[2].replace('%','')
  

    fixed_rates_text = fixed_rates_text.replace('APR', '')
    fixed_rates = fixed_rates_text.split('–')
    fixed_rates_min = fixed_rates[0].replace('%','')
    fixed_rates_max = fixed_rates[1].replace('%','')
    # fixed_rates_min = fixed_rates[0][0]
    # fixed_rates_max = fixed_rates[1][0]
    # print(fixed_rates_min,fixed_rates_max)
    
    
    element_text = soup.select_one('#container-7380159c33 div p:nth-of-type(3) span').text
    period = re.search(r'\d+-\d+', element_text).group().split('-')
    # print(period[0],period[1])

    info1 = { "type": "newLoan", "urlLink": "https://www.salliemae.com/landing/student-loans/?__hstc=236286046.7c672951a96099eb0e61adb73b2aefb2.1677262052961.1677334423704.1677338582694.5&__hssc=236286046.1.1677338582694&__hsfp=1483251232&submissionGuid=d003d643-b105-4e8e-ac5f-b9c68124fe65&MPID=3000000007&dtd_cell=SMLRSOPACUCURCOTAAM0847N010000","minPeriod": eval(period[0]), "maxPeriod":  eval(period[1]), "rateFrom": eval(fixed_rates_min), "rateTo": eval(fixed_rates_max), "maxAmount": "", "variableAPR":False, "fixedAPR": True}
    info2 = { "type": "newLoan", "urlLink": "https://www.salliemae.com/landing/student-loans/?__hstc=236286046.7c672951a96099eb0e61adb73b2aefb2.1677262052961.1677334423704.1677338582694.5&__hssc=236286046.1.1677338582694&__hsfp=1483251232&submissionGuid=d003d643-b105-4e8e-ac5f-b9c68124fe65&MPID=3000000007&dtd_cell=SMLRSOPACUCURCOTAAM0847N010000","minPeriod": eval(period[0]), "maxPeriod":  eval(period[1]), "rateFrom": eval(var_min), "rateTo": eval(var_max), "maxAmount": "", "variableAPR":True, "fixedAPR": False}
    
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'studentLoan', "itemType":[info1,info2]}}
    json_str = json.dumps(dic)
    # print(json_str)
    return dic
# get_student_loan()


def get_auto_loan(url,  bankName, bankUrl, bankID):
  
     
    r  = get(url)
    soup = bs(r.content,'html.parser')
    
    typ = None
    itemType = []
    
    element = soup.find_all('div', {'class': 'row-content'})
    data=[]
    for i in element:
        a=i.text
        data.append(a)

    
    minperiod=int(int(data[0].split( )[0])/12)
    maxperiod=int(int(data[6].split( )[0])/12)
    fromrate=(data[1].split('%')[0])
    torate=(data[7].split('%')[0])    
    # fromrate=(data[1])
    # torate=(data[7])

    info1 = { "type": "new", "urlLink": "https://www.arizonafinancial.org/auto-loan","minPeriod": (minperiod), "maxPeriod":  (maxperiod),"rateFrom": eval(fromrate), "rateTo": eval(torate), "maxAmount": ""}
    info2 = { "type": "used", "urlLink": "https://www.arizonafinancial.org/auto-loan","minPeriod": (minperiod), "maxPeriod":  (maxperiod),"rateFrom": eval(fromrate), "rateTo": eval(torate), "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1,info2]}}
    json_str = json.dumps(dic)
    # print(json_str)
    return dic
# get_auto_loan()

def get_home_Equity():
    
    url='https://www.arizonafinancial.org/home-equity-loan'
    r  = get(url)
    soup = bs(r.content,'html.parser')

    element = soup.find_all('div', {'class': 'row-content'})
    data=[]
    for i in element:
        a=i.text
        data.append(a)

    # print(data)
    minperiod=int(int(data[0].split( )[0])/12)
    maxperiod=int(int(data[12].split( )[0])/12)
    fromrate=(data[1].split('%')[0])
    torate=(data[13].split('%')[0]) 
    # fromrate=(data[1])
    # torate=(data[13])    

    info1 = {"type": "homeEquity",  "urlLink": "https://www.arizonafinancial.org/home-equity-loan",  "minPeriod":(minperiod),  "maxPeriod": (maxperiod),  "rateFrom":eval(fromrate),  "rateTo":eval(torate),  "maxAmount": "",  "ltvFrom": '80',  "ltvTo": "",  "description": "Up to 80%",  "default": True  }    # info2 = { "type": "used", "urlLink": "https://www.arizonafinancial.org/auto-loan","minPeriod": minperiod, "maxPeriod":  maxperiod,"rateFrom": fromrate, "rateTo": torate, "maxAmount": ""}
    return [info1]
    # print(info1)





def get_heloc(url,  bankName, bankUrl, bankID):

    bankName = 'arizonafinancial'
    bankUrl = 'https://www.arizonafinancial.org/'
    bankID = ''
  
    # url='https://www.arizonafinancial.org/home-equity-line-of-credit-heloc'
    r  = get(url)
    soup = bs(r.content,'html.parser')
    type1 = 'helocLoan'
    loanType = "helocLoan"
    element = soup.find_all('div', {'class': 'row-content'})
    data=[]
    for i in element:
        a=i.text
        data.append(a)

    years = re.findall(r'\d+(?= year)', data[0])

    if len(years) == 2:
        year1, year2 = years
        
    else:
        print("Could not find two year values")
    min_period=year1
    max_period=year2
    itemType=[]
    description = 'Up to 80%'
    rate_from=(data[1].split('%')[0])
    # rate_from=(data[1])
    info = {"type": type1,
            "urlLink": "https://www.arizonafinancial.org/home-equity-line-of-credit-heloc",
            "minPeriod": eval(min_period),
            "maxPeriod": eval(max_period),
            "rateFrom": eval(rate_from),
            "rateTo": "",
            "maxAmount": "",
            "ltvFrom": description.replace("Up to ","").replace("%",""),
            "ltvTo": "",
            "description": description,
            "default": True
            }

    itemType.append(info)
    itemType = itemType+get_home_Equity()
    dic = {"bankName": bankName, "bankID": bankID, "date": time.strftime("%m-%d-%Y"),
           "timestamp": time.strftime("%m-%d-%Y %H:%M:%S"), "bankUrl": bankUrl,
           "bankDetails": {"loanType": loanType, "itemType": itemType}}
    return dic
  


def parse(heloc_url, auto_loan_url, personal_loan_url, student_loan_url):
    
    bankName = 'arizonafinancial'
    bankUrl = 'https://www.arizonafinancial.org/'
    bankID = ''

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
      itemType4 = get_heloc(heloc_url, bankName, bankUrl, bankID)
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
    heloc_url = 'https://www.arizonafinancial.org/home-equity-line-of-credit-heloc'
    auto_loan_url = "https://www.arizonafinancial.org/auto-loan" 
    # mortgage_loan_url = "https://www.dcu.org/about/rates.html#:~:text=of%20the%20loan.-,Mortgage%20Loans,-Purchase%20Fixed%2DRate"
    personal_loan_url = "https://www.arizonafinancial.org/personal-loans"
    student_loan_url = "https://www.salliemae.com/landing/student-loans/?__hstc=236286046.7c672951a96099eb0e61adb73b2aefb2.1677262052961.1677334423704.1677338582694.5&__hssc=236286046.1.1677338582694&__hsfp=1483251232&submissionGuid=d003d643-b105-4e8e-ac5f-b9c68124fe65&MPID=3000000007&dtd_cell=SMLRSOPACUCURCOTAAM0847N010000"
    home_Equity_url='https://www.arizonafinancial.org/home-equity-loan'
    output = parse(heloc_url, auto_loan_url, personal_loan_url, student_loan_url)
    print(output)
    returnstr = "[" + ','.join(map(str, output))
    returnstr = returnstr + "]"
    return returnstr
    
fetch_data()