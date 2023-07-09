from selenium import webdriver
from selenium.webdriver.edge.service import Service
import csv,io
import requests
import json
import pprint
import re
import time
from google.cloud import firestore
from bs4 import BeautifulSoup as bs  
bankName = 'andrewsfcu'
bankUrl = 'https://www.andrewsfcu.org/'
bankID = 787994
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import re
import json
import requests
import time

user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument("--start-maximized")
options.add_argument(f'user-agent={user_agent}')

capabilities = {
    "browserName": "chrome",
    "version": "98.0",
    "enableVNC": True,
    "enableVideo": False
}

def data_validation(dataDictList):
    url = "https://us-central1-lendmesh.cloudfunctions.net/data-validation"

    payload = json.dumps(dataDictList)
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)



#service = Service(verbose = True)
#driver = webdriver.Edge(service = service)

def mortgage_loan(hostName,url):
    driver = webdriver.Remote(command_executor="http://"+ hostName +":4444/wd/hub", desired_capabilities=capabilities, options=options)
    driver.get("https://www.andrewsfcu.org/Learn/Resources/Rates/Mortgage-Rates")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[id='Table_1575']")))
    soup = bs(driver.page_source,'html.parser')
    table1 = soup.find('table',{'id':'Table_1575'}).find('tbody')
    table2 = soup.find('table',{'id':'Table_1577'}).find('tbody')
    rates1 = []
    aprs1 =[]
    terms1 = []
    rates2 = []
    aprs2 =[]
    terms2 = []
    for i in table1.findAll('tr'):
        i = i.findAll('td')
        term = int(re.findall(r'\d+',i[0].text)[0])
        rate = float(re.findall(r'\d+\.\d+',i[1].text)[0])
        apr = float(re.findall(r'\d+\.\d+',i[2].text)[0])
        rates1.append(rate)
        aprs1.append(apr)
        terms1.append(term)
    for i in table2.findAll('tr'):
        i = i.findAll('td')
        term = int(re.findall(r'\d+',i[0].text)[0])
        rate = float(re.findall(r'\d+\.\d+',i[1].text)[0])
        apr = float(re.findall(r'\d+\.\d+',i[2].text)[0])
        rates2.append(rate)
        aprs2.append(apr)
        terms2.append(term)
    info1 = {"type": 'purchase',"urlLink": url,"minPeriod": min(terms1),"maxPeriod":  max(terms1),"aprFrom": min(aprs1),"aprTo": max(aprs1),"rateFrom": min(rates1),"rateTo": max(rates1),"maxAmount": "","variableAPR": False,"fixedAPR": True}
    info2 = {"type": 'purchase',"urlLink": url,"minPeriod": min(terms2),"maxPeriod":  max(terms2),"aprFrom": min(aprs2),"aprTo": max(aprs2),"rateFrom": min(rates2),"rateTo": max(rates2),"maxAmount": "","variableAPR": True,"fixedAPR": False}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'mortgageLoan', "itemType":[info1]}}
    print(dic)
    return dic



def auto_loan(hostName,url):
    driver = webdriver.Remote(command_executor="http://"+ hostName +":4444/wd/hub", desired_capabilities=capabilities, options=options)
    driver.get('https://www.andrewsfcu.org/Learn/Resources/Rates/New-and-Used-Auto-Loan-Rates')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[id='Table_1416']")))
    soup = bs(driver.page_source,'html.parser')
    table1 = soup.find('table',{'id':'Table_1416'}).find('tbody')
    table2 = soup.find('table',{'id':'Table_1471'}).find('tbody')
    rates1 = []
    aprs1 =[]
    terms1 = []
    rates2 = []
    aprs2 =[]
    terms2 = []
    for i in table1.findAll('tr'):
        i = i.findAll('td')
        term = int(re.findall(r'\d+',i[0].text)[0])
        rate = float(re.findall(r'\d+\.\d+',i[1].text)[0])
        apr = float(re.findall(r'\d+\.\d+',i[2].text)[0])
        rates1.append(rate)
        aprs1.append(apr)
        terms1.append(term)
    for i in table2.findAll('tr'):
        i = i.findAll('td')
        term = int(re.findall(r'\d+',i[0].text)[0])
        rate = float(re.findall(r'\d+\.\d+',i[1].text)[0])
        apr = float(re.findall(r'\d+\.\d+',i[2].text)[0])
        rates2.append(rate)
        aprs2.append(apr)
        terms2.append(term)
    info1 = {"type": 'new',"urlLink": url,"minPeriod": min(terms1)/12,"maxPeriod":  max(terms1)/12,"rateFrom": min(rates1),"rateTo": max(rates1),"maxAmount": "","variableAPR": False,"fixedAPR":True}
    info2 = {"type": 'used',"urlLink": url,"minPeriod": min(terms2)/12,"maxPeriod":  max(terms2)/12,"rateFrom": min(rates2),"rateTo": max(rates2),"maxAmount": "","variableAPR": False,"fixedAPR": True}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1,info2]}}
    print(dic)
    return dic


