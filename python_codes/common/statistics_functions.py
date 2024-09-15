# Functions to get statistics on stations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# Create a df in ipynb
# operation_path = '/Users/mahlia/Desktop/SeineProject/hydrobiology/python/operations/operations_clipped.csv'
# df = pd.read_csv(operation_path,  sep=',')
# field_date = DateDebutOperationPrelBio
# field_id_station= CdStationMesureEauxSurface

def process_df(df, field_id_station, field_date, coord_x, coord_y):
    # fill with NaN if maths are impossible (no mean or no std)

    df[field_date] = pd.to_datetime(df[field_date]).dt.date
    # Keep geometry fields for Qgis and get list of dates
    grouped_df = df.groupby(field_id_station).agg({
        coord_x: 'first',
        coord_y: 'first',
        field_date: list
    }).reset_index()
    # Remove date duplicates
    grouped_df[field_date] = grouped_df[field_date].apply(lambda dates: list(set(dates)))
    # Convert date in months value
    grouped_df['DateInMonths'] = grouped_df[field_date].apply(lambda dates: [round(date.year * 12 + date.month + date.day/30.0, 2) for date in dates]) # a modifier pour utiliser directement datetime
    # Order dates so difference can be computed
    grouped_df['DateInMonths'] = grouped_df['DateInMonths'].apply(lambda x: sorted(x))
    # Calculate difference between two successive dates, rounding with 2 numbers so != 0
    grouped_df['MonthIntervals'] = grouped_df['DateInMonths'].apply(lambda months: [round(months[i + 1] - months[i],2) for i in range(len(months) - 1)])
    # Calculate Mean and Std on intervals
    grouped_df['MonthIntMean'] = grouped_df['MonthIntervals'].apply(lambda intervals: pd.Series(intervals).mean())
    grouped_df['MonthIntStd'] = grouped_df['MonthIntervals'].apply(lambda intervals: pd.Series(intervals).std())

    return grouped_df


def station_hist(df_list, type_data):
    
    fig, ax = plt.subplots(2,2, figsize= (12,10))

    # Measurements distribution over stations
    for i, df in enumerate(df_list):
        ax[i,0] = df["DateInMonths"].apply(len).hist(ax=ax[i,0], bins=max(df["DateInMonths"].apply(len)), grid=False, rwidth=0.8)
    
        total_count = df["DateInMonths"].apply(len).sum() # without duplicates
        ax[i,0].text(0.95, 0.95, f'Daily Measurements: {total_count}', horizontalalignment='right', verticalalignment='top', transform=ax[i,0].transAxes, bbox=dict(facecolor='white', alpha=0.5))

        # Month Interval distribution over stations
        if i==0: 
            custom_bins = [i for i in range(0,66,6)]
            df = df.loc[df['MonthIntStd'].notna()]
            ax[i,0].set_title(f'Measurements')
            ax[i,1].set_title(f'Average Months Interval (at least 3 measurements)')
        else: 
            custom_bins = [i for i in range(0,30,6)]
            ax[i,1].set_xlabel('Average Months Interval Between Measurements')
            ax[i,0].set_xlabel('Number of Measurements')

        ax[i,1] = df["MonthIntMean"].hist(ax=ax[i,1], bins=custom_bins, grid=False, rwidth=0.8)
        ax[i,1].set_xticks(custom_bins)

        total_count = df.shape[0]
        ax[i,1].text(0.95, 0.95, f'Total Stations: {total_count}', horizontalalignment='right', verticalalignment='top', transform=ax[i,1].transAxes, bbox=dict(facecolor='white', alpha=0.5))

        fig.supylabel('Number of Stations')
        fig.suptitle(f"Distributions over {type_data} stations - 1980-2019", fontsize=16, y=0.97)
        fig.text(0.44, 0.92, 'All stations', va='center', rotation='horizontal', fontsize=14)
        fig.text(0.4, 0.48, '\nMost frequent stations\n', va='center', rotation='horizontal', fontsize=14)
        


def plot_distrib(correl_df:list, type_data):
# Calculate the correlation coefficient and p-value

    fig, ax = plt.subplots(1,2, figsize= (12,5), layout="constrained")

    for i, df in enumerate(correl_df):

        corr_coeff, p_value = pearsonr(df['MonthIntMean'], df['DateInMonths'].apply(len))
        ax[i].scatter(df['MonthIntMean'], df['DateInMonths'].apply(len))
        ax[i].text(0.95, 0.8, f'r = {corr_coeff:.2f}\n', horizontalalignment='right', verticalalignment='bottom', transform=ax[i].transAxes, bbox=dict(facecolor='white', alpha=0.5))

        if i==0:
            # Add a vertical red bar at x=24
            ax[i].axvline(x=24, color='red', linestyle='--', linewidth=2)
            # Add '24' in red on the x-axis
            ax[i].text(24, -4, '24', color='red', ha='center')
            ax[i].set_title('All stations (at least 3 measurements)')

        else: ax[i].set_title('Most frequent stations')

    fig.supxlabel('Average Months Interval')
    fig.supylabel('Number of Measurements')
    fig.suptitle(f"Correlation between Average Month Interval and Number of Measurements over {type_data} stations - 1980-2019")



def stats_per_year(df_list: list, type_data, field_date):

    fig, ax = plt.subplots(1,2, figsize= (12,5), layout="constrained")

    for i, df in enumerate(df_list):

        df[field_date] = pd.to_datetime(df[field_date])
    
        measurements_per_year = df.groupby(df[field_date].dt.year).size()
        # Group years into decades and sum the number of measurements for each decade
        measurements_per_decade = measurements_per_year.groupby((measurements_per_year.index // 10) * 10).sum()
        
        # Create decade ranges
        decade_ranges = [f"{start}-{start+9}" for start in measurements_per_decade.index]
        # Combine decade ranges with corresponding values
        decade_counts = [f"{range_}: {count}" for range_, count in zip(decade_ranges, measurements_per_decade)] #measurements_per_decade[:-1]
        # Join the decade counts into a single string separated by semicolons
        decade_counts_string = "\n".join(decade_counts)

        
        # Plot the histogram
        ax[i].bar(measurements_per_year.index, measurements_per_year.values)
        ax[i].text(0.1, 0.7, decade_counts_string, fontsize=10, transform=ax[i].transAxes)
        
        if i==0:
            ax[i].set_title('All stations (at least 3 measurements)')
        else: ax[i].set_title('Most frequent stations')
        
    fig.supxlabel('Year')
    fig.supylabel('Number of Measurements')
    fig.suptitle(f"Number of {type_data} Measurements per Year - 1980-2019")



def generate_decades(start_year, end_year):
    return list(range((start_year // 10) * 10, (end_year // 10 + 1) * 10, 10))

def stations_per_decade(df, type_data, field_date_start, field_date_end):

    df[field_date_start] = pd.to_datetime(df[field_date_start])
    df[field_date_end] = pd.to_datetime(df[field_date_end])
    df['Decades'] = df.apply(lambda row: generate_decades(row[field_date_start].year, row[field_date_end].year), axis=1)
    df = df.explode('Decades')

    stations_per_decade = df.groupby('Decades').size().reset_index(name='Stations')
    stations_per_decade = stations_per_decade[stations_per_decade['Decades'] <= 2010]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(stations_per_decade['Decades'], stations_per_decade['Stations'], width=8, align='center')
    ax.set_xlabel('Decade')
    ax.set_ylabel('Number of Stations')
    ax.set_title(f'Number of {type_data} stations (at least 3 meas.) per decade')
    ax.set_xticks(stations_per_decade['Decades'])