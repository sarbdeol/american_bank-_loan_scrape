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
from fractions import Fraction
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
    soup = bs(r.text,'html.parser')
    # print(r.text)
    typ = 'personalLoan'
   

    table = soup.find("table", {"class": "responsiveTable datatable"})

    headers = []
    rows = []

    # Get table headers
    for th in table.find_all("th"):
        headers.append(th.text.strip())

    # Get table rows
    for tr in table.find_all("tr"):
        row = []
        for td in tr.find_all("td"):
            row.append(td.text.strip())
        if len(row) > 0:
            rows.append(row)

    # Print headers and rows
    # print(headers)
    # print(rows)
    years = []
    rates = []

    for row in rows:
        term = re.findall(r'\d+(?= Months)',row[0])
        
        year = int(term[0])/12
        rate = float(row[2].replace("%", ""))
        years.append(year)
        rates.append(rate)


    info = { "type": typ, "urlLink": url,"minPeriod": min(years), "maxPeriod": max(years), "rateFrom": min(rates), "rateTo": max(rates), "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'personalLoan', "itemType":[info]}}

    # json_str = json.dumps(dic)
    return dic


def get_auto_loan(url,  bankName, bankUrl, bankID):

    # url='https://www.americanheritagecu.org/loans/auto-loans'
    r  = get(url)
    soup = bs(r.text,'html.parser')
    # print(r.text)
    typ = 'autoLoan'
   

    table = soup.find("table", {"class": "responsiveTable datatable"})

    headers = []
    rows = []

    # Get table headers
    for th in table.find_all("th"):
        headers.append(th.text.strip())

    # Get table rows
    for tr in table.find_all("tr"):
        row = []
        for td in tr.find_all("td"):
            row.append(td.text.strip())
        if len(row) > 0:
            rows.append(row)

    # Print headers and rows
    # print(headers)
    # print(rows)
    years = []
    rates = []

    for row in rows:
        term = re.findall(r'\d+(?= Months)',row[0])
        # print(term)
        
        year =( int(term[0])/12)
        rate = float(row[1].replace("%", ""))
        years.append(year)
        rates.append(rate)
    
    info1 = { "type": "new", "urlLink": url,"minPeriod": min(years), "maxPeriod":  max(years),"rateFrom": min(rates), "rateTo": max(rates), "maxAmount": ""}
    info2 = { "type": "used", "urlLink": url,"minPeriod": min(years), "maxPeriod":  max(years),"rateFrom": min(rates), "rateTo": max(rates), "maxAmount": ""}
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'autoLoan', "itemType":[info1,info2]}}
    json_str = json.dumps(dic)
    # print(json_str)
    return dic
   

def get_student_loan(url,  bankName, bankUrl, bankID):
    r  = get(url)
    soup = bs(r.content,'html.parser')
    
     
    typ = 'stundetLoan'
    itemType = []

    variable_rates_text = ''
    for p in soup.find_all('p'):
        if p.find('b', text=re.compile('^Variable rates:')):
            variable_rates_text = p.find('b', text=re.compile('^Variable rates:')).next_sibling.strip()
            fixed_rates_text = p.find('b', text=re.compile('^Fixed rates:')).next_sibling.strip()
            
            break
    variable_rates_text = variable_rates_text.replace('\xa0', ' ')
    variable_rates_text = variable_rates_text.replace('APR', '')
    variable_rates = variable_rates_text.split(' – ')
    
    variable_rates = variable_rates[0].split(' ')
    var_min=variable_rates[0][0].replace('%','')
    var_max=variable_rates[2][0].replace('%','')
  

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

    info1 = { "type": "newLoan", "urlLink": "https://www.salliemae.com/landing/student-loans/?RefID=1987000001&CoBrandingID=001143&dtd_cell=SMLRSOPTRPSSN010297&_ga=2.161315965.1178841339.1682350085-1104792461.1680804135","minPeriod": eval(period[0]), "maxPeriod":  eval(period[1]), "rateFrom": eval(fixed_rates_min), "rateTo": eval(fixed_rates_max), "maxAmount": "", "variableAPR":False, "fixedAPR": True}
    info2 = { "type": "newLoan", "urlLink": "https://www.salliemae.com/landing/student-loans/?RefID=1987000001&CoBrandingID=001143&dtd_cell=SMLRSOPTRPSSN010297&_ga=2.161315965.1178841339.1682350085-1104792461.1680804135","minPeriod": eval(period[0]), "maxPeriod":  eval(period[1]), "rateFrom": eval(var_min), "rateTo": eval(var_max), "maxAmount": "", "variableAPR":True, "fixedAPR": False}
    
    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": 'studentLoan', "itemType":[info1,info2]}}
    json_str = json.dumps(dic)
    
    return dic