def personal_loan(hostName,url):
    driver = webdriver.Remote(command_executor="http://"+ hostName +":4444/wd/hub", desired_capabilities=capabilities, options=options)
    driver.get('https://www.andrewsfcu.org/Learn/Resources/Rates/Personal-Loan-Rates')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[id='Table_1629']")))
    soup = bs(driver.page_source,'html.parser')
    table1 = soup.find('table',{'id':'Table_1629'}).find('tbody')
    rates1 = []
    aprs1 =[]
    terms1 = []
    for i in table1.findAll('tr'):
        i = i.findAll('td')
        term = int(re.findall(r'\d+',i[0].text)[0])
        rate = float(re.findall(r'\d+\.\d+',i[1].text)[0])
        apr = float(re.findall(r'\d+\.\d+',i[2].text)[0])
        rates1.append(rate)
        aprs1.append(apr)
        terms1.append(term)
   
    info1 = {"type": 'personalLoan',"urlLink": url,"minPeriod": min(terms1)/12,"maxPeriod":  max(terms1)/12,"rateFrom": min(rates1),"rateTo": max(rates1),"maxAmount": "","variableAPR": False,"fixedAPR":True}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'personalLoan', "itemType":[info1]}}
    print(dic)
    return dic


def get_heloc(hostName,url):
    driver = webdriver.Remote(command_executor="http://"+ hostName +":4444/wd/hub", desired_capabilities=capabilities, options=options)
    
    driver.get('https://www.andrewsfcu.org/Learn/Resources/Rates/Home-Equity-Loans-and-Lines-Rates')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class='page-rich-text-content ']")))
    soup = bs(driver.page_source,'html.parser')
    div = soup.find('div',{'class':'page-rich-text-content'})
    paras = div.findAll('p')
    homeequity = [i for i in paras if "home equity loan rate" in i.text][0]
    heloc = [i for i in paras if "Home Equity Line of Credit rate" in i.text][0]
    helocrate = re.findall(r'\d+\.\d+\%\sAPR',heloc.text)[0]
    helocrate = float(re.findall(r'\d+\.\d+',helocrate)[0])
    homerate = re.findall(r'\d+\.\d+\%\sAPR',homeequity.text)[0]
    homerate = float(re.findall(r'\d+\.\d+',homerate)[0])
    info1 = {"type": "homeEquity","urlLink": url,"minPeriod": 5,"maxPeriod": 20,"rateFrom": homerate,"rateTo": "","maxAmount": '',"ltvFrom": 80,"ltvTo": '',"description": "Up to 80", "default": True}
    info2 = {"type": "helocLoan","urlLink": url,"minPeriod": 5,"maxPeriod": 20,"rateFrom": helocrate,"rateTo": "","maxAmount": '',"ltvFrom": 80,"ltvTo": '',"description": "Up to 80", "default": True}
    dic = {"bankName": bankName, "bankID": bankID, "date": time.strftime("%m-%d-%Y"),
           "timestamp": time.strftime("%m-%d-%Y %H:%M:%S"), "bankUrl": bankUrl,
           "bankDetails": {"loanType": "helocLoan", "itemType": [info1,info2]}}
    print(dic)
    return dic


