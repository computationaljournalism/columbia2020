''' utility functions for scraping
''' 

import os
from datetime import datetime
import requests

def get_folder_name(directory_name):
    ''' get the folder name with YYYY-MM-DD as prefix
        pass in the directory name: source, data, freepress
        and this function will return a string (folder name) as:
        YYYY-MM-DD/directory_name

        e.g.:
        2020-04-13/source
        2020-04-13/data
        2020-04-13/freepress
        
    '''
    
#    now = datetime.utcnow()
    now = datetime.now()
    folder_name = f'data/{now.strftime("%Y-%m-%d")}/{directory_name}'
    return folder_name

def get_file_name(file_name):
    ''' prefix the file name with HHMMSS
    '''
#    now = datetime.utcnow()
    now = datetime.now()
    return f'{now.strftime("%H%M%S")}_{file_name}'

def _save_data_file(folder_name, file_name, file_data):
    ''' 
    '''
    # does the folder exist? if not, create it
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)

    file_name_with_time_prefix = get_file_name(file_name)
    
    file_name_with_folder = f'{folder_name}/{file_name_with_time_prefix}'
    print(f'saving source file data to {file_name_with_folder}')
    
    # open the file so that we can "write" to it
    print(type(file_data))

    write_flags = 'w'
    if isinstance(file_data, bytes):
        # if the data is a bytes object, we need to open the file as 'wb'
        write_flags = 'wb'

    with open(file_name_with_folder, write_flags) as data_file:
        data_file.write(file_data)

def save_freepress_file(file_name, file_data):
    ''' create the "freepress" directory and save the file_data
    '''
    folder_name = get_folder_name("freepress")
    _save_data_file(folder_name, file_name, file_data)

def save_source_file(file_name, file_data):
    ''' create the "source" directory and save the file_data
    '''
    folder_name = get_folder_name("source")
    _save_data_file(folder_name, file_name,file_data)
    
def save_data_file(file_name, file_data):
    ''' like "save_source_file", create the "data" directory and save your csv to it
        **notice the duplicate code in here and save_source_file() - there are ways we can clean this up**
    '''
    folder_name = get_folder_name("data")
    _save_data_file(folder_name, file_name,file_data)
    
def fetch_and_save(url, file_name):
    ''' fetch the URL and save it to a file
    '''
    
    # TODO: this needs a bunch of error checking & logging

    # fetch the data from the url
    print(f'fetching {url}...')
    response = requests.get(url)
    print(response.headers)
    
    # save the text (HTML, JSON, etc) to our "source" directory
    if response.headers.get('Content-Type') in ['application/pdf']:
        # if it's of type pdf, we need to save response.content
        # TODO: there are prob other content-types (images) that should use this too
        save_source_file(file_name, response.content)
    else:
        save_source_file(file_name, response.text)

    # return the response object
    return response