def get_home_Equity():
   
    # url='https://www.americanheritagecu.org/loans/home-equity-loans'
    r  = get('https://www.americanheritagecu.org/rates#homeEquity')
    soup = bs(r.content, "html.parser")

        # Find the table with the specified class and text
    # soup = bs(response.content, "html.parser")

    table = soup.find("section", {"class": "rates", "aria-label": "Rates for Home Equity Loan Rates (Up to 70% LTV)"}) \
        .find("table", {"class": "responsiveTable"})
        # Initialize min and max values to None

        # Initialize min and max values to None
    min_term = None
    max_term = None
    min_apr = None
    max_apr = None

    # Loop through all rows in the table
    for row in table.tbody.find_all("tr"):
        # Extract the term and APR values
        term = row.find_all("td")[0].text.strip()
        apr = row.find_all("td")[1].text.strip().replace("%","")

        # Remove the "Up to" prefix from the term string
        term = term.replace("Up to", "")
        term = term.replace("to", "")
        term = term.replace("Months", "").replace("months", "")
        
        
        # Convert the term string to an integer and then to years
        term_int = int(term.split()[0]) / 12
        
        # Update min and max values if necessary
        if min_term is None or term_int < float(min_term.split()[0]):
            min_term = "{:.0f}".format(term_int)
            min_apr = apr
        try:
            if max_term is None or (int(term.split()[1]) / 12) > float(max_term.split()[0]):
                max_term = "{:.0f}".format((int(term.split()[1]) / 12))
                max_apr = apr
        except:
            pass

  
    table = soup.find("section", {"class": "rates", "aria-label": "Rates for Home Equity Loan Rates (70.001% - 80% LTV)"}) \
        .find("table", {"class": "responsiveTable"})
        # Initialize min and max values to None

        # Initialize min and max values to None
    min_term3 = None
    max_term3 = None
    min_apr3 = None
    max_apr3 = None

    # Loop through all rows in the table
    for row in table.tbody.find_all("tr"):
        # Extract the term and APR values
        term = row.find_all("td")[0].text.strip()
        apr = row.find_all("td")[1].text.strip().replace("%","")

        # Remove the "Up to" prefix from the term string
        term = term.replace("Up to", "")
        term = term.replace("to", "")
        term = term.replace("Months", "").replace("months", "")
        
        
        # Convert the term string to an integer and then to years
        term_int = int(term.split()[0]) / 12
        
        # Update min and max values if necessary
        if min_term3 is None or term_int < float(min_term3.split()[0]):
            min_term3 = "{:.0f}".format(term_int)
            min_apr3 = apr
        try:
            if max_term3 is None or (int(term.split()[1]) / 12) > float(max_term3.split()[0]):
                max_term3 = "{:.0f}".format((int(term.split()[1]) / 12))
                max_apr3 = apr
        except:
            pass

    # Print the results
    
    table = soup.find("section", {"class": "rates", "aria-label": "Rates for Home Equity Loan Rates (80.001% - 90% LTV)"}) \
        .find("table", {"class": "responsiveTable"})
        # Initialize min and max values to None

        # Initialize min and max values to None
    min_term4 = None
    max_term4 = None
    min_apr4 = None
    max_apr4 = None

    # Loop through all rows in the table
    for row in table.tbody.find_all("tr"):
        # Extract the term and APR values
        term = row.find_all("td")[0].text.strip()
        apr = row.find_all("td")[1].text.strip().replace("%","")

        # Remove the "Up to" prefix from the term string
        term = term.replace("Up to", "")
        term = term.replace("to", "")
        term = term.replace("Months", "").replace("months", "")
        
        
        # Convert the term string to an integer and then to years
        term_int = int(term.split()[0]) / 12
        
        # Update min and max values if necessary
        if min_term4 is None or term_int < float(min_term4.split()[0]):
            min_term4 = "{:.0f}".format(term_int)
            min_apr4 = apr
        try:
            if max_term4 is None or (int(term.split()[1]) / 12) > float(max_term4.split()[0]):
                max_term4 = "{:.0f}".format((int(term.split()[1]) / 12))
                max_apr4 = apr
        except:
            pass

    # Print the results
    
    info1 = {"type": "homeEquity",  "urlLink": "https://www.americanheritagecu.org/rates#homeEquity",  "minPeriod":min_term,  "maxPeriod": max_term,  "rateFrom": min_apr,  "rateTo": max_apr,  "maxAmount": "",  "ltvFrom": '70',  "ltvTo": "",  "description": "Up to 70%",  "default": True  }
    info2 = {"type": "homeEquity",  "urlLink": "https://www.americanheritagecu.org/rates#homeEquity",  "minPeriod":min_term,  "maxPeriod": max_term,  "rateFrom": min_apr,  "rateTo": max_apr,  "maxAmount": "",  "ltvFrom": '71',  "ltvTo": '80',  "description": "71%-80%",  "default": False }
    info3 = {"type": "homeEquity",  "urlLink": "https://www.americanheritagecu.org/rates#homeEquity",  "minPeriod":min_term3,  "maxPeriod": max_term3,  "rateFrom": min_apr3,  "rateTo": max_apr3,  "maxAmount": "",  "ltvFrom": '81',  "ltvTo": '89',  "description": "81%-89%",  "default": False }
    info4 = {"type": "homeEquity",  "urlLink": "https://www.americanheritagecu.org/rates#homeEquity",  "minPeriod":min_term4,  "maxPeriod": max_term4,  "rateFrom": min_apr4,  "rateTo": max_apr4,  "maxAmount": "",  "ltvFrom": '91',  "ltvTo": '95',  "description": "91%-95%",  "default": False }
    return [info1,info2,info3,info4]
    # data=info1,info2
    # itemType.extend(data)
        
