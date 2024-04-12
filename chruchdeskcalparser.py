from lxml import etree
from io import StringIO
import requests
import dateutil.parser
import datetime
import locale
import json


class ChruchdeskCalParser:
    
    def __init__(self, frameId):
        self.frameId = frameId
        self.events = []
        self.lastpage = -1
        self.numberRemotePages = -1

    def load_events_interval(self, days):
        self.events = []
        pageid = 1
        while(pageid <= self.numberRemotePages or self.numberRemotePages == -1):
            new_events = self._load_events(pageid)
            pageid += 1
            
            if new_events == []:
                print("Dont get new events")
                break
            
            self.events += new_events
            
            delta = self.events[-1]['startDate'] - self.events[0]['startDate']
            
            if delta.days >= days:
                break
        return self.events
    
    def load_events(self, pageId=1):
        self.events = self._load_events(self.url, pageid)
        return self.events
        
    def _load_events(self, pageId=1):
        
        url = "https://widget.churchdesk.com/w/3232/event/" + self.frameId + "/" + str(pageId) + "/-/-/-/-/-?frameId=" + self.frameId + "-1"

        resp = requests.get(url)
        if resp.status_code != 200:
            print("Server responded " + str(resp.status_code))
            return []

        # Set explicit HTMLParser
        parser = etree.HTMLParser()
        
        # Decode the page content from bytes to string
        html = resp.content.decode("utf-8")

        #print(html)

        # Create your etree with a StringIO object which functions similarly
        # to a fileHandler
        tree = etree.parse(StringIO(html), parser=parser)
        
        data_script = tree.xpath("//script[@id = '__NEXT_DATA__']")
        
        print(data_script)
        
        page_data = json.loads(data_script[0].text)
        
        self.numberRemotePages = page_data['props']['pageProps']['widget']['totalPages']
        self.lastpage =  page_data['props']['pageProps']['widget']['pageNumber']
        
        events = page_data['props']['pageProps']['widget']['items']
        
        for event in events:
            if 'startDate' in event:
                event['startDate'] = dateutil.parser.parse(event['startDate'])
            if 'endDate' in event:
                event['endDate'] = dateutil.parser.parse(event['endDate']) 
            
            event['locationstr'] = ""
            if 'locationName' in event and event['locationName'] is not None:
                 event['locationstr'] += event['locationName']
            if 'location' in event and event['location'] is not None:
                 event['locationstr'] += (" (%s)"% event['locationName'])
            if event['locationstr'] == "":
                event['locationstr'] = event['churches'][0]['name']
        return events
    
    
    def get_events(self):
        return self.events

    def filter_events(self, startday, endday):
        result = []
        
        for event in self.events:
            if event['startDate'] >= startday and event['startDate'] <= endday:
                result.append(event)
        return result

    def get_day_location_structure(self, events=None):
        structure = {}
        
        myevents = self.events
        if events:
            myevents = events
        
        for event in myevents:
            if event['startDate'].strftime("%m/%d/%Y") in structure:
                if event['locationstr'] in structure[event['startDate'].strftime("%m/%d/%Y")]:
                    structure[event['startDate'].strftime("%m/%d/%Y")][event['locationstr']].append(event)
                else:
                    structure[event['startDate'].strftime("%m/%d/%Y")][event['locationstr']] = [event]
            else:
                structure[event['startDate'].strftime("%m/%d/%Y")] = {event['locationstr']: [event]}
        return structure

    def get_all_locations(self, events=None):
        myevents = self.events
        if events:
            myevents = events
        
        locations = [x['locationstr'] for x in myevents]
        locations = list(set(locations))
        return locations

    def get_all_days(self, events=None):
        myevents = self.events
        if events:
            myevents = events
        
        dates = [x['startDate'].date() for x in myevents]
        dates = list(set(dates))
        return dates

