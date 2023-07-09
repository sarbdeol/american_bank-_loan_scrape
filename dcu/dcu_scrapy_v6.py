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

def data_validation(dataDictList):
    url = "https://us-central1-lendmesh.cloudfunctions.net/data-validation"

    payload = json.dumps(dataDictList)
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

#____________________

def get_student_loan(url,bankName, bankUrl, bankID):
    r  = get(url)
    soup = bs(r.content,'html.parser')
    
    typ = None
    itemType = []
    loans = [i for i in soup.findAll('div',{'class':'dcuRateTable aem-GridColumn aem-GridColumn--default--12'}) if "Student Loans - Undergraduate" in i.text]
    rate1 = re.findall(r'between\s\d+\.\d+\%\sand\s\d+\.\d+\%',loans[0].text.strip())[0]
    rate2 = re.findall(r'between\s\d+\.\d+\%\sand\s\d+\.\d+\%',loans[1].text)[0]
    rates1 = [float(i) for i in re.findall(r'\d+\.\d+',rate1)]
    rates2 = [float(i) for i in re.findall(r'\d+\.\d+',rate2)]

    #___________________
    loans1 = [i for i in soup.findAll('div',{'class':'dcuRateTable aem-GridColumn aem-GridColumn--default--12'}) if "RATE STUDENT REFINANCE LOAN RATES" in i.text.upper()]
    table1  = loans1[0]; table2 = loans1[1]
    rows1 = [i for i in table1.findAll('tr') if "<th" not in str(i)]
    rows2 = [i for i in table2.findAll('tr') if "<th" not in str(i)]
    periods = []
    rr1 = []
    rr2 = []
    for i in rows1:
       i = i.findAll('td')
       term = int(re.findall(r'\d+',i[0].text.strip())[0])
       print(term)
       val = re.findall(r'\d+\.\d+',i[1].text.strip())
       rr1 = rr1+[float(i) for i in val]
       periods.append(term)
    for i in rows2:
       i = i.findAll('td')
       val = re.findall(r'\d+\.\d+',i[1].text.strip())
       val = re.findall(r'\d+\.\d+',i[1].text.strip())
       rr2 = rr2+[float(i) for i in val]


    info1 = { "type": "newLoan", "urlLink": "https://www.dcu.org/about/rates.html#:~:text=Agreement%20for%20Consumers.-,Student%20Loans,-STUDENT%20LOANS%20%2D%20UNDERGRADUATE","minPeriod": '', "maxPeriod":  '', "rateFrom": min(rates1), "rateTo": max(rates1), "maxAmount": "", "variableAPR":False, "fixedAPR": True}
    info2 = { "type": "newLoan", "urlLink": "https://www.dcu.org/about/rates.html#:~:text=Agreement%20for%20Consumers.-,Student%20Loans,-STUDENT%20LOANS%20%2D%20UNDERGRADUATE","minPeriod": '', "maxPeriod":  '', "rateFrom": min(rates2), "rateTo": max(rates2), "maxAmount": "", "variableAPR":True, "fixedAPR": False}
    info3 = { "type": "refinance", "urlLink": "https://www.dcu.org/about/rates.html#:~:text=Agreement%20for%20Consumers.-,Student%20Loans,-STUDENT%20LOANS%20%2D%20UNDERGRADUATE","minPeriod": min(periods), "maxPeriod": max(periods), "rateFrom": min(rr1), "rateTo": max(rr1), "maxAmount": "", "variableAPR":True, "fixedAPR": False}
    info4 = { "type": "refinance", "urlLink": "https://www.dcu.org/about/rates.html#:~:text=Agreement%20for%20Consumers.-,Student%20Loans,-STUDENT%20LOANS%20%2D%20UNDERGRADUATE","minPeriod": min(periods), "maxPeriod": max(periods), "rateFrom": min(rr2), "rateTo": max(rr2), "maxAmount": "", "variableAPR":False, "fixedAPR": True}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'studentLoan', "itemType":[info1,info2,info3,info4]}}
    return dic

#_____________________________________________________


