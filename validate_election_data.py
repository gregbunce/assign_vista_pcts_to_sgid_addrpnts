import arcpy
from helper_functions.get_countyname_from_num import get_countyname

#: This script is dependent on the output from 'assign_vista_pcts_to_sgid_addpnts.py' in this repo
#: Before running this script, make sure to set these variable 
    # data_path
    # date_in_fgdb_file_name
    # county_names
    # dataset_name (this one should be fine, it's basically static)
    # out_table (this one should be fine, it's basically static)


#: Worker function.
def validate_sgid_addresses_and_voting_precincts(in_directory, in_dataset_name):

    #: add xy data to the in_dataset
    arcpy.AddXY_management(in_directory + in_dataset_name)

    #: Add field to mark flagged address records.
    flagged_exists = False
    dup_seqid_exists = False
    fields = arcpy.ListFields(in_directory + in_dataset_name)
    for field in fields:
        if field.name == "FLAGGED":
            flagged_exists = True
        elif field.name == "DUP_SEQID":
            dup_seqid_exists = True
    if flagged_exists == False:
        arcpy.AddField_management(in_directory + in_dataset_name, "FLAGGED", "TEXT", field_length=30, field_is_nullable="NULLABLE")
    if dup_seqid_exists == False:
        arcpy.AddField_management(in_directory + in_dataset_name, "DUP_SEQID", "LONG", field_precision=6, field_is_nullable="NULLABLE")

    #: find identical for address-based attributes only
    fields = ["UTAddPtID", "City", "ZipCode"]
    out_table = in_directory + "\\duplicate_addresspnts"
    duplicates = arcpy.FindIdentical_management(in_directory + in_dataset_name, out_table, fields, output_record_option="ONLY_DUPLICATES")

    #: Identify addresses that are duplicates by assigning the sequence id to the DUP_SEQID field.
    print("begin assigning sequence ids...")
    transfer_seqIDs_to_featureclass(in_directory + in_dataset_name, duplicates)

    #: Loop through the dataset and check if any rows do not contain a voting precinct.
    print("begin check for missing voting precinct...")
    check_for_missing_vp(in_directory + in_dataset_name)

    #: Loop through the duplicate addresses and see if it's an address point issue or voting precinct issue (if they have differnet x,y values then addrpnt, if same x,y then vp issue - ie: an overlap)
    print("begin checking duplicates to see if address point issue or voting precinct issue...")
    check_duplicate_addresses_for_issue(in_directory + in_dataset_name, in_directory, duplicates)

    #: Check if there is a descrepency as to what county the address belongs to.



#: This method adds the Sequence ID values from the find identical output table to the input feature class.
def transfer_seqIDs_to_featureclass(feature_class, find_identical_output):

    #: add sequence id and see if it has no vp, 
    with arcpy.da.SearchCursor(find_identical_output, ["IN_FID", "FEAT_SEQ"]) as search_cur:
        for dup_row in search_cur:
            dup_seq = dup_row[1]
            dup_oid = dup_row[0]

            with arcpy.da.UpdateCursor(feature_class, ["DUP_SEQID"], where_clause='OBJECTID = ' + str(dup_oid)) as update_cur:
                for update_row in update_cur:
                    update_row[0] = dup_seq
                    update_cur.updateRow(update_row)


#: Check for address point rows with missing voting precinct (ie: there's a gap in VP layer)
def check_for_missing_vp(feature_class):
    with arcpy.da.UpdateCursor(feature_class, ["FLAGGED"], where_clause="VistaID is Null or VistaID = ''") as update_cur:
        for row in update_cur:
            row[0] = "Missing VP"
            update_cur.updateRow(row)


