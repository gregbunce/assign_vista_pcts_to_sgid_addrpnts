import arcpy
from arcpy import env
import datetime
import csv

'''
My Notes: 
   1. Manually, create a new directory to store the output files.  I've been creating it here 'C:/Users/gbunce/Documents/projects/vista/agrc_addrpnts_with_vista_ballot_precincts'
   2. Update the local vista directory location variable ('local_vista_directory') to point at the directory created in step 1.
   3. Determine what counties need to be run and indicate those county numbers in the 'county_list' variable in the 'Main' function below. 
   4. Copy the output files here: G:\My Drive\VISTA\shared_files (Google Drive)
'''

#: Set global variables.
local_vista_directory = 'C:/Users/gbunce/Documents/projects/vista/agrc_addrpnts_with_vista_ballot_precincts/Sept23rd2019'  # use this varible below, in place of hard-coded strings (change in four places)
# local_vista_directory_on_old_tower = 'D:/vista/agrc_addrpnts_with_vista_ballot_precincts/Sept23rd2019'
sgid_addrspnts = 'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.LOCATION.AddressPoints'
sgid_vista_boundaries = 'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.POLITICAL.VistaBallotAreas'
sgid_census_place_names = 'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.DEMOGRAPHIC.UnIncorpAreas2010_Approx'

#: Create date variables.
now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour
min = now.minute
formatted_date = str(year) + str(month) + str(day)
#arcpy.env.overwriteOutput = True


