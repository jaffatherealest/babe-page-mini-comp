import io
import os
import requests
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

# Scopes for the Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_drive_api():
    """
    
    function which authenticates with the google drive api for further use of other functions
    
    """
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token_file:
            creds = Credentials.from_authorized_user_info(json.load(token_file), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
        else:
            raise Exception("No valid credentials available.")
    service = build('drive', 'v3', credentials=creds)
    return service

def download_file_from_url(url):
    """
    
    function which downloads a video to mem(io) from the video url
    
    """
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

def upload_file_to_drive(service, file_io, file_name, mime_type='video/mp4', folder_id='1-9Qn9nA50hnmxYaT3LfdgpJvMDB73SoM'):
    """
    
    this function is using the google drive api to upload data to a select folder in google drive. 
    in this example we are uploading mp4 video file

    folder name = "Babe Page Reels [MIRROR RESCHANGE]"
    https://drive.google.com/drive/u/0/folders/1-9Qn9nA50hnmxYaT3LfdgpJvMDB73SoM
    
    """
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(file_io, mimetype=mime_type, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    
    # Set permissions to "Anyone with the link"
    permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    service.permissions().create(fileId=file.get('id'), body=permission).execute()
    
    # Retrieve the updated file metadata to get the webViewLink
    file = service.files().get(fileId=file.get('id'), fields='webViewLink').execute()
    
    return file.get('webViewLink')

def retrieve_drive_file_info(service, file_id):
    file_info = service.files().get(fileId=file_id, fields='id, name, webViewLink, thumbnailLink').execute()
    return file_info
