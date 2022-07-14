from Google import Create_Service, convert_to_RFC_datetime
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']
import os

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
calId = os.getenv('CALENDAR_ID')


def cal_insert(day, month, year, SID, color, user):
    time_conv = 4
    event_request_body = {
        'start': {
            'dateTime': convert_to_RFC_datetime(int('20' + year), month, day, 9 + time_conv, 0),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': convert_to_RFC_datetime(int('20' + year), month, day, 17 + time_conv, 0),
            'timeZone': 'America/New_York',
        },
        'summary': SID,
        'colorId': color,
        'attendees': [
            {
            'displayName': user,
            'optional': False,
            'Organizer': True,
            'responseStatus': 'accepted',
            'email': 'cylinder_removed_calendar@gmail.com'
        }
        ]
    }


    response = service.events().insert(
        calendarId=calId,
        body=event_request_body
    ).execute()
    
    eventID = response['id']

    return eventID

def cal_update(eventId, color):
    
    response = service.events().get(
        calendarId=calId, eventId=eventId
        ).execute()

    response['colorId'] = color

    response = service.events().update(
        calendarId=calId,
        eventId=eventId,
        body=response
    ).execute()
    
    return