def get_auto_loan(url,  bankName, bankUrl, bankID):
  
    #url = "https://www.dcu.org/about/rates.html"
    r  = get(url)
    soup = bs(r.content,'html.parser')
    
    typ = None
    itemType = []
    divs = [i for i in soup.findAll('div',{'class':'dcuRateTable aem-GridColumn aem-GridColumn--default--12'}) if "AUTO LOAN" in i.text.upper()]
    
    terms1 = []
    rates1 = []
    terms2 = []
    rates2 = []
    for i in divs[0].findAll('tr'):
        if "Terms" in i.text:
          continue
        i = i.findAll('td')
        terms1.append(int(re.findall(r'\d+',i[0].text)[0])/12)
        rates1.append(float(re.findall(r'\d+\.\d+',i[1].text)[0]))
    for i in divs[1].findAll('tr'):
        if "Terms" in i.text:
          continue
        i = i.findAll('td')
        terms2.append(int(re.findall(r'\d+',i[0].text)[0])/12)
        rates2.append(float(re.findall(r'\d+\.\d+',i[1].text)[0]))
            
    info1 = { "type": "new", "urlLink": "https://www.dcu.org/about/rates.html#Borrow:~:text=Vehicle%20Loans-,Auto,-Loans%20and%20Auto","minPeriod": min(terms1), "maxPeriod":  max(terms1),"rateFrom": min(rates1), "rateTo": max(rates1), "maxAmount": ""}
    info2 = { "type": "used", "urlLink": "https://www.dcu.org/about/rates.html#Borrow:~:text=Vehicle%20Loans-,Auto,-Loans%20and%20Auto","minPeriod": min(terms2), "maxPeriod":  max(terms2),"rateFrom": min(rates2), "rateTo": max(rates2), "maxAmount": ""}
  
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1,info2]}}
    return dic
  #____________________