#: Check duplicate addresses for issue type.
def check_duplicate_addresses_for_issue(feature_class, in_directory, duplicates):
    #: Get the highest DUP_SEQID value to looping though later.
    max_dup_seqid_val = get_max_value_of_dup_seqid(duplicates, in_directory)

    #: Loop through for as as many unique sequence ids (duplicate addresses) there are.
    for seqid_val in range(max_dup_seqid_val):
        #: advance the value from '0' to '1' (it's zero based)
        seqid_val = seqid_val + 1
        
        #: Check how many duplicates there are for this sequence id.
        with arcpy.da.SearchCursor(feature_class, ["FLAGGED", "DUP_SEQID"], where_clause="DUP_SEQID = " + str(seqid_val)) as search_cur:
            number_of_dup_addresses = 0
            for row in search_cur:
                number_of_dup_addresses = number_of_dup_addresses + 1
        print(str(number_of_dup_addresses) + " duplicates for sequence id: " + str(seqid_val))

        #: if there are 2 duplicates address compare the locations and voting precincts, else flag as having x amount of duplicates.
        if number_of_dup_addresses == 2:
            dup_oid_1 = ""
            dup_oid_2 = ""
            dup_pct_1 = ""
            dup_pct_2 = ""
            dup_location_1 = ""
            dup_location_2 = ""
            with arcpy.da.SearchCursor(feature_class, ["FLAGGED", "DUP_SEQID", "VistaID", "POINT_X", "POINT_Y", "OBJECTID", "SHAPE@"], where_clause="DUP_SEQID = " + str(seqid_val)) as search_cur:
                x = 0
                for row in search_cur:
                    x = x + 1
                    #: Set the values to comapre for both features.
                    if x == 1:
                        dup_oid_1 = row[5]
                        dup_pct_1 = row[2]
                        dup_location_1 = str(round(row[3])) + "-" + str(round(row[4]))
                    else:
                        dup_oid_2 = row[5]
                        dup_pct_2 = row[2]
                        dup_location_2 = str(round(row[3])) + "-" + str(round(row[4]))

            #     #: needs work here... it there are no rows left to work with.. need another update cur.  maybe above is search and this is update.
            with arcpy.da.UpdateCursor(feature_class, ["FLAGGED", "DUP_SEQID", "VistaID", "POINT_X", "POINT_Y", "OBJECTID", "SHAPE@"], where_clause="DUP_SEQID = " + str(seqid_val)) as update_cur:
                #: Evaluate if address point issue or vp issue.
                for row in update_cur:
                    if row[5] == dup_oid_1:
                        if dup_pct_1 != dup_pct_2 and str(dup_location_1) != str(dup_location_2):
                            row[0] = "Possible AddrPnt Issue Diff VP"
                        elif dup_pct_1 != dup_pct_2 and str(dup_location_1) == str(dup_location_2):
                            row[0] = "Possible VP Issue"
                        else:
                            row[0] = "Possible AddrPnt Issue Same VP"
                        update_cur.updateRow(row)
                    elif row[5] == dup_oid_2:
                        if dup_pct_1 != dup_pct_2 and str(dup_location_1) != str(dup_location_2):
                            row[0] = "Possible AddrPnt Issue Diff VP"
                        elif dup_pct_1 != dup_pct_2 and str(dup_location_1) == str(dup_location_2):
                            row[0] = "Possible VP Issue"
                        else:
                            row[0] = "Possible AddrPnt Issue Same VP"
                        update_cur.updateRow(row)
                    else:
                        row[0] = "somthing went wrong"
        else:
            with arcpy.da.UpdateCursor(feature_class, ["FLAGGED", "DUP_SEQID"], where_clause="DUP_SEQID = " + str(seqid_val)) as update_cur:
                for row in update_cur:
                    row[0] = str(number_of_dup_addresses) + " duplicates found"
                    update_cur.updateRow(row)


#: Get max seqid value.
def get_max_value_of_dup_seqid(duplicates, in_directory):
    out_table = in_directory + "\\summary_stats"
    arcpy.Statistics_analysis(duplicates, out_table, [["FEAT_SEQ", "MAX"]])

    max_val = 0
    with arcpy.da.SearchCursor(out_table, ["MAX_FEAT_SEQ"], where_clause="OBJECTID = 1") as search_cur:
        for row in search_cur:
            max_val = search_cur[0]
    return int(max_val)



#: Main function.
if __name__ == "__main__":
    try:
        #: Set directory path for data files
        data_path = 'C:\\Users\\gbunce\\Documents\\projects\\vista\\agrc_addrpnts_with_vista_ballot_precincts\\2020_10_22\\'
        date_in_fgdb_file_name = "_2021615"
        dataset_name = "\\sgid_addrpnts_vista_placenames"

        #: Get a list of county names to run this project with.
        county_names = ['TOOELE']

        #: Loop through desired counties and create output text files.
        for county in county_names:
            #: Create path to data.
            fgdb_data_path = data_path + county + date_in_fgdb_file_name + ".gdb"
            validate_sgid_addresses_and_voting_precincts(fgdb_data_path, dataset_name)

        print("Done checking addresses against voting precincts for the following counties: " + str(county_names))

    except Exception:
        e = sys.exc_info()[1]
        print(str(e.args[0]))
        print(str(arcpy.GetMessages(2)))
        #file.write("\n" + "ERROR MESSAGE from sys.exe_info: " + e.args[0]+ "\n")
        #ile.write("\n" + "ERROR MESSAGE from arcpy.GetMessages(2): " + arcpy.GetMessages(2))
        #file.close()
        #log_file.write('An exception has occured - %s' % e)
