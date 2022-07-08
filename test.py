import pprint
from Google import Create_Service, convert_to_RFC_datetime
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


colors = service.colors().get().execute()
time_conv = 4
event_request_body = {
    'start': {
        'dateTime': convert_to_RFC_datetime(2022, 8, 8, 9 + time_conv, 0),
        'timeZone': 'America/New_York',
    },
    'end': {
        'dateTime': convert_to_RFC_datetime(2022, 8, 8, 17 + time_conv, 0),
        'timeZone': 'America/New_York',
    },
    'summary': 'eighthed',
    'description': 'here is my description',
    'colorId': 7,
    'attendees': [
        {
        'displayName': 'Talha from Pyth',
        'optional': False,
        'Organizer': True,
        'responseStatus': 'accepted',
        'email': 'cylinder_removed_calendar@gmail.com'
    }
    ]
}

response = service.events().insert(
    calendarId='61r7bbq1d657on0lv46hpq3e24@group.calendar.google.com',
    body=event_request_body
).execute()

# event = {
#   'summary': 'Google I/O 2015',
#   'location': '800 Howard St., San Francisco, CA 94103',
#   'description': 'A chance to hear more about Google\'s developer products.',
#   'start': {
#     'dateTime': '2015-05-28T09:00:00-07:00',
#     'timeZone': 'America/Los_Angeles',
#   },
#   'end': {
#     'dateTime': '2015-05-28T17:00:00-07:00',
#     'timeZone': 'America/Los_Angeles',
#   },
#   'recurrence': [
#     'RRULE:FREQ=DAILY;COUNT=2'
#   ],
#   'attendees': [
#     {'email': 'lpage@example.com'},
#     {'email': 'sbrin@example.com'},
#   ],
#   'reminders': {
#     'useDefault': False,
#     'overrides': [
#       {'method': 'email', 'minutes': 24 * 60},
#       {'method': 'popup', 'minutes': 10},
#     ],
#   },
# }

# event = service.events().insert(calendarId='primary', body=event).execute()
