import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CALENDARS = [
  'vif30abvsi70du85dvn3pd5tec@group.calendar.google.com', # Family
  'gsp4pcvtl33ug6rs0kb6liv03jvn3p43@import.calendar.google.com', #CHHS
  'ncaaf_-m-04ls81_%4eotre+%44ame+%46ighting+%49rish+football#sports@group.v.calendar.google.com' # ND Football
  ]

OUTPUT_FILE = os.environ.get('EVENT_FILE', "events.txt")

def cleanup_event_name(event_name):
  event_name = event_name.replace('SCHOOLS CLOSED', 'Schools Closed')
  event_name = event_name.replace('HOLIDAY RECESS', 'Holiday Recess')
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
  

  if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
  
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
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events = []
    for calendar in CALENDARS:
        events_result = (
            service.events()
            .list(
                calendarId=calendar,
                timeMin=now,
                maxResults=10,
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
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      if start.startswith(relevant_date): 
        event_str += cleanup_event_name(event["summary"]) + "\n"
    f = open(OUTPUT_FILE, "w")
    f.write(event_str)
    f.close()
        

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()