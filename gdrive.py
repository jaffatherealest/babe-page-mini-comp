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

def upload_file_to_drive(service, file_io, file_name, mime_type='video/mp4', folder_id='1Ct9CM5BGYYBd35DyZxz8Ij7o-x9OWPSl'):
    """
    Uploads a file to a specified Google Drive folder using the Google Drive API.
    
    Args:
        service: The authenticated Google Drive service instance.
        file_io: A file-like object or file path (string) representing the video file to upload.
        file_name: The name of the file to be uploaded to Google Drive.
        mime_type: The MIME type of the file (default is 'video/mp4').
        folder_id: The ID of the folder in Google Drive where the file will be uploaded.
        
    Returns:
        The webViewLink for the uploaded file.
    """
    # If file_io is a string (file path), open the file in binary mode
    if isinstance(file_io, str):
        if not os.path.exists(file_io):
            raise FileNotFoundError(f"File {file_io} not found.")
        
        file_io = open(file_io, 'rb')  # Open the file in binary mode

    try:
        # Prepare file metadata and media upload object
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaIoBaseUpload(file_io, mimetype=mime_type, resumable=True)
        
        # Upload the file to Google Drive
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id, webViewLink'
        ).execute()

        # Set file permissions to "Anyone with the link"
        permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        service.permissions().create(fileId=uploaded_file.get('id'), body=permission).execute()

        # Get and return the webViewLink
        file_info = service.files().get(fileId=uploaded_file.get('id'), fields='webViewLink').execute()
        return file_info.get('webViewLink')
    
    finally:
        # Ensure the file is closed if it was opened
        if isinstance(file_io, io.IOBase):
            file_io.close()

def retrieve_drive_file_info(service, file_id):
    file_info = service.files().get(fileId=file_id, fields='id, name, webViewLink, thumbnailLink').execute()
    return file_info
