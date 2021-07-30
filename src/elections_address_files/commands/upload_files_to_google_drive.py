
import os
from shutil import copyfile
import shutil

def upload_files(directory, folder_name):
    print("Move files to Google Drive...")

    google_drive_parent_directory = "G:\\My Drive\\agrc_public_share\\long_term_share\\voting_elections\\sgid_address_pnts_with_vista_pcts\\"

    #: Make a new folder on the Google Drive to hold this data.
    try:
        os.makedirs(google_drive_parent_directory + folder_name)
    except OSError as e:
        raise

    #: copy csv and zip files from local machine directory to corresponding google drive folder.
    ext = ('.zip', '.csv')
    
    # Iterate over all files and check for desired extentions for zipping.
    for file in os.listdir(directory):
        print(str(file))
        if file.endswith(ext):
            if file.endswith('.zip') and "DISCREPANCIES" in file:
                source_file = directory + "\\" + file
                destination_folder = google_drive_parent_directory + folder_name
                shutil.copy(source_file, destination_folder)
            elif file.endswith('.csv'):
                source_file = directory + "\\" + file
                destination_folder = google_drive_parent_directory + folder_name
                shutil.copy(source_file, destination_folder)