#: Worker function.
def do_work_and_save_as_csv(county_id):

    #: get the countyname from the county number
    county_name = get_countyname(county_id)
    county_name.strip()

    # create a new file geodatabase with today's date
    print "Create the file geodatabase for " + county_name
    arcpy.CreateFileGDB_management("D:/vista/agrc_addrpnts_with_vista_ballot_precincts/Sept23rd2019", county_name + "_" + formatted_date + ".gdb", "9.2")  ### use this var: local_vista_directory
    arcpy.env.workspace = "D:/vista/agrc_addrpnts_with_vista_ballot_precincts/Sept23rd2019/" + county_name + "_" + formatted_date + ".gdb"  ### use this var: local_vista_directory
    local_workspace = "D:/vista/agrc_addrpnts_with_vista_ballot_precincts/Sept23rd2019/" + county_name + "_" + formatted_date + ".gdb"  ### use this var: local_vista_directory

    # import the sgid address points for the desired counties (using where clause)
    # to run multiple counties use a where clause like this: 'CountyID = 49057, 49035, 49043' 
    county_where_clause = 'CountyID = ' + str(county_id)
    print "Import the Address Points into fgdb with the where clause: " + county_where_clause
    arcpy.FeatureClassToFeatureClass_conversion(sgid_addrspnts, local_workspace, "sgid_addrpnts", county_where_clause)

    # add the vista precincts to the address points
    print "Run Identity with vista boundaries"
    arcpy.Identity_analysis("sgid_addrpnts", sgid_vista_boundaries, "sgid_addrpnts_vista")

    # add the place name to the address points
    print "Run Identity with census place names" 
    arcpy.Identity_analysis("sgid_addrpnts_vista", sgid_census_place_names, "sgid_addrpnts_vista_placenames")

    # # add field to create the address name field (Street Name + Street Suffix)
    # print "Add StreetName + StreetSuffix field"
    # arcpy.AddField_management("sgid_addrpnts_vista_placenames", "StreetNameStreetSuffx", "TEXT", "", "", 50)

    # # calculate over street name and street suffix to the new field
    # print "Begin calculating street name and street suffix values to the new field"
    # arcpy.CalculateField_management(in_table="sgid_addrpnts_vista_placenames", field="StreetNameStreetSuffx", expression="combineValues( !StreetName!, !SuffixDir!)", expression_type="PYTHON_9.3", code_block="""def combineValues(streetname, streetsuffix):\n   fullname = streetname\n   if len(streetsuffix) > 0:\n      fullname = fullname + " " + streetsuffix\n   return fullname\n""")

    # add the value "Unincorporated" when there is no City value
    print "Begin adding the value Unincorporated when there is no City value"
    arcpy.CalculateField_management(in_table="sgid_addrpnts_vista_placenames", field="City", expression="addUnincorporated( !City! )", expression_type="PYTHON_9.3", code_block="""def addUnincorporated(city):\n   if city == "":\n      city = "Unincorporated"\n   return city\n""")

    # export to table and rename and remove fields
    print "Export the feature class to table"
    # arcpy.TableToTable_conversion(in_rows="sgid_addrpnts_vista_placenames", out_path="D:/vista/agrc_addrpnts_with_vista_ballot_precincts/SgidPntsVistaPcts_2019719.gdb", out_name="table_for_export", where_clause="", field_mapping="""HouseNumber "Address Number" true true false 10 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,AddNum,-1,-1;PrefixDir "Prefix Direction" true true false 1 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,PrefixDir,-1,-1;StreetType "Street Type" true true false 4 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,StreetType,-1,-1;UnitType "Unit Type" true true false 20 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,UnitType,-1,-1;UnitID "Unit ID" true true false 20 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,UnitID,-1,-1;City "City" true true false 30 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,City,-1,-1;Zip "Zip Code" true true false 5 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,ZipCode,-1,-1;AddressType "Point Type" true true false 15 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,PtType,-1,-1;CountyID "CountyID" true true false 2 Short 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,CountyID_1,-1,-1;Precinct "Precinct" true true false 6 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,PrecinctID,-1,-1;SubPrecinct "SubPrecinct" true true false 4 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,SubPrecinctID,-1,-1;Placename "pop_place" true true false 50 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,PLACENAME,-1,-1;StreetName "StreetName" true true false 50 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,StreetNameStreetSuffx,-1,-1""", config_keyword="")
    arcpy.TableToTable_conversion("sgid_addrpnts_vista_placenames", local_workspace, "table_for_export")

    # remove a few fields in the table
    print "Remove a few fields in the table"
    arcpy.DeleteField_management("table_for_export", ["FID_sgid_addrpnts_vista", "FID_sgid_addrpnts", "AddSystem", "UTAddPtID", "FullAdd", "AddNumSuffix", "LandmarkName", "Building", "CountyID", "State", "PtLocation", "Structure", "ParcelID", "AddSource", "LoadDate", "USNG", "FID_VistaBallotAreas", "VistaID", "VersionNbr", "EffectiveDate", "AliasName", "Comments", "RcvdDate", "FID_UnIncorpAreas2010_Approx", "CountyNbr"])

    # upgrade geodatabase to 10.0 or greater (to allow for the alter field tool to run)
    print "Upgrading geodatbase so we can run .AlterField tool - which requires newer fgdb"
    arcpy.UpgradeGDB_management(local_workspace, input_prerequisite_check="PREREQUISITE_CHECK", input_upgradegdb_check="UPGRADE")

    # rename a few field names in the table
    print "Rename a few field names in the table"
    arcpy.AlterField_management("table_for_export", 'AddNum', 'HouseNumber')
    # arcpy.AlterField_management("table_for_export", 'StreetNameStreetSuffx', 'StreetName', 'StreetName')
    arcpy.AlterField_management("table_for_export", 'ZipCode', 'Zip', 'Zip')
    arcpy.AlterField_management("table_for_export", 'CountyID_1', 'CountyID', 'CountyID')
    arcpy.AlterField_management("table_for_export", 'PrecinctID', 'Precinct', 'Precinct')
    arcpy.AlterField_management("table_for_export", 'SubPrecinctID', 'SubPrecinct', 'SubPrecinct')
    arcpy.AlterField_management("table_for_export", 'PLACENAME', 'CensusPlace', 'CensusPlace')

    # export the table to a text file
    print "export table to text file"
    # this method seems to give all OIDs a -1 value: arcpy.TableToTable_conversion(local_workspace + "/table_for_export", r"D:\vista\agrc_addrpnts_with_vista_ballot_precincts", "SGIDAddrPntsVistaPcts" + formatted_date + ".csv")

    input_fct = local_workspace + "/table_for_export"
    output_csv = "D:/vista/agrc_addrpnts_with_vista_ballot_precincts/Sept23rd2019/" + county_name + "_" + formatted_date + ".csv"  ### use this var: local_vista_directory
    csv_delimiter = ","

    fld_list = arcpy.ListFields(input_fct)
    fld_names = [fld.name for fld in fld_list]

    # Open the CSV file and write out field names and data
    with open(output_csv, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=csv_delimiter)
        writer.writerow(fld_names)
        
        with arcpy.da.SearchCursor(input_fct, fld_names) as cursor:
            for row in cursor:
                writer.writerow(row)
        csv_file.close()


