# ## Scraping Oakland data

################################
# use utils.py
import sys
sys.path.append("../")
import utils
import sheets
################################

# This code pulls the data on Oakland county corona virus cases by zip code from https://www.oakgov.com/covid/casesByZip.html. The data includes death toll, number of cases and population by zip code area in Oakland

from requests import get
from bs4 import BeautifulSoup
from datetime import datetime

now = datetime.now()

log = open("log.txt","a")
log.write("=================================\n")
log.write("0. "+now.strftime("%Y-%m-%d-%H-%M")+"\n")

#Finding the data from a map in this page https://www.oakgov.com/covid/casesByZip.html. 
#Url3 is the address where the map pulls its data from

url3='https://services1.arcgis.com/GE4Idg9FL97XBa3P/arcgis/rest/services/COVID19_Cases_by_Zip_Code_Total_Population/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Join_Zip_Code%20asc&resultOffset=0&resultRecordCount=200&cacheHint=true'

response = get(url3)
data=response.json()

log.write("1. Pulled JSON\n")

#The data is in the list of dictionaries called 'features'
features=data['features']

#We want to pull all the variables inside the dict called attributes, so we create a new list of dictionaries that only includes the attributes
new_data=[]

for feature in features:
    new_data.append(feature['attributes'])

from pandas import DataFrame

Oakland = DataFrame(new_data)
log.write("2. Created data frame\n")


#### Output ##################
utils.save_source_file("Oakland.json", response.text)
log.write("3. Saved Source file\n")

csv = Oakland.to_csv(index=False)
utils.save_data_file("Oakland.csv", csv)
log.write("4. Saved Data file\n")

fp = Oakland[["Join_Zip_Code","Total__COVID19_Cases","Death_Count","Total_Population_ACS_17_5YR"]].copy(deep=True)

fp.columns=["ZIP code","Cases","Deaths","Population"]
fp.loc[:,"Cases"] = fp["Cases"].astype(float)
fp.loc[:,"Deaths"] = fp["Deaths"].astype(float)
fp.loc[:,"Population"] = fp["Population"].astype(float)
fp.loc[fp["Cases"].isnull(),"Cases"] = 0.0
fp.loc[fp["Deaths"].isnull(),"Deaths"] = 0.0
fp.loc[:,"Cases per 100,000"] = 100000.0*fp["Cases"]/fp["Population"]
log.write("5. Processed Freepress\n")

fpcsv = fp.to_csv(index=False)
utils.save_freepress_file("Oakland.csv", fpcsv)
log.write("6. Saved Freepress\n")
##############################

#### save csv to sheets ######

GOOGLE_SHEET_ID = '1wtkFL6BIZQoLnUVfcr8y_2XyjSzlrPimH6A0lMjtlys'
try:
    # we need to convert the dataframe to a list of lists
    # and then update via google sheets api
    data_to_save = [fp.columns.values.tolist()] + fp.values.tolist() 
    sheets.update_sheet(GOOGLE_SHEET_ID, data_to_save)
    log.write("7. Updated google sheet\n")

except Exception as exc:
    print(exc)
    log.write(f'exception writing to sheet: {exc}')

##############################