def get_heloc(url,  bankName, bankUrl, bankID):
    
    #__________________________default_values
    loanType = "helocLoan"
    type1 = 'helocLoan'
    description = 'Up to 70 '
    min_period=1;max_period=20
    #__________________________scraping
    soup = bs(requests.get(url).content,'html.parser')

    # Find the table with the specified class and text
    table = soup.find("section", {"class": "rates", "aria-label": "Rates for Interest-Only HELOC"}) \
        .find("table", {"class": "responsiveTable"})

    # Find all the rows in the table
    rows = table.find_all('tr')

    # Loop through the rows and extract the data
    min_period = None
    max_period = None
    min_apr = None
    max_apr = None

    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            # Extract the period and APR values from the cells
            period = cells[0].text.strip()
            apr = float(cells[1].text.strip().strip('%'))

            # Check if this is the minimum or maximum period
            if 'Up to' in period:
                min_period = int(period.split()[2].replace('%', ''))
            if '-' in period:
                parts = period.split('-')
                max_period_str = parts[1].split()[0].strip()
                max_period_str = re.sub('[^0-9]', '', max_period_str)
                if not max_period or int(max_period_str) > max_period:
                    max_period = int(max_period_str)

            # Check if this is the minimum or maximum APR
            if not min_apr or apr < min_apr:
                min_apr = apr
            if not max_apr or apr > max_apr:
                max_apr = apr

    itemType = []
    info = {"type": type1,
            "urlLink": "https://www.americanheritagecu.org/rates#homeEquity",
            "minPeriod": '',
            "maxPeriod":'' ,
            "rateFrom": min_apr,
            "rateTo": max_apr,
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
    

def get_mortgages_2(url,  bankName, bankUrl, bankID):


    # url='https://www.americanheritagecu.org/loans/mortgages'
    r  = get(url)
    soup = bs(r.content,'html.parser')
    # print(r.text)
    typ = 'mortgageLoan'

    periods = []
    rates = []
    prices = []
    
    for row in soup.find_all('tbody')[1].find_all('tr'):
        cells = row.find_all('td')
        period = cells[0].text.strip().split('-')
        rate = float(cells[1].text.strip().replace('%', '').replace('†', ''))
        price = None  # no price data available in the provided table
        periods.append(period[0])
        rates.append(rate)
        prices.append(price)

    min_rate = min(rates)
    max_rate = max(rates)
    min_period = int(periods[rates.index(min_rate)])
    max_period = int(periods[rates.index(max_rate)])


    # print('Minimum rate: {}% for {}'.format(min_rate, min_period))
    # print('Maximum rate: {}% for {}'.format(max_rate, max_period))
    info3 = { "type": "refinance", "urlLink": url,"minPeriod": min_period, "maxPeriod":  max_period, "aprFrom": min_rate ,"aprTo":max_rate,"rateFrom": '', "rateTo": '', "maxAmount": "","variableAPR":False, "fixedAPR": True}

 
    ##########variable true##############

    table = soup.find('table', {'class': 'responsiveTable datatable'})

    rows = table.find('tbody').find_all('tr')
    periods = []
    rates = []
    aprs = []

    for row in rows:
        
        cells = row.find_all("td")
        term = cells[0].text.strip()
        if 'ARM' in term:
            periods.append(term)
            rate = float(cells[1].text.strip().replace("%", ""))
            apr = float(cells[2].text.strip().replace("%", ""))
        
            rates.append(rate)
            aprs.append(apr)
    # Extract the numbers from each ARM value using regular expressions
    arm_numbers = [re.findall(r'\d+', arm) for arm in periods]

    # Convert the numbers to floats and divide the first number by the second to get the fractional form
    arm_fractions = [float(num[0])/float(num[1]) for num in arm_numbers]

    # Get the minimum and maximum fractional values
    min_arm = min(arm_fractions)
    max_arm = max(arm_fractions)

    # Convert the min and max fractional values back to the a/b form
    min_period = f"{int(min_arm)}/1"
    max_period = f"{int(max_arm)}/1"

    # Print the results


    min_rates = min(rates)
    max_rates = max(rates)
    min_aprs = min(aprs)
    max_aprs = max(aprs)


    # print(f"Min: {min_period}")
    # print(f"Max: {max_period}")

    # print()
    # print("Rate:")
    # print("Min:", min_rates)
    # print("Max:", max_rates)
    # print()
    # print("APR:")
    # print("Min:", min_aprs)
    # print("Max:", max_aprs)
    info1 = { "type": "purchase", "urlLink": url,"minPeriod": min_period, "maxPeriod":  max_period, "aprFrom": min_aprs, "aprTo":max_aprs,"rateFrom": min_rates, "rateTo": max_rates, "maxAmount": "","variableAPR":True, "fixedAPR": False}
   
   
    #################FIXED#########################
    
    rows = table.find_all('tr')[1:7]  # select first 6 rows

    # initialize min and max values as first row values
    min_period, max_period = int(rows[0].find_all('td')[0].text.replace('Year','')), int(rows[0].find_all('td')[0].text.replace('Year',''))
    min_rate, max_rate = float(rows[0].find_all('td')[1].text.replace('%', '')), float(rows[0].find_all('td')[1].text.replace('%', ''))
    min_apr, max_apr = float(rows[0].find_all('td')[2].text.replace('%', '')), float(rows[0].find_all('td')[2].text.replace('%', ''))

    for row in rows[1:]:
        columns = row.find_all('td')
        
        if 'FHA' not in columns[0].text and 'VA' not in columns[0].text and 'ARM' not in columns[0].text:
            period = int(re.findall('\d+\/\d+|\d+', columns[0].text.strip())[0])
            rate = float(columns[1].text.strip().replace('%', ''))
            apr = float(columns[2].text.strip().replace('%', ''))
            
            # update min and max values
            if period < min_period:
                min_period = period
            if period > max_period:
                max_period = period
            if rate < min_rate:
                min_rate = rate
            if rate > max_rate:
                max_rate = rate
            if apr < min_apr:
                min_apr = apr
            if apr > max_apr:
                max_apr = apr

    # print(f"Min Period: {min_period}")
    # print(f"Max Period: {max_period}")
    # print(f"Min Rate: {min_rate}%")
    # print(f"Max Rate: {max_rate}%")
    # print(f"Min APR: {min_apr}%")
    # print(f"Max APR: {max_apr}%")
    info2 = { "type": "purchase", "urlLink": url,"minPeriod": min_period, "maxPeriod":  max_period, "aprFrom": min_apr, "aprTo":max_apr,"rateFrom": min_rate, "rateTo": max_rate, "maxAmount": "","variableAPR":False, "fixedAPR": True}

    dic = {'bankName':bankName, 'bankID':bankID, 'date':time.strftime("%m-%d-%Y"), 'timestamp':time.strftime("%m-%d-%Y %H:%M:%S"), 'bankUrl':bankUrl, 'bankDetails':{"loanType": typ, "itemType":[info1,info2,info3]}}
    # json_str = json.dumps(dic)
    # print(dic)
    return dic
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

def fetch_data ():
   
    auto_loan_url = 'https://www.americanheritagecu.org/loans/auto-loans'
    mortgage_loan_url = 'https://www.americanheritagecu.org/loans/mortgages'
    personal_loan_url = 'https://www.americanheritagecu.org/loans/personal-loans'
    student_loan_url = "https://www.salliemae.com/landing/student-loans/?RefID=1987000001&CoBrandingID=001143&dtd_cell=SMLRSOPTRPSSN010297&_ga=2.161315965.1178841339.1682350085-1104792461.1680804135"
    heloc='https://www.americanheritagecu.org/rates#homeEquity'
    output = parse(heloc, auto_loan_url,mortgage_loan_url, personal_loan_url, student_loan_url)
    print(output)
    returnstr = "[" + ','.join(map(str, output))
    returnstr = returnstr + "]"
    return returnstr
    
fetch_data()