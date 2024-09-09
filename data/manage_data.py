import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

csv_source_path = "data/BOULDER, CO USC00050848.csv"
csv_target_path = "data/GHCND_from_23-01_Boulder_CO.csv"
json_description_path = "data/GHCN-Daily-dict.json"

def load_and_fix_data(source_path, target_path):
    df = pd.read_csv(source_path)

    selected_columns = list(range(1, 12))  # DATE, PRCP, SNOW, TMAX, TMIN, TOBS, WT01, WT03, WT08, WT11, WT16
    df_selected = df.iloc[:, selected_columns]
    print(df_selected)

    df_selected[df_selected.columns[0]] = pd.to_datetime(df_selected[df_selected.columns[0]])
    df_selected = df_selected.sort_values(by=df_selected.columns[0])
    print(df_selected)

    df_selected.to_csv(target_path, index=False)

def generate_description(row):
    date = row['DATE']
    prcp = row['PRCP']
    snow = row['SNOW']
    tmin = row['TMIN']
    tmax = row['TMAX']
    tobs = row['TOBS']
    data_dict = { }
    if not np.isnan(tmin):
        data_dict['min temp'] = f"{tmin} degrees Celsius"
    if not np.isnan(tmax):
        data_dict['max temp'] = f"{tmax} degrees Celsius"
    if not np.isnan(prcp):
        data_dict['rain'] = f"{prcp} mm"
    if not np.isnan(snow):
        data_dict['snowfall'] = f"{snow} mm"
        # 'Temperature': f"{row['TOBS']} °C"
    
    # WT01, WT03, WT08, WT11, WT16
    if not np.isnan(row['WT01']):
        data_dict['fog'] = True
    if not np.isnan(row['WT03']):
        data_dict['thunder'] = True
    if not np.isnan(row['WT08']):
        data_dict['smoke or haze'] = True
    if not np.isnan(row['WT11']):
        data_dict['high or damaging winds'] = True
    date_obj = datetime.strptime(row['DATE'], '%Y-%m-%d')
    formatted_date = date_obj.strftime('%B %d, %Y')
    return { f"Weather on {formatted_date}": f"Weather on {formatted_date} - {data_dict}" }

def get_averages(df):
    year_averages = {}
    monthly_averages = {}
    rain_avg = []
    snow_avg = []
    temp_avg = []
    monthly_days_rain = []
    monthly_days_snow = []
    year_avg = []
    for idx, row in df.iterrows():
        date = row['DATE'] # 2024-09-07
        month = date[:-3]
        year = date[:4]
        if month not in monthly_averages:
            monthly_averages[month] = {'rain': [], 'snow': [], 'temp': [], 'days_rain': 0, 'days_snow': 0}
        if year not in year_averages:
            year_averages[year] = {'rain': [], 'snow': [], 'temp': [], 'days_rain': 0, 'days_snow': 0 }

        if not np.isnan(row['TOBS']):
            monthly_averages[month]['temp'].append(row['TOBS'])
            year_averages[year]['temp'].append(row['TOBS'])

        if not np.isnan(row['PRCP']):
            monthly_averages[month]['rain'].append(row['PRCP'])
            year_averages[year]['rain'].append(row['PRCP'])
            if row['PRCP'] > 0: 
                monthly_averages[month]['days_rain'] += 1
                year_averages[year]['days_rain'] += 1

        if not np.isnan(row['SNOW']):
            monthly_averages[month]['snow'].append(row['SNOW'])
            year_averages[year]['snow'].append(row['SNOW'])
            if row['SNOW'] > 0: 
                monthly_averages[month]['days_snow'] += 1
                year_averages[year]['days_snow'] += 1
        
    for month, avgs in monthly_averages.items():
        date_obj = datetime.strptime(month, '%Y-%m')
        formatted_date = date_obj.strftime('%B, %Y')
        monthly_days_rain.append({f"Number of rainy days {formatted_date}": f"Number of rainy days {formatted_date} = {avgs['days_rain']}"})
        monthly_days_snow.append({f"Number of snowy days {formatted_date}": f"Number of snowy days {formatted_date} = {avgs['days_snow']}"})
        rain_avg.append({f"Month rain average for {formatted_date}": f"Month rain average for {formatted_date} = {round(np.mean(avgs['rain']), 2)} mm"})
        snow_avg.append({f"Month snowfall average for {formatted_date}": f"Month snowfall average for {formatted_date} = {round(np.mean(avgs['snow']), 2)} mm"})
        temp_avg.append({f"Month temp average for {formatted_date}": f"Month temp average for {formatted_date} = {round(np.mean(avgs['temp']), 2)} degrees Celsius"})
    
    for year, avgs in year_averages.items():
        year_avg.append({f"Number of rainy days in {year}": f"Number of rainy days in {year} = {avgs['days_rain']}"})
        year_avg.append({f"Number of snowy days in {year}": f"Number of snowy days in {year} = {avgs['days_snow']}"})
        year_avg.append({f"Average rain in the year {year}": f"Average rain in the year {year} = {round(np.mean(avgs['rain']), 2)} mm"})
        year_avg.append({f"Average snowfall in the year {year}": f"Average snowfall in the year {year} = {round(np.mean(avgs['snow']), 2)} mm"})
        year_avg.append({f"Average temperature in the year {year}": f"Average temperature in the year {year} = {round(np.mean(avgs['temp']), 2)} degrees Celsius"})
    

    return rain_avg, snow_avg, temp_avg, monthly_days_rain, monthly_days_snow, year_avg

def get_csv_descriptions(csv_path, json_path):
    df = pd.read_csv(csv_path)
    results = []

    for idx, row in df.iterrows():
        description = generate_description(row)
        results.append(description)
            # "date": row['DATE'],
            # "description": description
        # })
    avg_rain, avg_snow, avg_temp, monthly_days_rain, monthly_days_snow, year_avg = get_averages(df)
    results = results+ avg_temp + avg_rain + avg_snow  + monthly_days_rain + monthly_days_snow + year_avg
    with open(json_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)

get_csv_descriptions(csv_source_path, json_description_path)

