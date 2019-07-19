import arcpy
from arcpy import env
import datetime
#import arcgisscripting

# get date variables
now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour
min = now.minute
formatted_date = str(year) + str(month) + str(day)

# global variables
sgid_addrspnts = 'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.LOCATION.AddressPoints'
sgid_vista_boundaries = 'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.POLITICAL.VistaBallotAreas'
sgid_census_place_names = 'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.DEMOGRAPHIC.UnIncorpAreas2010_Approx'

# create a new file geodatabase with today's date
print "Create the file geodatabase"
arcpy.CreateFileGDB_management("D:/vista/agrc_addrpnts_with_vista_ballot_precincts", "SgidPntsVistaPcts_" + formatted_date + ".gdb", "9.2")
arcpy.env.workspace = "D:/vista/agrc_addrpnts_with_vista_ballot_precincts/SgidPntsVistaPcts_" + formatted_date + ".gdb"
local_workspace = "D:/vista/agrc_addrpnts_with_vista_ballot_precincts/SgidPntsVistaPcts_" + formatted_date + ".gdb"

# import the sgid address points for the desired counties (using where clause)
county_where_clause = 'CountyID = 49057'
print "Import the Address Points into fgdb with the where clause: " + county_where_clause
arcpy.FeatureClassToFeatureClass_conversion(sgid_addrspnts, local_workspace, "sgid_addrpnts", county_where_clause)

# add the vista precincts to the address points
print "Run Identity with vista boundaries"
arcpy.Identity_analysis("sgid_addrpnts", sgid_vista_boundaries, "sgid_addrpnts_vista")

# add the place name to the address points
print "Run Identity with census place names" 
arcpy.Identity_analysis("sgid_addrpnts_vista", sgid_census_place_names, "sgid_addrpnts_vista_placenames")

# add field to create the address name field (Street Name + Street Suffix)
print "Add StreetName + StreetSuffix field"
arcpy.AddField_management("sgid_addrpnts_vista_placenames", "StreetNameStreetSuffx", "TEXT", "", "", 50)

# calculate over street name and street suffix to the new field
print "Begin calculating street name and street suffix values to the new field"
arcpy.CalculateField_management(in_table="sgid_addrpnts_vista_placenames", field="StreetNameStreetSuffx", expression="combineValues( !StreetName!, !SuffixDir!)", expression_type="PYTHON_9.3", code_block="""def combineValues(streetname, streetsuffix):\n   fullname = streetname\n   if len(streetsuffix) > 0:\n      fullname = fullname + " " + streetsuffix\n   return fullname\n""")

# add the value "Unincorporated" when there is no City value
print "Begin adding the value Unincorporated when there is no City value"
arcpy.CalculateField_management(in_table="sgid_addrpnts_vista_placenames", field="City", expression="addUnincorporated( !City! )", expression_type="PYTHON_9.3", code_block="""def addUnincorporated(city):\n   if city == "":\n      city = "Unincorporated"\n   return city\n""")

# export to table and rename and remove fields
print "export the feature class to a fgdb table"
arcpy.TableToTable_conversion(in_rows="sgid_addrpnts_vista_placenames", out_path="D:/vista/agrc_addrpnts_with_vista_ballot_precincts/SgidPntsVistaPcts_2019719.gdb", out_name="finished_table_for_export", where_clause="", field_mapping="""HouseNumber "Address Number" true true false 10 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,AddNum,-1,-1;PrefixDir "Prefix Direction" true true false 1 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,PrefixDir,-1,-1;StreetType "Street Type" true true false 4 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,StreetType,-1,-1;Building "Building" true true false 75 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,Building,-1,-1;UnitType "Unit Type" true true false 20 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,UnitType,-1,-1;UnitID "Unit ID" true true false 20 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,UnitID,-1,-1;City "City" true true false 30 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,City,-1,-1;Zip "Zip Code" true true false 5 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,ZipCode,-1,-1;AddressType "Point Type" true true false 15 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,PtType,-1,-1;CountyID "CountyID" true true false 2 Short 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,CountyID_1,-1,-1;Precinct "Precinct" true true false 6 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,PrecinctID,-1,-1;SubPrecinct "SubPrecinct" true true false 4 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,SubPrecinctID,-1,-1;CensusPlaceName2010 "pop_place" true true false 50 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,PLACENAME,-1,-1;StreetName "StreetName" true true false 50 Text 0 0 ,First,#,D:\vista\agrc_addrpnts_with_vista_ballot_precincts\SgidPntsVistaPcts_2019719.gdb\sgid_addrpnts_vista_placenames,StreetNameStreetSuffx,-1,-1""", config_keyword="")

# export the table to a text file
print "export table to text file"
arcpy.TableToTable_conversion(local_workspace + "/finished_table_for_export", r"D:\vista\agrc_addrpnts_with_vista_ballot_precincts", "WeberAddrPnts_test.txt")



print "Done!"
