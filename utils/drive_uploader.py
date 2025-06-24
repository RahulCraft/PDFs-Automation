from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

FOLDER_ID = 'YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE'
CRED_PATH = 'permit_automation/creds/service-account.json'

def upload_to_drive(file_path):
    credentials = service_account.Credentials.from_service_account_file(CRED_PATH, scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    service.permissions().create(fileId=file['id'], body={"role": "reader", "type": "anyone"}).execute()
    return f"https://drive.google.com/file/d/{file['id']}/view"
