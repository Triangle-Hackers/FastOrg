import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# Define scope
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Authentication with google sheets
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# List of organizations and their sheets
list_organizations = "https://docs.google.com/spreadsheets/d/1YWPQhhhrnnns4XjwEJykUsYszygLtCRBY0_sJTrr594/edit?gid=0#gid=0"
organizations = client.open_by_url(list_organizations).sheet1

organization_data = organizations.get_all_records()

# Folder to store csv files
os.makedirs("organizations", exist_ok=True)

for organization in organization_data:
    organization_name = organization["Organization Name"]
    sheet_url = organization["Sheet URL"]
    output_csv = organization["Output CSV"]

    # Individually open each organization's google sheets link
    sheet = client.open_by_url(sheet_url).sheet1

    # Get data and save to CSV
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    output_path = os.path.join("organizations", output_csv)
    df.to_csv(output_path, index=False)

    print(f"{organization_name} responses saved to {output_csv}")
