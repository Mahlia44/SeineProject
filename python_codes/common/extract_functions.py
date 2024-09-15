# Function to extract data from Naïades using Hub'heau API

# Charging modules
import os
import requests
import pandas as pd
import math
from tqdm.auto import tqdm


# Parametrization to download

# Base URL
BASE = "http://hubeau.eaufrance.fr/api"
# Results per page
PAGE_SIZE = 1000
# Max results per research (fixed by API)
MAX_RESULTS = 20000

# Regions in the Basin
regions = ["27", "44", "11", "28", "24", "32"]
# depart = ["21", "10", "51", "77", "91", "94", "78", "75", "92", "95", "93", "27", "76", "14"]


def parametrization(start_date, end_date, endpoint, operation, regions=regions):

    parameters = [
        {
            "parameter": "date_debut_prelevement",
            "value": start_date
        },
        {
            "parameter": "date_fin_prelevement",
            "value": end_date
        },
        
        {
            "parameter": "size",
            "value": PAGE_SIZE
        },

        {
            "parameter": "code_region",
            "value": ",".join(regions)
        },
        
        {
            "parameter": "code_groupe_parametre",
            "value": ["47"]
        }
    
    ]

    # URL to download data
    parameters = "&".join([f"{param['parameter']}={param['value']}" for param in parameters])
    hubeau_url = f"{BASE}/{endpoint}/{operation}?{parameters}"
    return hubeau_url


def get_response(hubeau_url):
    # Get response from first page
    response = requests.get(hubeau_url)
    # Converting into json type
    response = response.json()
    # Get response and number of results for the research
    return response, response["count"]


def get_data(response, hubeau_url):
    # Get data from first page
    data = response['data']
    # Initialize number of results
    nb_results = PAGE_SIZE

    # Initialize indicator for last page
    last_page = False

    # Get results for next page
    # Stop when last page reached
    while response['next'] is not None and not last_page:
        # URL of ith page of results
        hubeau_url = response['next']

        if (nb_results + PAGE_SIZE) >= MAX_RESULTS:
            # Re parametrize number of results for last page
            hubeau_url = hubeau_url.replace(
                f"size={PAGE_SIZE}", "size={}".format(MAX_RESULTS - nb_results)
            )
            last_page = True

        # Get response for ith page of results
        response = requests.get(hubeau_url)
        response = response.json()
        # Catching error if there is one
        try:
            data += response['data']
        except:
            print("WARNING ERROR", response)
        
        # Increment number of results
        nb_results += PAGE_SIZE

    # Converting into df
    df = pd.DataFrame(data)
    return df



days_in_month = {
    "1":(31),
    "2":(28,59),
    "3":(31,90),
    "4":(30,120),
    "5":(31,151),
    "6":(30,181),
    "7":(31,212),
    "8":(31,243),
    "9":(30,273),
    "10":(31,304),
    "11":(30,334),
    "12":(31,365)
}
days_too_much = []

def export_data(start_year, end_year, start_month, end_month, start_day, end_day, endpoint, operation, days_in_month=days_in_month):
    """ export data for opertions """

    start_date = f"{start_year}-{'0'+str(start_month) if len(str(start_month)) == 1 else start_month}-{'0'+str(start_day) if len(str(start_day)) == 1 else start_day}"
    end_date = f"{end_year}-{'0'+str(end_month) if len(str(end_month)) == 1 else end_month}-{'0'+str(end_day) if len(str(end_day)) == 1 else end_day}"

    hubeau_url = parametrization(start_date=start_date, end_date=end_date, endpoint=endpoint, operation=operation)
    response, n = get_response(hubeau_url=hubeau_url)
    
    if n>=MAX_RESULTS:
        print(f"Too much data ({n}) between {start_date} and {end_date} --> splitting")

        if end_month-start_month<=1 and start_year==end_year: #have to split within a month

            if end_day==start_day and end_month==start_month: #special case within a day, just take 20000 data
                print(f"{start_date} has too much data")
                days_too_much.append(start_date)
                df = pd.DataFrame()
                return df

            else:     
                print("Using mid day...")
                mid_day = start_day + ((end_day+days_in_month[str(end_month)][1])-(start_day+days_in_month[str(start_month)][1]))//2
                print("Mid day", mid_day)
                df1 = export_data(start_year, start_year, start_month, start_month, start_day, mid_day)
                df2 = export_data(start_year, end_year, start_month, end_month, mid_day, end_day)

        else: #have to split within the year
            print("Using mid month...")
            mid_month = start_month + ((end_month+12*end_year)-(start_month+12*start_year))//2
            df1 = export_data(start_year, start_year, start_month=start_month, end_month=mid_month, start_day=start_day, end_day=end_day)
            df2 = export_data(start_year, end_year, start_month=mid_month, end_month=end_month, start_day=start_day, end_day=end_day)

        return pd.concat((df1, df2), axis=0, ignore_index=True)
    
    else: #no need to split
        print(f"Exporting {n} data between {start_date} and {end_date}...")
        df = get_data(response=response, hubeau_url=hubeau_url)
        return df
    


# Exporting stations

def parametrization_stations(endpoint, operation, regions=regions):

    parameters = [
        
        {
            "parameter": "size",
            "value": PAGE_SIZE
        },

        {
            "parameter": "code_region",
            "value": ",".join(regions)
        },
        
        {
            "parameter": "code_groupe_parametre",
            "value": ["47"]
        }
    
    ]

    # URL to download data
    parameters = "&".join([f"{param['parameter']}={param['value']}" for param in parameters])
    hubeau_url = f"{BASE}/{endpoint}/{operation}?{parameters}"
    return hubeau_url


def export_data_station(endpoint, operation):
    """ export data for stations """

    hubeau_url = parametrization_stations(endpoint=endpoint, operation=operation)
    response, n = get_response(hubeau_url=hubeau_url)

    print(f"Number of stations: {n}")

    df = get_data(response=response, hubeau_url=hubeau_url)

    return df