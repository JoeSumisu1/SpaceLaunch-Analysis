from bs4 import BeautifulSoup
import requests
import time
import pandas as pd

def scrape_details(page):
    '''
    description:
        scrapes launch information from single Next Spaceflight details page

    params:
        page number of launch details

    returns:
        a list of data points extracted from details page
    '''

    response = requests.get(url=f'https://nextspaceflight.com/launches/details/{page}')
    details_page = response.text
    soup = BeautifulSoup(details_page, 'html.parser')

    headers = ['mission', 'time', 'location', 'rocket', 'result', 'organization', 'status', 'price', 'liftoff thrust',
            'payload to LEO','Payload to GTO','Stages', 'Strap-ons', 'Rocket Height', 'Fairing Diameter', 'Fairing Height']

    data=[]

    # mission name
    data.append(soup.find(name='h4', class_='mdl-card__title-text').text.strip())

    # launch time/date
    data.append(soup.find(name='span', id='localized').text.strip())

    # location
    data.append(soup.find(string='Location').find_next('h4').get_text())

    # rocket name
    data.append(soup.select('header div div div span')[0].text.strip())

    # failure or success of past missions. Future missions return None
    try:
        data.append(soup.find(name='h6', class_='rcorners status').text.strip())
    except:
        data.append(None)

    # organization name
    table = soup.find_all(name='div', class_='mdl-grid a')[1]
    data.append(table.get_text().strip().split('\n')[0].strip())

    # for data points with consistent labels.
    stats = ['Status:', 'Price', 'Liftoff Thrust', 'Payload to LEO', 'Payload to GTO', 'Stages', 'Strap-ons',
             'Rocket Height', 'Fairing Diameter', 'Fairing Height']
    for stat in stats:
        try:
            data.append(soup.find(string=lambda t: stat in t.text).split(':')[1].strip())
        except:
            data.append(None)
    return data

def scrape_spaceflight():
    '''
    description:
        loops through every mission detail page on Next SpaceFlight and calls scrape_details function to capture data.
        Once 500 consecutive missing pages are detected, loop breaks.

    returns:
        A list of lists, each representing a single mission on a row.
    '''
    consecutive_fails = 0
    page = 0
    df = []
    while consecutive_fails < 500:
        if page % 250 == 0:
            print(f'parsed {page} pages')
        try:
            df.append(scrape_details(page))
            page += 1
            consecutive_fails = 0
        except:
            page += 1
            consecutive_fails += 1
    return df

def create_csv(file_name):
    '''
    description:
        creates a csv document of scraped data
    params:
        file name and path(optional). If no path given, file will be saved in current working directory.
        File name must have .csv extension
    '''
    df = pd.DataFrame(scrape_spaceflight(), columns=['mission', 'time', 'location', 'rocket', 'result', 'organization',
                                                     'status', 'price', 'liftoff thrust', 'payload to LEO','Payload to GTO',
                                                     'Stages', 'Strap-ons', 'Rocket Height', 'Fairing Diameter', 'Fairing Height'])
    df.to_csv(file_name)

# to check how long code takes to run. Took ~30 min to execute
# start_time = time.time()
# create_csv('nextSpaceFlightData.csv')
# execution_length = time.time()-start_time
# print(execution_length)