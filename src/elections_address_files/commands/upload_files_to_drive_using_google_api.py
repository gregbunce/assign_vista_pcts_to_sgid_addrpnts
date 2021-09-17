
import os
from shutil import copyfile
import shutil
from commands.Google import Create_Service
from googleapiclient.http import MediaFileUpload

def upload_files(directory, folder_name):
    print("Move files to Google Drive...")

    CLIENT_SECRET_FILE = 'C:\\Users\\gbunce\\Documents\\Visual Studio 2013\\Projects\\python\\sgid_addrpnts_vista_pcts\\src\\client_secret.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service (CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    #: Make a new folder on the Google Drive to hold this data.
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': ['12WTSnre9iIs4ZkmMyT24HZkPFgy_cB9t']
    }
    new_folder = service.files().create(body=file_metadata,fields='id').execute()
    folder_id = new_folder.get('id')


    #: copy csv and zip files from local machine directory to corresponding google drive folder.
    ext = ('.zip', '.csv')
    
    # Iterate over all files and check for desired extentions for zipping.
    for file in os.listdir(directory):
        print(str(file))
        if file.endswith(ext):
            if file.endswith('.zip') and "DISCREPANCIES" in file:
                file_metadata = {
                    'name': file,
                    'parents': [folder_id]
                }

                media = MediaFileUpload(directory + "\\" + file, mimetype='application/zip')

                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

            elif file.endswith('.csv'):
                file_metadata = {
                    'name': file,
                    'parents': [folder_id]
                }

                media = MediaFileUpload(directory + "\\" + file, mimetype='text/csv')

                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
