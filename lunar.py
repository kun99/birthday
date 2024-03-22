from lunardate import LunarDate
from datetime import date
from smtplib import SMTP, SMTPException
from email.message import EmailMessage
import traceback
from dotenv import load_dotenv
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

sender = os.getenv("SENDER")
recipient = os.getenv("RECIPIENT")
password = os.getenv("PASSWORD")

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# below code is from google calendar api docs
def get_creds():
    creds = None
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
    return creds

def calc():
    today = date.today()
    year = today.year
    lunar_month = 3
    lunar_day = 23
    lunar_date = LunarDate(year, lunar_month, lunar_day)
    print("Birthday this year:", lunar_date.toSolarDate())
    event = {
        'summary': 'Birthday',
        'start': {
            'date': str(lunar_date.toSolarDate()),
        },
        'end': {
            'date': str(lunar_date.toSolarDate()),
        },
    }
    return lunar_date.toSolarDate(), event

def email():
    msg = EmailMessage()
    date, event = calc()
    msg.set_content("Birthday this year: " + str(date) + "\n\n This email was generated automatically.")

    msg['Subject'] = 'Birthday'
    msg['From'] = sender
    msg['To'] = recipient
    try: 
        with SMTP("smtp.gmail.com", 587) as server:   
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            print("SENT EMAIL")
        creds = get_creds()
        service = build("calendar", "v3", credentials=creds)
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except (SMTPException, ConnectionError, HttpError) as e:
        print("Got an error. :c", e)
        traceback.print_exc()

email()