def get_personal_loan(url,  bankName, bankUrl, bankID):
 
    url = "https://www.dcu.org/about/rates.html"
    r  = get(url)
    soup = bs(r.content,'html.parser')
    typ = 'personalLoan'
    loan = [div for div in soup.findAll('div',{'class':'dcuRateTable aem-GridColumn aem-GridColumn--default--12'}) if "TRADITIONAL SIGNATURE LOANS" in div.text.upper()][0]
    tds = loan.findAll('tr')[1].findAll('td')
    period = int(re.findall(r'\d+',tds[0].text)[0])/12
    rate = float(re.findall(r'\d+\.\d+',tds[1].text)[0])
    info = { "type": typ, "urlLink": "https://www.dcu.org/about/rates.html#:~:text=by%20contacting%20DCU.-,Personal,-Loans","minPeriod": '', "maxPeriod": period, "rateFrom": rate, "rateTo": '', "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'personalLoan', "itemType":[info]}}
    return dic

#_________________________________________
from pickle import TUPLE2
def get_mortgage_loan(url,bankName, bankUrl, bankID):

  url = "https://www.dcu.org/about/rates.html"
  r  = get(url)
  soup = bs(r.content,'html.parser')
  itemType = []
  tables = [i for i in soup.findAll('div',{'class':'optimalBlueRateTable aem-GridColumn aem-GridColumn--default--12'}) if "Refinance Fixed-Rate Mortgage Rates" in i.text or "Purchase Fixed-Rate Mortgage Rates" in i.text]
  tables2  = [i for i in soup.findAll('div',{'class':'optimalBlueRateTable aem-GridColumn aem-GridColumn--default--12'}) if "REFINANCE ADJUSTABLE RATE MORTGAGE (ARM) RATES" in i.text.upper() or "PURCHASE ADJUSTABLE RATE MORTGAGE (ARM) RATES" in i.text.upper()]

  t1 = [i for i in tables if "Refinance Fixed-Rate Mortgage Rates" in i.text][0]
  t2 = [i for i in tables if "Purchase Fixed-Rate Mortgage Rates" in i.text][0]
  t3 = [i for i in tables2 if "REFINANCE ADJUSTABLE RATE MORTGAGE (ARM) RATES" in i.text.upper()][0]
  t4 = [i for i in tables2 if "PURCHASE ADJUSTABLE RATE MORTGAGE (ARM) RATES" in i.text.upper()][0]

  #____table 1

  rows1 = [i for i in t1.findAll('tr') if "Terms" not in i.text]
  terms1 = []; aprs1 = []; rates1 = []
  for i in rows1:
      i = bs(str(i)).findAll('td')
      terms1.append(int(re.findall(r'\d+',i[0].text)[0]))
      rates1.append(float(re.findall(r'\d+\.\d+',i[1].text)[0]))
      aprs1.append(float(re.findall(r'\d+\.\d+',i[2].text)[0]))
      
  #____table 2
  rows2 = [i for i in t2.findAll('tr') if "Terms" not in i.text]
  terms2 = []; aprs2 = []; rates2 = []
  for i in rows2:
      i = bs(str(i)).findAll('td')
      terms2.append(int(re.findall(r'\d+',i[0].text)[0]))
      rates2.append(float(re.findall(r'\d+\.\d+',i[1].text)[0]))
      aprs2.append(float(re.findall(r'\d+\.\d+',i[2].text)[0]))

  rows3 = [i for i in t3.findAll('tr') if "<th" not in str(i)]
  terms3 = []; aprs3 = []; rates3 = []
  for i in rows3:
      i = bs(str(i)).findAll('td')
      terms3.append(int(re.findall(r'\d+',i[1].text)[0]))
      rates3.append(float(re.findall(r'\d+\.\d+',i[2].text)[0]))
      aprs3.append(float(re.findall(r'\d+\.\d+',i[3].text)[0]))

  rows4 = [i for i in t4.findAll('tr') if "<th" not in str(i)]
  terms4 = []; aprs4 = []; rates4 = []
  for i in rows4:
      i = bs(str(i)).findAll('td')
      terms4.append(int(re.findall(r'\d+',i[1].text)[0]))
      rates4.append(float(re.findall(r'\d+\.\d+',i[2].text)[0]))
      aprs4.append(float(re.findall(r'\d+\.\d+',i[3].text)[0]))

  info1 = { "type": 'refinance', "urlLink": "https://www.dcu.org/about/rates.html#:~:text=of%20the%20loan.-,Mortgage,-Loans","minPeriod": min(terms1), "maxPeriod":  max(terms1), "aprFrom": min(aprs1), "aprTo": max(aprs1), "rateFrom": min(rates1), "rateTo": max(rates1), "maxAmount": "", "variableAPR":False, "fixedAPR": True}
  info2 = { "type": 'purchase', "urlLink": "https://www.dcu.org/about/rates.html#:~:text=of%20the%20loan.-,Mortgage,-Loans","minPeriod": min(terms2), "maxPeriod":  max(terms2), "aprFrom": min(aprs2), "aprTo": max(aprs2), "rateFrom": min(rates2), "rateTo": max(rates2), "maxAmount": "", "variableAPR":False, "fixedAPR": True}
  info3 = { "type": 'refinance', "urlLink": "https://www.dcu.org/about/rates.html#:~:text=of%20the%20loan.-,Mortgage,-Loans","minPeriod": min(terms3), "maxPeriod":  max(terms3), "aprFrom": min(aprs3), "aprTo": max(aprs3), "rateFrom": min(rates3), "rateTo": max(rates3), "maxAmount": "", "variableAPR":True, "fixedAPR": False}
  info4 = { "type": 'purchase', "urlLink": "https://www.dcu.org/about/rates.html#:~:text=of%20the%20loan.-,Mortgage,-Loans","minPeriod": min(terms4), "maxPeriod":  max(terms4), "aprFrom": min(aprs4), "aprTo": max(aprs4), "rateFrom": min(rates4), "rateTo": max(rates4), "maxAmount": "", "variableAPR":True, "fixedAPR": False}
  dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": "mortgageLoan", "itemType":[info1,info2,info3,info4]}}
  return dic

#____________________________________________________________

def get_home_Equity(heloc_url):
    
    #__________________________default_values
    loanType = "helocLoan"
    type1 = 'helocLoan'
    description = 'Up to 60%'
    min_period=1;max_period=20
    #__________________________scraping
    soup = bs(requests.get(heloc_url).content,'html.parser')
    divs = [i for i in soup.findAll('div',{'class':'optimalBlueRateTable aem-GridColumn aem-GridColumn--default--12'}) if "Fixed-Rate Home Equity Loan" in str(i)]
    rates1 = []
    rates2 = []
    periods1 = []
    periods2 = []
    
    for row in divs[0].findAll('tr'):
        try: 
          col = row.findAll('td')
        except:
          continue
        try:
          periods1.append(int(re.findall(r'\d+',col[0].text)[0]))
          rates1.append(float(re.findall(r'\d+\.\d+',col[2].text)[0]))
        except: pass
    for row in divs[1].findAll('tr'):
        try:
          col = row.findAll('td') 
        except:
          continue
        try:
          periods2.append(int(re.findall(r'\d+',col[0].text)[0]))
          rates2.append(float(re.findall(r'\d+\.\d+',col[2].text)[0]))
        except: pass
    print(rates1)
    print(rates2)    
    info1 = {"type": "homeEquity",  "urlLink": "https://www.dcu.org/about/rates.html#:~:text=per%20%241%2C000%20borrowed.-,FIXED%2DRATE%20HOME%20EQUITY,-LOAN%20RATES",  "minPeriod":min(periods1),  "maxPeriod": max(periods1),  "rateFrom": min(rates1),  "rateTo": max(rates1),  "maxAmount": "",  "ltvFrom": '60',  "ltvTo": "",  "description": "Up to 60%",  "default": True  }
    info2 = {"type": "homeEquity",  "urlLink": "https://www.dcu.org/about/rates.html#:~:text=Line%20of%20Credit%20(-,HELOC,-)%20Rate",  "minPeriod":min(periods2),  "maxPeriod": max(periods2),  "rateFrom": min(rates2),  "rateTo": max(rates2),  "maxAmount": "",  "ltvFrom": '90',  "ltvTo": "",  "description": "Up to 90%",  "default": False }
    return [info1,info2]


def get_heloc(heloc_url, bankName, bankUrl, bankID):
    
    #__________________________default_values
    loanType = "helocLoan"
    type1 = 'helocLoan'
    description = 'Up to 60%'
    min_period=1;max_period=20
    #__________________________scraping
    soup = bs(requests.get(heloc_url).content,'html.parser')
    div = [i for i in soup.findAll('div',{'class':'dcuRateTable aem-GridColumn aem-GridColumn--default--12'}) if "HOME EQUITY LINE OF CREDIT (HELOC) RATE" in str(i).upper()]
    rate_from = div[0].findAll("td")[1].text.replace(" ","").replace("%","")
    itemType = []
    info = {"type": type1,
            "urlLink": "https://www.dcu.org/about/rates.html#:~:text=Line%20of%20Credit%20(-,HELOC,-)%20Rate",
            "minPeriod": min_period,
            "maxPeriod": max_period,
            "rateFrom": rate_from,
            "rateTo": "",
            "maxAmount": "",
            "ltvFrom": description.replace("Up to ","").replace("%",""),
            "ltvTo": "",
            "description": description,
            "default": True
            }

    itemType.append(info)
    itemType = itemType+get_home_Equity(heloc_url)
    dic = {"bankName": bankName, "bankID": bankID, "date": time.strftime("%m-%d-%Y"),
           "timestamp": time.strftime("%m-%d-%Y %H:%M:%S"), "bankUrl": bankUrl,
           "bankDetails": {"loanType": loanType, "itemType": itemType}}

    return dic


def parse(heloc_url, auro_loan_url, mortgage_loan_url, personal_loan_url, student_loan_url):
    
    bankName = 'dcu'
    bankUrl = 'https://www.dcu.org/'
    bankID = 787995
    try:
      itemType1 = get_auto_loan(auro_loan_url, bankName, bankUrl, bankID)
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
      itemType4 = get_mortgage_loan(mortgage_loan_url, bankName, bankUrl, bankID)
    except:
      itemType4 = {}
    try:
      itemType5 = get_heloc(heloc_url, bankName, bankUrl, bankID)
    except:
      itemType5 = {}

    dic = [itemType1, itemType2, itemType3, itemType4 , itemType5] 
    print('dic')
    print(dic)
    validatedDictList = data_validation(dic)
    print('validatedDictList')
    print(validatedDictList)
    '''
    db = firestore.Client(project='lendmesh')
    for validatedDict in validatedDictList:
        displayValue = validatedDict['display']
        print("displayValue")
        print(displayValue)
        if str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="personalLoan":
            if displayValue == True:
                doc_per = db.collection(u'webscrapy_stage').document(u'personalloan').collection(u'bankrates').document(bankName)
                doc_per.set(validatedDict, merge=True)
                doc_per = db.collection(u'webscrapy_stage_history').document(u'personalloan').collection(bankName)
                doc_per.add(validatedDict)
            elif displayValue == False:
                print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - PersonalLoan')
                print("Inside loop")
                print(validatedDict)
                validatedDict = { "display": False }
                doc_per = db.collection(u'webscrapy_stage').document(u'personalloan').collection(u'bankrates').document(bankName)
                doc_per.set(validatedDict, merge=True)

        elif str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="autoLoan":
            if displayValue == True:
                doc_auto = db.collection(u'webscrapy_stage').document(u'autoloan').collection(u'bankrates').document(bankName)
                doc_auto.set(validatedDict, merge=True)
                doc_auto = db.collection(u'webscrapy_stage_history').document(u'autoloan').collection(bankName)
                doc_auto.add(validatedDict)
            elif displayValue == False:
                print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - AutoLoan')
                print("Inside loop")
                print(validatedDict)
                validatedDict = { "display": False }
                doc_auto = db.collection(u'webscrapy_stage').document(u'autoloan').collection(u'bankrates').document(bankName)
                doc_auto.set(validatedDict, merge=True)

        elif str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="helocLoan":
            if displayValue == True:
                doc_heloc = db.collection(u'webscrapy_stage').document(u'helocloan').collection(u'bankrates').document(bankName)
                doc_heloc.set(validatedDict, merge=True)
                doc_heloc = db.collection(u'webscrapy_stage_history').document(u'helocloan').collection(bankName)
                doc_heloc.add(validatedDict)
            elif displayValue == False:
                print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - HelcoLoan')
                print("Inside loop")
                print(validatedDict)
                validatedDict = { "display": False }
                doc_heloc = db.collection(u'webscrapy_stage').document(u'helocloan').collection(u'bankrates').document(bankName)
                doc_heloc.set(validatedDict, merge=True)

        elif str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="mortgageLoan":
            if displayValue == True:
                doc_mortgage = db.collection(u'webscrapy_stage').document(u'mortgageloan').collection(u'bankrates').document(bankName)
                doc_mortgage.set(validatedDict, merge=True)
                print(validatedDict)
                doc_mortgage = db.collection(u'webscrapy_stage_history').document(u'mortgageloan').collection(bankName)
                doc_mortgage.add(validatedDict)
            elif displayValue == False:
                print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - MortgageLoan')
                print("Inside loop")
                print(validatedDict)
                validatedDict = { "display": False }
                doc_mortgage = db.collection(u'webscrapy_stage').document(u'mortgageloan').collection(u'bankrates').document(bankName)
                doc_mortgage.set(validatedDict, merge=True)
        elif str(validatedDict.get('bankDetails',{}).get('loanType','')).strip()=="studentLoan":
            if displayValue == True:
                doc_studentloan = db.collection(u'webscrapy_stage').document(u'studentloan').collection(u'bankrates').document(bankName)
                doc_studentloan.set(validatedDict, merge=True)
                print(validatedDict)
                doc_studentloan = db.collection(u'webscrapy_stage_history').document(u'studentloan').collection(bankName)
                doc_studentloan.add(validatedDict)
            elif displayValue == False:
                print('ERROR: DATA NOT CAPTURED IN DB. PLEASE FIX THE CODE - StudentLoan')
                print("Inside loop")
                print(validatedDict)
                validatedDict = { "display": False }
                doc_studentloan = db.collection(u'webscrapy_stage').document(u'studentloan').collection(u'bankrates').document(bankName)
                doc_studentloan.set(validatedDict, merge=True) 

    # f = open("affinityplus.json", "w", encoding='utf-8')
    # tmp = json.dumps(validatedDictList, indent=4)
    # f.write(tmp)
    # f.close()
    '''
    return validatedDictList

def fetch_data (request):
    rate_url = "https://www.dcu.org/about/rates.html" 
    heloc_url = 'https://www.dcu.org/borrow/mortgage-loans/home-equity-loans.html'
    auro_loan_url = "https://www.dcu.org/about/rates.html#:~:text=RATES-,Vehicle%20Loans%C2%A0%C2%A0,-Auto%20Loans%20and" 
    mortgage_loan_url = "https://www.dcu.org/about/rates.html#:~:text=of%20the%20loan.-,Mortgage%20Loans,-Purchase%20Fixed%2DRate"
    personal_loan_url = "https://www.dcu.org/about/rates.html#:~:text=by%20contacting%20DCU.-,Personal%20Loans,-Traditional%20Signature%20Loans"
    student_loan_url = "https://www.dcu.org/about/rates.html#:~:text=Lending%20Disclosure%20Statement.-,Student%20Loans,-Student%20Loans%20%2D%20Undergraduate"
    output = parse(heloc_url, auro_loan_url, mortgage_loan_url, personal_loan_url, student_loan_url)
    print(output)
    returnstr = "[" + ','.join(map(str, output))
    returnstr = returnstr + "]"
    return returnstr
