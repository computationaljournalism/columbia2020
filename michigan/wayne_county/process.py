''' Scraping Wayne Count data for the FreePress
'''

################################
# use utils.py
import sys
sys.path.append("../bin")
from datetime import datetime
from requests import get
import pandas as pd
import utils
import sheets
################################

# This code pulls the data on Wayne county corona virus cases via:
# https://www.waynecounty.com/gisserver/rest/services/COVID/COVID_Location/MapServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirms%20desc&resultOffset=0&resultRecordCount=43
# this data relies on city/municipality population, which is currently in city_population.csv

# the google sheet ID and name of the sheet/tab we want to update
GOOGLE_SHEET_ID = '1wtkFL6BIZQoLnUVfcr8y_2XyjSzlrPimH6A0lMjtlys'
GOOGLE_SHEET_NAME = 'Wayne County'

def main():
    ''' run it
    '''
    now = datetime.now()

    log = open("log.txt", "a")
    log.write("=================================\n")
    log.write("0. "+now.strftime("%Y-%m-%d-%H-%M")+"\n")

    # read the local "config" csv file with each city/municipality's display name,
    # name (as mapped to gis data) and 2018 population
    # format of the csv is
    # display name, name in gis data, 2018 population
    city_population_df = pd.read_csv('city_population.csv')

    url = 'https://www.waynecounty.com/gisserver/rest/services/COVID/COVID_Location/MapServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirms%20desc&resultOffset=0&resultRecordCount=43'
    data = {}

    try:
        response = get(url)
        data = response.json()
    except Exception as exc:
        log.write(f'Failed to fetch data via waynecounty.com/gisserver: {exc}')
        return

    log.write("1. Pulled JSON\n")

    # The data is in the list of dictionaries called 'features'
    features = data.get('features')
    if not features:
        log.write('Failed to get "features" from json for wayne county')
        return

    new_data = []
    for feature in features:
        new_data.append(feature.get('attributes'))

    wayne_df = pd.DataFrame(new_data)
    log.write("2. Created data frame\n")

    #### Output ##################
    utils.save_source_file("wayne.json", response.text)
    log.write("3. Saved Source file\n")

    wayce_csv = wayne_df.to_csv(index=False)
    utils.save_data_file("wayne.csv", wayce_csv)
    log.write("4. Saved Data file\n")

    # create a dataframe with the data from arcgis merged with the population csv file
    wayne_df = pd.DataFrame(new_data)
    wayne_full_df = pd.merge(wayne_df, city_population_df, on='Municipality')

    # some cleanup...converting to floats
    wayne_full_df.loc[:, 'Confirms'] = wayne_full_df['Confirms'].astype(float)
    wayne_full_df.loc[:, 'Deaths'] = wayne_full_df['Deaths'].astype(float)
    wayne_full_df.loc[:, '2018 Population'] = wayne_full_df['2018 Population'].str.replace(',', '').astype(float)
    wayne_full_df.loc[wayne_full_df['Confirms'].isnull(), 'Confirms'] = 0.0
    wayne_full_df.loc[wayne_full_df['Deaths'].isnull(), 'Deaths'] = 0.0

    # cases per 1,000
    wayne_full_df['Cases per 1,000 population'] = 1000.0*wayne_full_df['Confirms']/wayne_full_df['2018 Population']

    # save our a few of the columns to a new dataframe and
    # rename the columns to match what the free press would like
    final_df = wayne_full_df[['Display Name', 'Confirms', 'Deaths', 'Cases per 1,000 population', '2018 Population']].copy(deep=True)
    final_df.columns = ['City/Twp.', 'Cases', 'Deaths', 'Cases per 1,000 population', 'Population']

    log.write("5. Processed Freepress\n")

    # save the dataframe to csv
    df_csv = final_df.to_csv(index=False)
    utils.save_freepress_file("wayne.csv", df_csv)
    log.write("6. Saved Freepress\n")
    ##############################

    #### save csv to sheets ######

    try:
        # we need to convert the dataframe to a list of lists
        # and then update via google sheets api
        data_to_save = [final_df.columns.values.tolist()] + final_df.values.tolist()
        sheets.update_sheet(GOOGLE_SHEET_ID, GOOGLE_SHEET_NAME, data_to_save)
        log.write("7. Updated google sheet\n")

    except Exception as exc:
        print(exc)
        log.write(f'exception writing to sheet: {exc}')
        raise exc

    ##############################

if __name__ == '__main__':
    main()
