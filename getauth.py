import requests
import re
import time
import sys
import csv
import json
from notifiers import get_notifier
import configparser
config = configparser.ConfigParser()

config.read('sandboxconfig.ini')

telegram = get_notifier('telegram')
telegramchatid = config['DEFAULT']['telegramchatid']
districtids = config['DEFAULT']['district_ids']
telegramtoken = config['DEFAULT']['telegramtoken']
cowinauth = config['DEFAULT']['cowinauth']

print(telegramchatid)
print(districtids)
print(telegramtoken)
print(cowinauth)

headers = {"authority":"cdn-api.co-vin.in" , "accept":"application/json text/plain, */*"   , "authorization":cowinauth   , "sec-ch-ua-mobile":"?0"   , "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"   , "origin":"https://selfregistration.cowin.gov.in"   , "sec-fetch-site":"cross-site" , "sec-fetch-mode":"cors" , "sec-fetch-dest":"empty", "referer":"https://selfregistration.cowin.gov.in/" ,"accept-language":"en-US,en-DE;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,bn-IN;q=0.5,bn;q=0.4,hi-IN;q=0.3,hi;q=0.2"}

mdict = {}
while True:
    for distid in districtids.split(','):
        print(distid)
        try:
            r=requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id=%s&date=23-05-2021"%(distid), headers=headers)
            #print(r.status_code)
            print(r.json())
            resj = r.json()
            for center in resj['centers']:
                for session in center['sessions']:
                    cd = {}
                    cd['name'] = center['name']
                    cd['address'] = center['address']
                    cd['state'] = center['state_name']
                    cd['district'] = center['district_name']
                    cd['pincode'] = center['pincode']
                    cd['available'] = session['available_capacity']
                    cd['vaccine'] = session['vaccine']
                    cd['date'] = session['date']
                    cd['min_age_limit'] = session['min_age_limit']
                    key = cd['name']+':'+cd['vaccine']+':'+cd['date']+':'+str(cd['min_age_limit'])
                    if key not in mdict:
                        mdict[key] = cd
                    elif cd['available'] > 0 and mdict[key] != cd:
                        print(cd)
                        print("BOOK")
                        mdict[key] = cd
                        telegram.notify(message=json.dumps(cd,indent=4), token=telegramtoken, chat_id=telegramchatid)
                        time.sleep(1)
    
            time.sleep(1)
        except Exception as err:
            print(err)
            time.sleep(5)
    time.sleep(30)
