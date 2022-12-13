from __future__ import print_function

import datetime
import os.path
from sys import argv

import sqlite3

from dateutil import parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


from database import *

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


# ADD YOUR CALENDAR ID HERE
YOUR_CALENDAR_ID = '96kuerg3v0qi4rl93d3nhrkfseau6hpe@import.calendar.google.com'
YOUR_TIMEZONE = 'Europe/Paris'


def google_calendar_api(nb_jours):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    #token.json stores the user's access and refresh tokens, create when logging first time
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    #if there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        #save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    evenement = commitHours(creds, int(nb_jours))
    return evenement

def date_command(date_input):

    # print(date_input)

    temporalite = {
        'passé' : ['hier', 'il y a' + 'jour', 'dernier', 'dernière'],
        'futur' : ['demain', 'dans' + 'jour', 'prochaine', 'prochain'],
        'autres' : ['ce matin', 'cet après-midi', 'ce soir', 'cette nuit']
    }

    for i in range(len(temporalite['passé'])):
        if temporalite['passé'][i] in date_input:
            date_input = temporalite['passé'][i]
        if temporalite['futur'][i] in date_input:
            date_input = temporalite['futur'][i]
        if temporalite['autres'][i] in date_input:
            date_input = temporalite['autres'][i]

    print("\ncommande reçue par agenda [FILTERED] : ", date_input, '\n')

    return date_input
  
def commitHours(creds, nb_jours):
    try:

        service = build('calendar', 'v3', credentials=creds) #to call calendar API
        date_, label, type_seance, salle, heure= [], [], [], [], []
        for i in range(nb_jours):
            today= datetime.date.today() #date parsing
            next = datetime.date.today() + datetime.timedelta(days=i)
            # past = datetime.date.today() - datetime.timedelta(days=1)

            # day = int(today.strftime("%d"))
            # month = int(today.strftime("%m"))
            # year = int(today.strftime("%Y"))
            # today = str(year)+'-'+str(month)+'-'+str(day)
            # print('Date : ', next)
            timeStart = str(next) + "T00:00:00Z" # set time range
            timeEnd = str(next) + "T23:59:59Z" # Z = UTC time

            # print("Getting events...")
            events_result = service.events().list(calendarId=YOUR_CALENDAR_ID, timeMin=timeStart, timeMax=timeEnd, maxResults = 10, singleEvents=True, orderBy='startTime', timeZone=YOUR_TIMEZONE).execute()
            events = events_result.get('items', [])

            if not events:
                # print('! No upcoming events found !')
                pass

            total_duration = datetime.timedelta(
            seconds=0,
            minutes=0,
            hours=0,
            )
            id = 0
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                start_formatted = parser.isoparse(start) # changing the start time to datetime format
                end_formatted = parser.isoparse(end) # changing the end time to datetime format
                duration = end_formatted - start_formatted

                total_duration += duration
                date_.append(next)             
                label.append(event['summary'].split(',')[0][1:])
                type_seance.append(event['summary'].split(',')[1][1:].replace(' CDI','').split('Grp:')[1][1:])
                if "Salle: " in event['summary'].split(',')[-2][1:]:
                    salle.append(event['summary'].split(',')[-2][1:].replace('Salle: ',''))
                else:
                    salle.append(event['summary'].split(',')[-2][1:])
                heure.append('-'.join(event['description'].split('\n')[0].split('[')[1][:-1].split('-')[1:3]))
            

            # print("Temps de travail total: ", total_duration, "\n")

        evenement = {
                        "date"    : date_,
                        "matiere" : label,
                        "type" : type_seance, 
                        "salle" : salle, 
                        "heure" : heure
                    }
            

        return evenement

    except HttpError as error:
        print('An error occurred: %s' % error)

def addEvent(creds, duration, description):
    start = datetime.datetime.utcnow()
    
    end = datetime.datetime.utcnow() + datetime.timedelta(hours=int(duration))
    start_formatted = start.isoformat() + 'Z'
    end_formatted = end.isoformat() + 'Z'

    event = {
    'summary': description,
    'start': {
        'dateTime': start_formatted,
        'timeZone': YOUR_TIMEZONE,
        },
    'end': {
        'dateTime': end_formatted,
        'timeZone': YOUR_TIMEZONE,
        },
    }

    service = build('calendar', 'v3', credentials=creds)
    event = service.events().insert(calendarId=YOUR_CALENDAR_ID, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def getHours(number_of_days):

    # get today's date
    today = datetime.date.today()
    seven_days_ago = today + datetime.timedelta(days=-int(number_of_days))

    # get hours from database
    conn = sqlite3.connect('hours.db')
    cur = conn.cursor()

    cur.execute(f"SELECT DATE, HOURS FROM hours WHERE DATE between ? AND ?", (seven_days_ago, today))

    hours = cur.fetchall()

    total_hours = 0
    for element in hours:
        print(f"{element[0]}: {element[1]}")
        total_hours += element[1]
    print(f"Total hours: {total_hours}")
    print(f"Average hours: {total_hours/float(number_of_days)}")

def create_table_sql():
    #creer une table dans db sqlite
    conn.execute("CREATE TABLE edt(date text , matiere text, type text, heure text, salle text)")
    conn.commit()

def table_exist(name):
    param = ' name='+"'"+str(name)+"'"
    #get the count of tables with the name
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND"+param)

    #if the count is 1, then table exists
    if cursor.fetchone()[0]==1:
        print('table ['+str(name)+'] existe')
    else:
        print("table ["+str(name)+"] n'existe pas")

def set_agenda_database(values_to_insert):
    sql_agenda = "INSERT INTO edt (date, matiere, type, heure, salle) VALUES (?, ?, ?, ?, ?);"
    cursor.executemany(sql_agenda, values_to_insert)
    conn.commit()
    return values_to_insert

def update_agenda_database():
    sql_update_query = """UPDATE edt set salary = 10000 where id = 4"""
    cursor.execute(sql_update_query)
    conn.commit()

def check_info_database(values_to_insert):
    cursor.execute("""SELECT date, matiere, type, heure, salle from edt""")
    table = cursor.fetchall()

    for event in values_to_insert:
        for each_value in table:
            if each_value == event:
                print("Yeah! Find: {0}".format(each_value), "database\n", event, " evenement\n")
    conn.commit()
      
def delete_all_database():
    cursor.execute("""DELETE FROM edt""")
    conn.commit()

def recup_edt_to_list(nb_jours):
    evenement = google_calendar_api(nb_jours) #recup edt sur un jour
    values_to_insert = []
    for i in range(len(evenement['date'])):
        values_to_insert.append((str(evenement['date'][i]), str(evenement['matiere'][i]),
        str(evenement['type'][i]), str(evenement['heure'][i]), str(evenement['salle'][i])))
    return evenement, values_to_insert

# from chantal import *
# date_command(date_input)
# table_exist("edt")

# delete_all_database()
# set_agenda_database()
# evenement, values_to_insert = recup_edt_to_list(30)
# set_agenda_database(values_to_insert)


# conn.close()   



