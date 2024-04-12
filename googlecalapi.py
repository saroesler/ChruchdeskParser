from __future__ import print_function

import datetime
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendar:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, calendarid, timezone='Europe/Berlin'):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        self.calendarid = calendarid
        self.timezone = pytz.timezone(timezone)
        
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('calendar', 'v3', credentials=creds)
        except HttpError as error:
            print('An error occurred: %s' % error)


    def get_events(self, maxResults=50):
        try:
            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 10 events')
            events_result = self.service.events().list(calendarId=self.calendarid, timeMin=now,
                                                  maxResults=maxResults, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])
            
            return events
            
        except HttpError as error:
            print('An error occurred: %s' % error)
    
    def create_event(self, title, start, end, description=None, location=None):
        event = {'start':{}, 'end':{}}
        
        if start.tzinfo:
            start_timezone = start
        else:
            start_timezone = self.timezone.localize(start)
        
        if start.tzinfo:
            end_timezone = end
        else:
            end_timezone = self.timezone.localize(end)
        
        event['summary'] = title
        
        event['start']['dateTime'] = start.isoformat()
        event['start']['timeZone'] = self.timezone.zone
        event['end']['dateTime'] = end.isoformat()
        event['end']['timeZone'] = self.timezone.zone
        
        if description:
            event['description'] = description
        if location:
            event['location'] = location

        event = self.service.events().insert(calendarId=self.calendarid, body=event).execute()
        return event.get('htmlLink')
    
    def create_events(self, events, standardduration=2):
        result = []
        for event in events:
            description = None
            location = None
            end = event['startDate'] + datetime.timedelta(hours=standardduration)
            
            if event['location']:
                location = event['location']
            if isinstance(event['endDate'], type(datetime.datetime.now())):
                end = event['endDate']
            
            result.append(self.create_event(event['title'], event['startDate'], end, description=description, location=location))
        return result
    
    def update_event(self, event):
        result = self.service.events().update(calendarId=self.calendarid, eventId=event['id'], body=event).execute()
        return result.get('htmlLink')
    
    def update_events(self, events):
        result = []
        for event in events:
            result.append(self.update_event(event))
        return result
    
    def delete_event(self, event):
        result = self.service.events().delete(calendarId=self.calendarid, eventId=event['id']).execute()
        return result
    
    def delete_events(self, events):
        result = []
        for event in events:
            result.append(self.delete_event(event))
        return result