def parse(heloc_url, auto_loan_url, personal_loan_url, mortgage_loan_url, hostName):
    
    bankName = 'andrewsfcu'
    bankUrl = 'https://www.andrewsfcu.org/'
    bankID = 787994

    itemType1 = auto_loan(hostName,auto_loan_url)
    itemType2 = personal_loan(hostName,personal_loan_url)
    #itemType3 = get_student_loan(student_loan_url, bankName, bankUrl, bankID)
    itemType4 = mortgage_loan(hostName,mortgage_loan_url)
    itemType5 = get_heloc(hostName,heloc_url)

    dic = [itemType1, itemType2, itemType4, itemType5] 
    print(dic)
    validatedDictList = data_validation(dic)
    print("validatedDictList")
    print(validatedDictList)
    # db = firestore.Client(project='lendmesh')
    # for validatedDict in validatedDictList:
    #     displayValue = validatedDict['display']
    #     print("displayValue")
    #     print(displayValue)
    #     if str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="personalLoan":
    #         if displayValue == True:
    #             doc_per = db.collection(u'webscrapy_stage').document(u'personalloan').collection(u'bankrates').document(bankName)
    #             doc_per.set(validatedDict, merge=True)
    #             doc_per = db.collection(u'webscrapy_stage_history').document(u'personalloan').collection(bankName)
    #             doc_per.add(validatedDict)
    #         elif displayValue == False:
    #             print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - PersonalLoan')
    #             print("Inside loop")
    #             print(validatedDict)
    #             validatedDict = { "display": False }
    #             doc_per = db.collection(u'webscrapy_stage').document(u'personalloan').collection(u'bankrates').document(bankName)
    #             doc_per.set(validatedDict, merge=True)

    #     elif str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="autoLoan":
    #         if displayValue == True:
    #             doc_auto = db.collection(u'webscrapy_stage').document(u'autoloan').collection(u'bankrates').document(bankName)
    #             doc_auto.set(validatedDict, merge=True)
    #             doc_auto = db.collection(u'webscrapy_stage_history').document(u'autoloan').collection(bankName)
    #             doc_auto.add(validatedDict)
    #         elif displayValue == False:
    #             print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - AutoLoan')
    #             print("Inside loop")
    #             print(validatedDict)
    #             validatedDict = { "display": False }
    #             doc_auto = db.collection(u'webscrapy_stage').document(u'autoloan').collection(u'bankrates').document(bankName)
    #             doc_auto.set(validatedDict, merge=True)

    #     elif str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="helocLoan":
    #         if displayValue == True:
    #             doc_heloc = db.collection(u'webscrapy_stage').document(u'helocloan').collection(u'bankrates').document(bankName)
    #             doc_heloc.set(validatedDict, merge=True)
    #             doc_heloc = db.collection(u'webscrapy_stage_history').document(u'helocloan').collection(bankName)
    #             doc_heloc.add(validatedDict)
    #         elif displayValue == False:
    #             print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - HelcoLoan')
    #             print("Inside loop")
    #             print(validatedDict)
    #             validatedDict = { "display": False }
    #             doc_heloc = db.collection(u'webscrapy_stage').document(u'helocloan').collection(u'bankrates').document(bankName)
    #             doc_heloc.set(validatedDict, merge=True)

    #     elif str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="mortgageLoan":
    #         if displayValue == True:
    #             doc_mortgage = db.collection(u'webscrapy_stage').document(u'mortgageloan').collection(u'bankrates').document(bankName)
    #             doc_mortgage.set(validatedDict, merge=True)
    #             print(validatedDict)
    #             doc_mortgage = db.collection(u'webscrapy_stage_history').document(u'mortgageloan').collection(bankName)
    #             doc_mortgage.add(validatedDict)
    #         elif displayValue == False:
    #             print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - MortgageLoan')
    #             print("Inside loop")
    #             print(validatedDict)
    #             validatedDict = { "display": False }
    #             doc_mortgage = db.collection(u'webscrapy_stage').document(u'mortgageloan').collection(u'bankrates').document(bankName)
    #             doc_mortgage.set(validatedDict, merge=True)
    #     elif str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="studentLoan":
    #         if displayValue == True:
    #             doc_studentloan = db.collection(u'webscrapy_stage').document(u'studentloan').collection(u'bankrates').document(bankName)
    #             doc_studentloan.set(validatedDict, merge=True)
    #             print(validatedDict)
    #             doc_studentloan = db.collection(u'webscrapy_stage_history').document(u'studentloan').collection(bankName)
    #             doc_studentloan.add(validatedDict)
    #         elif displayValue == False:
    #             print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - StudentLoan')
    #             print("Inside loop")
    #             print(validatedDict)
    #             validatedDict = { "display": False }
    #             doc_studentloan = db.collection(u'webscrapy_stage').document(u'studentloan').collection(u'bankrates').document(bankName)
    #             doc_studentloan.set(validatedDict, merge=True)   

    # f = open("affinityplus.json", "w", encoding='utf-8')
    # tmp = json.dumps(validatedDictList, indent=4)
    # f.write(tmp)
    # f.close()
    return validatedDictList



def fetch_data(request):
    auto_loan_url = "https://www.andrewsfcu.org/Learn/Resources/Rates/New-and-Used-Auto-Loan-Rates" 
    personal_loan_url = "https://www.andrewsfcu.org/Learn/Resources/Rates/Personal-Loan-Rates"
    mortgage_loan_url = "https://www.andrewsfcu.org/Learn/Resources/Rates/Mortgage-Rates"
    heloc_url = "https://www.andrewsfcu.org/Learn/Resources/Rates/Home-Equity-Loans-and-Lines-Rates"
    if request.args:
        hostName = request.args.get('hostName')
        print(hostName)
        output = parse(heloc_url, auto_loan_url, personal_loan_url, mortgage_loan_url, hostName)
        print(output)
        returnstr = "[" + ','.join(map(str, output))
        returnstr = returnstr + "]"
        return returnstr
