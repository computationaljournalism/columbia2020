''' simple class/wrapper for google sheets api and credentials
'''
import pickle
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.pickle file
SERVICE_ACCOUNT_FILE = 'michigancovid-91b78f619d61.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_credentials():
    ''' get the google/sheets credentials for a service account
    '''
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.

    curr_dir = os.path.dirname(os.path.realpath(__file__))
    token_file_name = f'{curr_dir}/sheets_token.pickle'
    if os.path.exists(token_file_name):
        with open(token_file_name, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            service_account_file_name = f'{curr_dir}/{SERVICE_ACCOUNT_FILE}'
            creds = service_account.Credentials.from_service_account_file(
                   service_account_file_name,
                   scopes=SCOPES
            )
        # Save the credentials for the next run
        with open(token_file_name, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def update_sheet(sheet_id, sheet_name, csv_data):
    ''' pass in a google sheet ID and a list-of-lists
        and this will update (over-write!) the sheet
    '''

    # TODO: dont read the creds in each time we do this...cache it on first read
    creds = get_google_credentials()
    service = build('sheets', 'v4', credentials=creds)

    # clear the sheet before updating it
    # The A1 notation of the values to clear (ie the entire Sheet1)
    # this is a little brittle b/c it has to be named 'Sheet1'
    #range_ = 'Sheet1'
    range_ = sheet_name
    request = service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range=range_,
        body={}
    )
    response = request.execute()

    # now, update Sheet1
    # the body of the payload...we're just passing in a csv (list of lists)
    body = {
        'values': csv_data
    }
    response = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_,
        valueInputOption='RAW',
        body=body).execute()

    print(response)
    
def test():
    ''' simple test method
    '''

    values = []
    file_name = 'oakland_county/data/2020-04-19/freepress/231348_Oakland.csv'
    import csv
    with open(file_name) as data_file:
        csv_reader = csv.reader(data_file)
        for line in csv_reader:
            print(line)
            values.append(line)

    print(values)

    SAMPLE_SPREADSHEET_ID = '13i0HP8f_yVen7aCLXNoarRrxsXIQAHJ6_N1NlfnZRFI'
    sheet_name = 'Sheet1'
    sheet_name = 'Oakland County'
    update_sheet(SAMPLE_SPREADSHEET_ID, sheet_name, values)

#if __name__ == '__main__':
#    test()
