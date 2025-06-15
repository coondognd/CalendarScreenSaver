import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import json

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CALENDARS = [
  'vif30abvsi70du85dvn3pd5tec@group.calendar.google.com', # Family
  'gsp4pcvtl33ug6rs0kb6liv03jvn3p43@import.calendar.google.com', #CHHS
  'ncaaf_-m-04ls81_%4eotre+%44ame+%46ighting+%49rish+football#sports@group.v.calendar.google.com' # ND Football
  ]

ONE_DAY_FILE = os.environ.get('EVENT_FILE', "events.txt")
ALL_EVENTS_FILE = os.environ.get('CALENDAR_FILE', "events.json")

def cleanup_event_name(event_name):
  event_name = event_name.replace('SCHOOLS CLOSED', 'Schools Closed')
  event_name = event_name.replace('HOLIDAY RECESS', 'Holiday Recess')
  if len(event_name) > 40:
    event_name = event_name[0:40] + "..."
  return event_name

def is_late_in_the_day():
    """
    Determines if the current time is after 6 PM.

    :return: True if the current time is after 6 PM, otherwise False.
    """
    now = datetime.datetime.now()
    six_pm = now.replace(hour=18, minute=0, second=0, microsecond=0)
    return now > six_pm

def main():
  

  if os.path.exists(ONE_DAY_FILE):
    os.remove(ONE_DAY_FILE)
  if os.path.exists(ALL_EVENTS_FILE):
    os.remove(ALL_EVENTS_FILE)
  
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    # Calculate the most recent Sunday (or today if today is Sunday)

    today = datetime.date.today()
    # Calculate the 1st day of the current month
    first_of_month = today.replace(day=1)
    # Calculate the most recent Sunday (or today if today is Sunday)
    days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
    most_recent_sunday = today - datetime.timedelta(days=days_since_sunday)
    # Choose the earlier of the two dates
    start_date = min(first_of_month, most_recent_sunday)
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    # days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
    # most_recent_sunday = today - datetime.timedelta(days=days_since_sunday)
    # start_datetime = datetime.datetime.combine(most_recent_sunday, datetime.time.min)
    end_datetime = start_datetime + datetime.timedelta(days=31)
    time_min = start_datetime.isoformat() + "Z"
    time_max = end_datetime.isoformat() + "Z"

    print(f"Getting events from {time_min} to {time_max}")
    events = []
    for calendar in CALENDARS:
      events_result = (
        service.events()
        .list(
          calendarId=calendar,
          timeMin=time_min,
          timeMax=time_max,
          singleEvents=True,
          orderBy="startTime",
        )
        .execute()
      )
      events += events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return

    today_str = datetime.date.today().strftime('%Y-%m-%d')
    tomorrow = datetime.date.today() +  + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')

    relevant_date = today_str
    event_prefix = "Today:"
    if is_late_in_the_day():
      relevant_date = tomorrow_str
      event_prefix = "Tomorrow:"
    events = sorted(events, key=lambda event: event["start"].get("dateTime", event["start"].get("date")))
    # Prints the start and name of the next 10 events
    event_str = event_prefix + "\n"
    events_by_day = {}
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      isoStart = start.replace(":00Z", ":00-00:00")
      cleaned_event_name = cleanup_event_name(event["summary"])
      if start.startswith(relevant_date): 
        event_str += cleaned_event_name + "\n"
      if isoStart not in events_by_day:
        events_by_day[isoStart] = []
      events_by_day[isoStart].append(cleaned_event_name)
    f = open(ONE_DAY_FILE, "w")
    f.write(event_str)
    f.close()
    f = open(ALL_EVENTS_FILE, "w")
    f.write(json.dumps(events_by_day))
    f.close()
        

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()