import os, datetime, sys, setuptools
from commands.assign_vista_pcts_to_sgid_addpnts import *
from commands.validate_election_data import *
from commands.zip_files import *
from commands.upload_files_to_google_drive import *

def main(county_list, gis_validation):
    print("Begin...")
    print("  Processing the following counties: " + str(county_list))

    #: STEP 1
    #: Create new directory with today's date (this folder will hold the output data from this script).
    directory, folder_name = create_output_dir_with_todays_date()

    #: STEP 2
    #: Call create_county_address_vista_files.py.
    #: Loop through desired counties and create output text files.
    for county in county_list:
        do_work_and_save_as_csv(county, directory + "\\", folder_name)

    #: STEP 3
    #: (optional) Call validate_election_data.py (this script creates the gis files that show possible discrepancies).
    #: Loop through desired counties and create output text files.
    if gis_validation == "validate_gis":
        print("Running GIS validation checks...")
        #: Set directory path for data files
        dataset_name = "\\sgid_addrpnts_vista_placenames"

        for county in county_list:
            #: Create path to data.
            fgdb_data_path = directory + "\\" + county + "_" + folder_name + ".gdb"
            print("Begin validating for " + str(county) + ":")
            validate_sgid_addresses_and_voting_precincts(fgdb_data_path, dataset_name)

        #: Export the flagged rows (the onces with possible issues) into a single file geodatabase.
        export_flagged_rows_to_fgdb(directory + "\\", folder_name, county_list, dataset_name, "statewide_layer") # last param is either "individual_county_layers" or "statewide_layer"
    else:
        print("Skipping GIS validation checks.")

    #: STEP 4
    #: zip up each fgdb output(s) that were created step 1.
    zipfiles(directory)

    #: STEP 5
    #: copy the the output data (that's in the newly created floder in step 1) to the agrc_public_share were folks can pick up the data.
    upload_files(directory, folder_name)

    print("Done!")
    print("  Completed counties include: " + str(county_list))

def create_output_dir_with_todays_date():
    #: Create a folder based on the date (ie: Year_Month_Day = 2021_1_15)
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    folder_name = str(year) + "_" + str(month) + "_" + str(day)
    
    #: create the output folder one directory up from the current
    #directory = "..\\" + folder_name
    directory = "C:\\Temp\\county_election_files\\" + folder_name
    try:
        os.makedirs(directory)
    except OSError as e:
        raise

    return directory, folder_name;


#: Main function.
if __name__ == "__main__":
    try:
        list_of_counties = sys.argv[1].split(',')
        gis_validation = sys.argv[2]
        print(str(sys.argv[1]))
        print((sys.argv[2]))

        #: create list from list_of_counties commandline string.


        #: setup params:
        #: Get a list of county names to run this project with.
        #: all counties, in one list.
        #list_of_counties = ['SANPETE','IRON','KANE','WEBER','SAN_JUAN','GARFIELD','RICH','SUMMIT','TOOELE','BEAVER','BOX_ELDER','CACHE','UINTAH','GRAND','WASHINGTON','MILLARD','WASATCH','JUAB','UTAH','DUCHESNE','DAGGETT','PIUTE','DAVIS','MORGAN','WAYNE','EMERY','SEVIER','CARBON','SALT_LAKE']
        ##list_of_counties = ['DAGGETT']
        #: determine if we're running the additional/optional gis validation checks that output the discrepancies fgdb
        ##run_gis_validation_checks_bool = True

        main(list_of_counties, gis_validation)

    except Exception:
        e = sys.exc_info()[1]
        print(str(e.args[0]))
        print(str(arcpy.GetMessages(2)))
