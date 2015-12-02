# Geocoding using python 

# Import system modules
import arcpy
arcpy.env.workspace = "" 

# Set local variables:
input_feat = ""
# Add paramters for fields
addr =
city = 
state = 
postal =
geocode_result = "geocode_result"

if locator is True:
	address_locator = "Atlanta_AddressLocator"

	# Create string that uses parameters but is passed through Geocoding function
	geocode_string = "Address Address VISIBLE NONE;City CITY VISIBLE NONE;State State VISIBLE NONE;Zip Zip VISIBLE NONE"
	
	arcpy.GeocodeAddresses_geocoding(input_feat, address_locator, "Address Address VISIBLE NONE;City CITY VISIBLE NONE;State State VISIBLE NONE;Zip Zip VISIBLE NONE", geocode_result, "STATIC")

#### Run R script for remaining addresses