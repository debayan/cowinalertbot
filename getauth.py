import requests
import re
import time
import sys
import csv
import json
import os
from datetime import date
from datetime import timedelta
from notifiers import get_notifier
import configparser
config = configparser.ConfigParser()

config.read('sandboxconfig.ini')

telegram = get_notifier('telegram')
telegramchatid = config['DEFAULT']['telegramchatid']
districtids = config['DEFAULT']['district_ids']
telegramtoken = config['DEFAULT']['telegramtoken']
cowinauth = config['DEFAULT']['cowinauth']
personalchatid = config['DEFAULT']['personalchatid']
weeks = int(config['DEFAULT']['weeks'])

# print(telegramchatid)
# print(districtids)
# print(telegramtoken)
# print(cowinauth)

notified_stale_token = False

headers = {"authority":"cdn-api.co-vin.in" , "accept":"application/json text/plain, */*"   , "authorization":cowinauth   , "sec-ch-ua-mobile":"?0"   , "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"   , "origin":"https://selfregistration.cowin.gov.in"   , "sec-fetch-site":"cross-site" , "sec-fetch-mode":"cors" , "sec-fetch-dest":"empty", "referer":"https://selfregistration.cowin.gov.in/" ,"accept-language":"en-US,en-DE;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,bn-IN;q=0.5,bn;q=0.4,hi-IN;q=0.3,hi;q=0.2"}

mdict = {}
while True:
    for distid in districtids.split(','):
        print('District', distid)
        try:
            today = date.today()
            for i in range(weeks):
                search_for = (today + timedelta(days=7*i)).strftime('%d-%m-%Y')
                print('Week of ' + search_for)
                r = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id=%s&date=%s"%(distid, search_for), headers=headers)
                # print(r.status_code)
                # print(r.json())

                try:
                    resj = r.json()
                except json.decoder.JSONDecodeError:
                    print('ERROR Decoding JSON')
                    print(r.text)
                    if r.text == 'Unauthenticated access!' and not notified_stale_token:
                        print('Notifying stale token to admin')
                        telegram.notify(message='Please refresh token', token=telegramtoken, chat_id=personalchatid)
                        notified_stale_token = True
                count = 0
                for center in resj['centers']:
                    for session in center['sessions']:
                        cd = {}
                        cd['name'] = center['name']
                        cd['address'] = center['address']
                        cd['state'] = center['state_name']
                        cd['district'] = center['district_name']
                        cd['pincode'] = center['pincode']
                        cd['available'] = session['available_capacity']
                        cd['available1'] = session['available_capacity_dose1']
                        cd['available2'] = session['available_capacity_dose2']
                        cd['vaccine'] = session['vaccine']
                        cd['date'] = session['date']
                        cd['min_age_limit'] = session['min_age_limit']
                        key = cd['name']+':'+cd['vaccine']+':'+cd['date']+':'+str(cd['min_age_limit'])
                        if key not in mdict:
                            mdict[key] = cd
                        elif (cd['available'] > 0 and mdict[key] != cd):
                            count += 1
                            mdict[key] = cd
                            message = [str(cd['pincode']) + ' ' + str(cd['min_age_limit']) + '+ ' + cd['vaccine'] + ' ' + cd['date']]
                            message.append(str(cd['available']) + ' slots')
                            message.append('Dose 1: ' + str(cd['available1']) + ', ' + 'Dose 2: ' + str(cd['available2']))
                            message.append(cd['name'] + ', ' + cd['district'])
                            message.append(cd['address'])
                            telegram.notify(message='\n'.join(message), token=telegramtoken, chat_id=telegramchatid)
                            time.sleep(0.25)
                print('Slots found: ' + str(count))
                time.sleep(2)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            time.sleep(5)
    time.sleep(30)