#: Pass in county number and get county name (used for final text file names).
def get_countyname(county_number):
    county_name = ''

    if county_number == 49039:
        county_name = 'SANPETE'
    if county_number == 49021:
        county_name = 'IRON'
    if county_number == 49025:
        county_name = 'KANE'
    if county_number == 49057:
        county_name = 'WEBER'
    if county_number == 49037:
        county_name = 'SAN_JUAN'
    if county_number == 49017:
        county_name = 'GARFIELD'
    if county_number == 49033:
        county_name = 'RICH'
    if county_number == 49043:
        county_name = 'SUMMIT'
    if county_number == 49045:
        county_name = 'TOOELE'
    if county_number == 49001:
        county_name = 'BEAVER'
    if county_number == 49003:
        county_name = 'BOX_ELDER'
    if county_number == 49005:
        county_name = 'CACHE'
    if county_number == 49047:
        county_name = 'UINTAH'
    if county_number == 49019:
        county_name = 'GRAND'
    if county_number == 49053:
        county_name = 'WASHINGTON'
    if county_number == 49027:
        county_name = 'MILLARD'
    if county_number == 49051:
        county_name = 'WASATCH'
    if county_number == 49023:
        county_name = 'JUAB'
    if county_number == 49049:
        county_name = 'UTAH'
    if county_number == 49013:
        county_name = 'DUCHESNE'
    if county_number == 49009:
        county_name = 'DAGGETT'
    if county_number == 49031:
        county_name = 'PIUTE'
    if county_number == 49011:
        county_name = 'DAVIS'
    if county_number == 49029:
        county_name = 'MORGAN'
    if county_number == 49055:
        county_name = 'WAYNE'
    if county_number == 49015:
        county_name = 'EMERY'
    if county_number == 49041:
        county_name = 'SEVIER'
    if county_number == 49007:
        county_name = 'CARBON'
    if county_number == 49035:
        county_name = 'SALT_LAKE'

    if county_name == '':
        return "NotFound"
    else:
        return county_name


#: Main function.
if __name__ == "__main__":
    try:
        #: Get a list of county numbers to run this project with. 
        #: (The following three lines contain all the State's county numbers.  I ran them in three batches but they ran fast enough that they can be run together.)
        #county_list = [49039,49021,49025,49057,49037,49017,49033,49043,49045]
        #county_list = [49001,49003,49005,49047,49019,49053,49027,49051,49023]
        county_list = [49049,49013,49009,49031,49011,49029,49055,49015,49041,49007,49035]

        #: Loop through desired counties and create output text files.
        for county in county_list:
            do_work_and_save_as_csv(county)

        print("Done creating csv files for the following counties: " + str(county_list))

    except Exception:
        e = sys.exc_info()[1]
        print str(e.args[0])
        print str(arcpy.GetMessages(2))
        file.write("\n" + "ERROR MESSAGE from sys.exe_info: " + e.args[0]+ "\n")
        file.write("\n" + "ERROR MESSAGE from arcpy.GetMessages(2): " + arcpy.GetMessages(2))
        file.close()
        #log_file.write('An exception has occured - %s' % e)