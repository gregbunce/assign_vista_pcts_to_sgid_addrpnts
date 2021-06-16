import arcpy
from helper_functions.get_countyname_from_num import get_countyname


#: Worker function.
def validate_sgid_addresses_and_voting_precincts(in_directory, in_dataset_name):

    #: add xy data to the in_dataset
    arcpy.AddXY_management(in_directory + in_dataset_name)

    #: add field to mark flagged address rows
    arcpy.AddField_management(in_directory + in_dataset_name, "FLAGGED", "TEXT", fieldPrecision, field_length=10, field_is_nullable="NULLABLE")

    #: find identical for address-based attributes only
    fields = ["UTAddPtID", "City", "ZipCode"]
    out_table = in_directory + "\\duplicate_addresspnts"
    duplicates = arcpy.FindIdentical_management(in_directory + in_dataset_name, out_table, fields, output_record_option="ONLY_DUPLICATES")


    #: loop through the dups and see if they have differnet x,y values - if so, flag as possible address pnt issue, if not, flag as possible vp issue




#: Main function.
if __name__ == "__main__":
    try:
        #: Set directory path for data files
        data_path = 'C:\\Users\\gbunce\\Documents\\projects\\vista\\agrc_addrpnts_with_vista_ballot_precincts\\2021_06_16\\'
        date_in_fgdb_file_name = "_2021616"
        dataset_name = "\\sgid_addrpnts_vista"

        #: Get a list of county numbers to run this project with. 
        
        #: all counties, in one list.
        county_list = [49001,49003,49005,49007,49009,49011,49013,49015,49017,49019,49021,49023,49025,49027,49029,49031,49033,49035,49037,49039,49041,49043,49045,49047,49049,49051,49053,49055,49057]

        #: The following three lines contain all the counties, broken into three batches.  I ran them in three batches but they ran fast enough that they can be run together.)
        #county_list = [49039,49021,49025,49057,49037,49017,49033,49043,49045]
        #county_list = [49001,49003,49005,49047,49019,49053,49027,49051,49023]
        #county_list = [49049,49013,49009,49031,49011,49029,49055,49015,49041,49007,49035]
        #county_list = [49045]

        #: Loop through desired counties and create output text files.
        for county in county_list:
            #: Create path to data.
            fgdb_data_path = data_path + county + date_in_fgdb_file_name + ".gdb"
            validate_sgid_addresses_and_voting_precincts(fgdb_data_path, dataset_name)

        print("Done checking addresses against voting precincts for the following counties: " + str(county_list))

    except Exception:
        e = sys.exc_info()[1]
        print(str(e.args[0]))
        print(str(arcpy.GetMessages(2)))
        #file.write("\n" + "ERROR MESSAGE from sys.exe_info: " + e.args[0]+ "\n")
        #ile.write("\n" + "ERROR MESSAGE from arcpy.GetMessages(2): " + arcpy.GetMessages(2))
        #file.close()
        #log_file.write('An exception has occured - %s' % e)
