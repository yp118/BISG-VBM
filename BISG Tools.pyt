import arcpy
import os
import re

class Toolbox(object):
    def __init__(self):
        self.label = "BISG Tools"
        self.alias = "BISG_Tools"

        # List of tool classes associated with this toolbox
        self.tools = [Address_Cleaner]

class Address_Cleaner(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Address Cleaner"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        workspace = arcpy.Parameter(
            displayName = "Geodatabase",
            name = "gdb",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")

        workspace.defaultEnvironmentName = "workspace"

        param1 = arcpy.Parameter(
            displayName = "Input Feature",
            name = "in_feature",
            datatype = "GPTableView",
            parameterType = "Required",
            direction = "Input"
            )

        param2 = arcpy.Parameter(
            displayName = "Street Address",
            name = "street_address",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param2.parameterDependencies = [param1.name]
        param2.filter.list = ["Text"]

        param3 = arcpy.Parameter(
            displayName = "Suite/Floor/Apt/Unit Information",
            name = "street2",
            datatype = "Field",
            parameterType = "Optional",
            direction = "Input"
            )

        param3.parameterDependencies = [param1.name]
        param3.filter.list = ["Text"]

        param4 = arcpy.Parameter(
            displayName = "Postal Code",
            name = "zip",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param4.parameterDependencies = [param1.name]
        param4.filter.list = ["Text", "Short", "Long"]

        param5 = arcpy.Parameter(
            displayName = "Clean Address",
            name = "Clean_Address",
            datatype = "Field",
            parameterType = "Derived",
            direction = "Output")

        param6 = arcpy.Parameter(
            displayName = "Clean Zip",
            name = "Clean_Zip",
            datatype = "Field",
            parameterType = "Derived",
            direction = "Output")

        param7 = arcpy.Parameter(
            displayName = "GEOCODE Table",
            name = "geocode_table",
            datatype = "DETable",
            parameterType = "Derived",
            direction = "Output")

        param8 = arcpy.Parameter(
            displayName = "FLAGGED Table",
            name = "flagged_table",
            datatype = "DETable",
            parameterType = "Derived",
            direction = "Output")

        params = [workspace, param1, param2, param3, param4, param5, param6, param7, param8]
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):        
        return

    def updateMessages(self, parameters):
        # Check to see if Street Address and Suite Information are the same field. 
        if parameters[3].value:
            p2 = parameters[2].valueAsText
            p3 = parameters[3].valueAsText
            if p2 == p3:
                parameters[3].setErrorMessage(
                    "Street Address and Suite Information inputs cannot have the same field. "
                    "If Suite Information field does not exist, leave this parameter blank.")
            else:
                parameters[3].setWarningMessage(
                    "This field will be altered permanently. This cannot be undone. If the original contents of "
                    "the field need to be preserved, create a copy of the field before cleaning addresses.")     

        if parameters[4].value:
            p2 = parameters[2].valueAsText
            p3 = parameters[3].valueAsText
            p4 = parameters[4].valueAsText

            if p4 == p3 or p4 == p2:
                parameters[4].setErrorMessage(
                    "The Postal Code field must be different from Street Address and Suite Information "
                    "fields. Addresses cannot be cleaned if information is not parsed into separate fields.")

        if parameters[1].value:
            lst = arcpy.ListFields(parameters[1].valueAsText)
            for f in lst:
                if f.name == "Clean_Address" or f.name == "Clean_Zip5":
                    parameters[1].setErrorMessage(
                        parameters[1].valueAsText + ' includes fields named "Clean_Address" and/or "Clean_Zip5". '
                        'Please delete these fields or change their name before cleanining addresses as fields with '
                        'these names will be added to the table after running the code.')
                    break

            tblgcd = parameters[1].valueAsText + "_GEOCODE"
            tblflg = parameters[1].valueAsText + "_FLAGGED"
            arcpy.env.workspace = parameters[0].valueAsText
            if arcpy.Exists(tblgcd) or arcpy.Exists(tblflg):
                parameters[1].setErrorMessage(
                    "This table appears to be cleaned in geodatabase already."
                    "To continue geocoding, please rename/remove " + tblgcd + " and/or " + tblflg + " tables from "
                    "the Geodatabase or change the Geodatabase above.")


        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #   IMPORTING MODULES
        import arcpy
        import re

        #   UPDATING GEODATABASE LOCATION
        arcpy.env.workspace = parameters[0].valueAsText

        #   INPUT PARAMETERS
        #           fc  = FEATURE CLASS INPUT
        #   ADDRESS_in  = NAME OF FIELD WITH ADDRESS INFORMATION IN fc
        #       ZIP_in  = NAME OF FIELD WITH ZIPCODE INFORMATION IN fc
        #
        #   ***THIS SCRIPT ASSUMES ADDRESS INFORMATION HAS BEEN PARSED***

        fc = parameters[1].valueAsText    
        ADDRESS_in = parameters[2].valueAsText     
        ZIP_in = parameters[4].valueAsText
        ADDRESS_in2 = parameters[3].valueAsText

        ########################################################################################################
        ########################################################################################################

        #   SETTING NAMES OF NEW FIELDS FOR CLEAN ADDRESS INFORMATION   
        Clean_Address = "Clean_Address"
        Clean_Zip5 = "Clean_Zip5"

        #   CREATING NEW FIELDS FOR CLEAN ADDRESS IN THE INPUT FEATURE CLASS
        #   FIELDS ARE SET TO TYPE STRING
        arcpy.AddField_management(fc, Clean_Address, "TEXT")
        arcpy.AddField_management(fc, Clean_Zip5, "TEXT")
        arcpy.AddField_management(fc, "WORKS", "TEXT")

        #   SETTING NAMES FOR OUTPUT TABLES
        #               out_geo     = TABLE NAME FOR ADDRESSES READY FOR GEOCODE
        #           out_flagged     = TABLE NAME FOR FLAGGED ADDRESSES
        out_geo = fc + "_GEOCODE"
        out_flagged = fc + "_FLAGGED"

        #   CREATING LIST OF FIELD NAMES TO BE USED IN CURSOR
        #   THE LAST FIELD - "WORKS" - IS A TEMPORARY FIELD THAT IS USED TO STORE INFORMATION ON IF ADDRESS IS
        #   OK TO GEOCODE. THIS FIELD WILL BE USED IN A SQL QUERY TO CREATE THE TWO OUTPUT TABLES.
        fields_raw = (ADDRESS_in, ADDRESS_in2, ZIP_in, Clean_Address, Clean_Zip5, "WORKS")


        ########################################################################################################
        ########################################################################################################
        ########################################################################################################
        ########################################################################################################


        #   DEFINING PROGRAM VARIABLES, FUNCTIONS, AND EXPRESSIONS
        #   VARIABLE, REGEXES, FUNCTION, SQL DEFINITIONS:
        #                     symbls    = VARIABLES FOR SYMBOLS TO BE REMOVED FROM ADDRESS.
        #                     flInfo    = REGEX PATTERN TO FIND FLOOR INFORMATION IN ADDRESS.
        #                    isPOBox    = REGEX PATTERN TO CHECK IF ADDRESS IS A PO BOX.
        #               firstNoDigit    = REGEX PATTERN TO CHECK IF FIRST CHARACTER IN ADDRESS IS A DIGIT.
        #                    goodZip    = REGEX PATTERN TO CHECK IF ZIP CODE IS 5 DIGITS ONLY. 
        #                      words    = VARIABLE DEFINING LIST OF KEY WORDS AND ABBREVIATIONS IN ADDRESS THAT 
        #                                 NEED TO BE REMOVED.
        #                    numWrit    = WRITTEN FORM OF NUMBERS ONE THROUGH TEN. THESE NUMBERS WILL BE
        #                                 CONVERTED TO NUMERICS IF THEY ARE IN THE BEGINING OF AN ADDRESS.
        #                   numNumer    = NUMERICAL FORM OF NUMBERS ONE THROUGH TEN. THESE NUMBERS WILL
        #                                 REPLACE THEIR RESPECTIVE WRITTEN FORM NUMBERS IF THEY ARE IN THE 
        #                                 BEGINING OF A SENTENCE. 
        #                      types    = VARIABLE DEFINING LIST OF KEY STREET TYPES WRITTEN IN LONG FORM. IF FOUND
        #                                 THESE WILL BE REPLACED WITH THEIR RESPECTIVE ABBREVIATIONS.
        #                 typesAbbrv    = VARIABLE DEFINING LIST OF STREET TYPE ABBREVIATIONS THAT WILL BE USED TO 
        #                                 REPLACE LONG FORM STREET TYPES IF FOUND.
        #                   poundNum    = CLASS RETURNING RESULTS OF REGEX PATTERN SEARCH USED TO FIND SUITE,
        #                                 APARTMENT, AND FLOOR INFORMATION REPRESENTED WITH A "#" FOLLOWED BY
        #                                 A SERIES OF DIGITS.
        #              findWrongWord    = CLASS RETURNING RESULTS OF REGEX PATTERN SEARCH USED TO FIND KEY
        #                                 WORDS AND ABBREVIATIONS IN ADDRESS THAT NEED TO BE REMOVED OR ALTERED.
        #                                 USER INPUTS WORD AND CLASS RETURNS T/F IF FOUND OR NOT FOUND.     
        #           where_clause_geo    = SQL EXPRESSION TO VERIFY THE TEMPORARY "WORKS" FIELD IS "YES".
        #       where_clause_flagged    = SQL EXPRESSION TO VERIFY THE TEMPORARY "WORKS" FIELD IS "NO".

        #   DEFINING LISTS,VARIBLES, AND REGEXES
        arcpy.AddMessage("Compiling RegExes...")
        symbls = r"[!@$:#\\^]"
        flInfo = re.compile(r"([\d]?[\d]?[\d][\s]?[\s]?((ST)|(ND)|(RD)|(TH))?[\s][\s]?(FL((OOR)|(\s)|($))))")
        isPOBox = re.compile(r"P\.?\s?O\.?(\s{1,2})?((BOX)|(BX))")
        firstNoDigit = re.compile(r"^\D.*$")
        goodZip = re.compile(r"^\d{5}$")
        words = (
            "SUITE", 
            "STE", 
            "APARTMENT", 
            "APT",
            "UNIT",
            "FLOOR",
            "FL",
            "BSMT",
            "BLDG",
            "DEPT",
            "FRNT",
            "HNGR",
            "LBBY",
            "LOWR",
            "OFC",
            "PH",
            "TRLR",
            "UPPR",
            "STUDIO",
            "LEVEL"
            )
        numWrit = (
            "ONE",
            "TWO",
            "THREE",
            "FOUR",
            "FIVE", 
            "SIX",
            "SEVEN",
            "EIGHT",
            "NINE",
            "TEN",
            )
        numNumer = (
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            )
        types = (
            "AVENUE",
            "ROAD",
            "BOULEVARD",
            "COURTS",
            "DRIVE",
            "ROUTE",
            "JUNCTION",
            "HIGHWAY",
            "STREET",
            "TRAIL",
            "PARKWAY",
            "CIRCLE",
            "CENTER",
            "LANE"
            )
        typesAbbrv = (
            "AVE",
            "RD",
            "BLVD",
            "CTS",
            "DR",
            "RT",
            "JCT",
            "HWY",
            "ST",
            "TRL",
            "PKWY",
            "CIR",
            "CTR",
            "LN"
            )

        #   DEFINING FUNCTIONS
        def poundNum(w):
            return re.compile(r'\s({0})[0-9]'.format(w),).search
        def findWrongWord(w):
            return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

        #   DEFINING SQL QUERIES
        where_clause_geo = " \"WORKS\" = 'YES' "
        where_clause_flagged = " \"WORKS\" = 'NO' "


        ########################################################################################################
        ########################################################################################################
        ########################################################################################################
        ########################################################################################################


        #   CREATING A CURSOR TO BE USED TO UPDATE ROWS IN THE ATTRIBUTE TABLE
        arcpy.AddMessage("Cleaning addresses...")
        with arcpy.da.UpdateCursor(fc, fields_raw) as cursor_raw:
            #   THIS FOR LOOP WILL UPDATE THE "Clean_Address" AND "Clean_Zip5" FIELDS. IT WILL ALSO POPULATE THE
            #   "_GEOCODE" AND "_FLAGGED" TABLES WITH THEIR RESPECTIVE ROWS. WHEN READY FOR GEOCODING, USE THE 
            #   "_GEOCODE" TABLE FOR MOST ACCURATE AND EFFICIENT RESULTS.  
            #   
            #   INPUT PARAMETERS:
            #                 row[0]    = ADDRESS_in
            #                 row[1]    = ADDRESS_in2
            #                 row[2]    = ZIP_in
            #                 row[3]    = Clean_Address
            #                 row[4]    = Clean_Zip5
            #                 row[5]    = WORKS (temporary)
            #
            #   KEY VARIABLES:
            #                    addy   = VARIABLE HOLDING AND UPDATING ADDRESS INFORMATION.
            #                   addy2   = VARIABLE HOLDING AND UPDATING ADDRESS LINE 2 INFORMATION IF GIVEN.
            #                   zippy   = VARIABLE HOLDING AND UPDATING ZIPCODE INFORMATION.
            #            flInfo_match   = VARIABLE THAT CHECKS FOR FLOOR INFORMATION IN ADDRESS.
            #           isPOBox_match   = VARIABLE THAT TESTS IF ADDRESS IS A PO BOX.
            #      firstNoDigit_match   = VARIABLE THAT TESTS IF ADDRESS BEGINS WITH DIGIT.
            #           goodZip_match   = VARIABLE THAT TESTS IF ZIP CODE IS ONLY 5 DIGITS. 
            
            for row in cursor_raw:
                #   CREATING VARIABLES TO STORE AND UPDATE VALUES IN FOR LOOP
                addy = row[0]
                if ADDRESS_in2:
                    if row[1] is None:
                        row[1] = ""
                        # cursor_raw.updateRow(row)
                    addy2 = row[1]
                    if addy2 == " ":
                        addy2 = ""

                
                #   UPDATING CLEAN ADDRESS VARIABLE WITH ADDRESS INFORMATION.
                #   TRANSFORMING TO UPPERCASE.
                if addy:
                    addy = addy.upper()
                else:
                    addy = ""

                #   STRIPPING ALL INFORMATION IF PATTERN " #" + [0-9] FOUND.
                #   THE SPACE BEFORE "#" ENSURES THAT ENTIRE ADDRESS IS NOT REMOVED IF ADDRESS STARTS WITH
                #   "#". ALL ADDITIONAL "#" WILL BE REMOVED IN A LATER STEP.
                if poundNum(r"#")(addy):    
                    sep = " #"
                    addy, sep, tail = addy.partition(sep)
                    if ADDRESS_in2:
                        if addy2 == "":
                            addy2 = sep + tail
                            addy2 = addy2.replace(" ", "")

                #   NOTE: WE REMOVE SYMBOLS AFTER CHECKING IF poundNum == True.
                #   THIS IS TO ENSURE WE STRIP ENTIRE SUITE/FLOOR/UNIT INFORMATION IF PRECEEDED BY "#".
                addy = re.sub(symbls, "", addy)
                
                #   THE FOLLOWING CHECKS FOR FLOOR INFORMATION ATTACHED TO THE END OF THE ADDRESS.
                #   EXAMPLE "3RD FLOOR". IF FOUND, THIS INFORMATION IS STRIPPED AND COPIED TO 
                #   ADDRESS_in2 FIELD, IF PROVIDED.
                flInfo_match = re.search(flInfo, addy)
                if flInfo_match is not None:
                    sep = flInfo_match.group(1)
                    addy, sep, tail = addy.partition(sep)
                    if ADDRESS_in2:
                        if addy2 == "":
                            addy2 = sep + tail

                #   THE FOLLOWING LOOP REMOVES COMMON ABBREVIATIONS FOR SUITE/FLOOR/UNIT/APARTMENT
                #   AS WELL AS ALL PROCEEDING TEXT. THIS INFORMATION IS STRIPPED AND COPIED TO
                #   ADDRESS_in2 FIELD, IF PROVIDED.
                for word in words:
                    if findWrongWord(word)(addy):
                        sep = " " + word + " "
                        addy, sep, tail = addy.partition(sep)
                        if ADDRESS_in2:
                            if addy2 == "":
                                sep = sep.replace(" ", "")
                                sep = sep + " "
                                addy2 = sep + tail

                        sep = "," + word
                        addy, sep, tail = addy.partition(sep)           
                        if ADDRESS_in2:
                            if addy2 == "":
                                addy2 = sep + tail
                                addy2 = addy2.replace(",", "")
                                addy2 = addy2.replace(" ", "")

                        sep = "-" + word
                        addy, sep, tail = addy.partition(sep)       
                        if ADDRESS_in2:
                            if addy2 == "":
                                addy2 = sep + tail
                                addy2 = addy2.replace("-", "")
                                addy2 = addy2.replace(" ", "")      
                
                #   COMMAS AND SEMICOLONS ARE TREATED DIFFERENTLY AS THEY COMMONLY ARE USED TO SPLIT
                #   SUIT/FLOOR/UNIT INFORMATION. IF FOUND, WILL REPLACE WITH SPACE, NOT BLANK.  
                addy = re.sub(r"[,;\\.]", " ", addy)
                
                #   THE FOLLOWING LOOP REPLACES WRITTEN NUMBERS WITH NUMERICAL NUMBERS IF THEY ARE IN
                #   THE BEGINING OF AN ADDRESS.
                for i, nums in enumerate(numWrit):
                    if findWrongWord(nums)(addy):
                        sep = nums + " "
                        first_word = addy.split(sep, 1)[0]
                        if first_word == "":
                            addy = addy.split(sep, 1)[-1]
                            addy = numNumer[i] + " " + addy
                
                #   THE FOLLOWING LOOP REPLACES LONG FORM STREET TYPES WITH THE ABBREVIATIONS.
                addy = addy + " "
                for i, typ in enumerate(types):
                    if findWrongWord(typ)(addy):
                        addy = addy.replace(r" "+typ+r" ", r" "+typesAbbrv[i]+r" ")

                #   UPDATING "Clean_Address" AND "ADDRESS_in2" FIELDS
                row[3] = addy
                row[1] = addy2


                ####################################################################################################
                ####################################################################################################
                ####################################################################################################
                ####################################################################################################


                #   THE FOLLOWING SECTION OF THE LOOP FOCUSES ON CLEANING ZIPCODE INFORMATION AND STANDARDIZING IT
                #   TO FIVE DIGIT ZIP CODES. THE "Clean_Zip5" FIELD WILL BE UPDATED.
                #   SETTING zippy TO CURRENT ZIPCODE INFORMATION.
                zippy = str(row[2])

                #   REMOVING SPACES FROM ZIP CODE
                if zippy:
                    zippy = zippy.replace(r" ", "")
                else:
                    zippy = ""
                
                #   STRIPPING ALL INFORMATION IF HYPHEN FOUND.
                #   IF A HYPHEN APPEARS IN THE ZIP CODE, THE HYPHEN AND ALL TEXT TO THE RIGHT OF IT WILL BE REMOVED.
                if re.search(r"-", zippy):
                    sep = "-"
                    zippy, sep, tail = zippy.partition(sep)
                
                #   UPDATING "Clean_Zip5" FIELD. 
                row[4] = zippy
                

                ####################################################################################################
                ####################################################################################################
                ####################################################################################################
                ####################################################################################################


                # PERFORMING TESTS ON CLEANED ADDRESS AND ZIPCODE TO SEE IF RECORD CAN BE GEOCODED.
                isPOBox_match = re.search(isPOBox, addy)
                firstNoDigit_match = re.search(firstNoDigit,addy)
                goodZip_match = re.search(goodZip, zippy)

                #   THE FOLLOWING STATEMENTS ASSIGN THE TEMPORARY "WORKS" FIELD WITH YES/NO AFTER CHEKCING IF THE ADDRESS
                #   IS READY FOR GEOCODING. 
                if addy is None:
                    row[5] = "NO"
                elif isPOBox_match is not None:
                    row[5] = "NO"
                elif firstNoDigit_match is not None:
                    row[5] = "NO"
                elif goodZip_match is None:
                    row[5] = "NO"
                else:
                    row[5] = "YES"

                #   UPDATING INPUT TABLE.
                cursor_raw.updateRow(row)
        del cursor_raw, row

        arcpy.AddMessage("Creating GEOCODE and FLAGGED tables...")
        #   CREATING "_GEOCODE" TABLE FROM RECORDS IN INPUT TABLE THAT ARE READY FOR GEOCODING.
        arcpy.TableSelect_analysis(fc, out_geo, where_clause_geo)
        #   CREATING "_FLAGGED" TABLE FROM RECORDS IN INPUT TABLE THAT CANNOT BE GEOCODED. 
        arcpy.TableSelect_analysis(fc, out_flagged, where_clause_flagged)
        #   DELETING TEMPORARY FIELD.
        arcpy.AddMessage("Deleting temp files...")
        arcpy.DeleteField_management(fc, "WORKS")
        arcpy.DeleteField_management(out_geo, "WORKS")
        arcpy.DeleteField_management(out_flagged, "WORKS")


        return
