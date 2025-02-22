import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


# Define scope
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Authentication with google sheets
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open Google Sheets
sheet = client.open("Membership Form (Responses)").sheet1

# Get the records from google sheets
data = sheet.get_all_records()

df = pd.DataFrame(data)

df.to_csv("form_responses.csv", index=False)
