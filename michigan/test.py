''' testing...
''' 

import utils

def main():
    '''  test the fetch_and_save method
    '''
    utils.fetch_and_save('https://resources.bibblio.org/hubfs/share/2018-09-18-RecSysNYC-Diane_Hu.pdf', 'test.pdf')
    utils.fetch_and_save('https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html', 'test.html')
    utils.fetch_and_save('https://api.census.gov/data/2018/acs/acs5/variables/B08128_001E.json', 'test.json')

if __name__ == '__main__':
    main()