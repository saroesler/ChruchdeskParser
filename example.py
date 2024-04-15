import datetime
import argparse
from chruchdeskcalparser import ChruchdeskCalParser
from googlecalapi import GoogleCalendar


def getby_startdate_of_google(event, googleevents):
    for googleevent in googleevents:
        if event['startDate'] == datetime.datetime.fromisoformat(googleevent['start']['dateTime']):
            return googleevent
    return None

def getby_startdate_of_churchdesk(googleevent, events):
    for event in events:
        if event['startDate'] == datetime.datetime.fromisoformat(googleevent['start']['dateTime']):
            return event
    return None

def compare_event_with_google(event, googleevent):
    #print("\n\n")
    changed = False
    if event['title'] != googleevent['summary']:
        print("Change title to " +  event['title'] + " was " + googleevent["summary"])
        googleevent['summary'] = event['title']
        changed = True
    if 'location' in googleevent and event['locationstr'] and event['locationstr'] != googleevent['location']:
        print("Change location to " +  event['location'] + " was " + googleevent["location"])
        googleevent['location'] = event['locationstr']
        changed = True
    #if isinstance(event['end'], type(datetime.datetime.now())):
    #   print(event['end'].isoformat() + "vs" + googleevent['end']['dateTime'])
    if isinstance(event['endDate'], type(datetime.datetime.now())) and event['endDate'].isoformat() != googleevent['end']['dateTime']:
        print("Change end to " +  event['endDate'].isoformat() + " was " + googleevent['end']['dateTime'] )
        googleevent['end']['dateTime'] = event['endDate'].isoformat()
        changed = True
    if changed:
        return googleevent
    return None

def filter_on_google(events, googleevents):
    newevents = []
    updateevents = []
    for event in events:
        googleevent = getby_startdate_of_google(event, googleevents)
        if googleevent:
            updateGoogleEvent = compare_event_with_google(event, googleevent)
            if updateGoogleEvent:
                updateevents.append(updateGoogleEvent)
        else:
            newevents.append(event)
    return newevents, updateevents

def filter_outdated_google(events, googleevents):
    outdated = []
    for googleevent in googleevents:
        event = getby_startdate_of_churchdesk(googleevent, events)
        if not event:
            outdated.append(googleevent)
    return outdated


frameId = "chruchdeskFrameId"
googlekalender = 'googleCalendarId@group.calendar.google.com'
duration = 720

parser = argparse.ArgumentParser(description='Update the google calendar based on churchdesk')
parser.add_argument('-s','--source', help='chruchdesk frameId', default=frameId)
parser.add_argument('-d','--destination', help='google calendar id', default=googlekalender)
parser.add_argument('-n','--days', help='number of days to control', type=int, default=duration)
parser.add_argument('-c','--create', help='enable creation of new events', action="store_true")
parser.add_argument('-r','--remove', help='enable remove of outdated events', action="store_true")
parser.add_argument('-u','--update', help='enable update of changed events', action="store_true")
args = parser.parse_args()


duration = args.days
frameId = args.source
googlekalender = args.destination

parser = ChruchdeskCalParser(frameId)
events = parser.load_events_interval(duration)

googlecal = GoogleCalendar(googlekalender)
googleevents = googlecal.get_events()

print("I found these %d events on chruchdesk: "%len(events))
print(events)

print("\n\nI found these %d events on google: "%len(googleevents))
print(googleevents)

newevents, updateevents = filter_on_google(events, googleevents)
print("\n\nNew events %d:"%(len(newevents)))
print(newevents)

if args.create:
    newaddr = googlecal.create_events(newevents)
    print("\n\nNew addresses %d:"%(len(newaddr)))
    print(newaddr)
elif len(newevents)> 0:
    print("Creation is not activated. Use -c to send the new events to google.")

print("\n\nUpdated events %d:"%(len(updateevents)))
print(updateevents)

if len(updateevents) > 0 and args.update:
    updateaddr = googlecal.update_events(updateevents)
    print("\n\nUpdated addresses %d:"%(len(updateaddr)))
    print(updateaddr)
elif len(updateevents)> 0:
    print("Update is not activated. Use -u to send the changed events to google.")

outdated = filter_outdated_google(events, googleevents)
print("\n\nOutdated events %d:"%(len(outdated)))
print(outdated)

if len(outdated) > 0 and args.remove:
    updateaddr = googlecal.delete_events(outdated)
    print("\n\nDeleted addresses %d:"%(len(updateaddr)))
    print(updateaddr)
elif len(outdated)> 0:
    print("Deletion is not activated. Use -r to remove the events to google.")





exit(0)

