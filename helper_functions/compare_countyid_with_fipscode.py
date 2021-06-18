import arcpy

#: This function compares the Vista CountyId with the Address Point's County FIPS Code ID.
def county_has_discrepency(vista_countyid, addresspnt_fips_countyid):
    countyid_list= create_countyid_list()
    ids_to_validate = str(vista_countyid).strip() + "-" + str(addresspnt_fips_countyid).strip()

    #: Comapre the strings of county IDs.
    if ids_to_validate in countyid_list:
        #: It's in the list, so there is no discrepancy.
        return False
    else:
        #: It's not in the list, so there is a discrepancy.
        return True


#: Create a list with UGRC County ID code and it's corresponding FIPS code.
def create_countyid_list():
    countyid_fipsid = [
    "01-49001",
    "02-49003",
    "03-49005",
    "04-49007",
    "05-49009",
    "06-49011",
    "07-49013",
    "08-49015",
    "09-49017",
    "10-49019",
    "11-49021",
    "12-49023",
    "13-49025",
    "14-49027",
    "15-49029",
    "16-49031",
    "17-49033",
    "18-49035",
    "19-49037",
    "20-49039",
    "21-49041",
    "22-49043",
    "23-49045",
    "24-49047",
    "25-49049",
    "26-49051",
    "27-49053",
    "28-49055",
    "29-49057"]
    return countyid_fipsid