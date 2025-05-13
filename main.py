import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
st.header("AOD Data for Turlock, Sacramento, Modesto, and Fresno")

# Date Input for selecting start and end dates
start_date = st.date_input("Start Date", datetime.date(2024, 5, 1))
end_date = st.date_input("End Date", datetime.date(2024, 5, 8))

# Convert selected dates to datetime objects
StartDateTime = datetime.datetime.combine(start_date, datetime.time(0, 0))
EndDateTime = datetime.datetime.combine(end_date, datetime.time(23, 59))

# Allow the user to set y-axis limits
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# Input GitHub URL for the repositories
file_urls = [
    "https://raw.githubusercontent.com/Rsaltos7/SacromentoAOD/refs/heads/main/20240101_20241231_Sacramento_River.lev15",
    "https://raw.githubusercontent.com/Rsaltos7/ModestoAOD/refs/heads/main/20240101_20241231_Modesto.lev15",
    "https://raw.githubusercontent.com/Rsaltos7/FresnoAOD/refs/heads/main/20240101_20241231_Fresno_2.lev15",
    "https://raw.githubusercontent.com/Rsaltos7/TurlockAOD2024/refs/heads/main/20240101_20241231_Turlock_CA_USA.lev15"
]

# Function to load data from the given URL
def load_data(file_url):
    try:
        # Read the data from the provided GitHub raw URL
        df = pd.read_csv(file_url, skiprows=6, parse_dates={'datetime': [0, 1]})
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)
        return df
    except Exception as e:
        st.error(f"Failed to process the file from {file_url}: {e}")
        return None

# Load data from all the files
dfs = []
for url in file_urls:
    df = load_data(url)
    if df is not None:
        dfs.append(df)

# Ensure data is loaded and columns are correct
if len(dfs) > 0:
    # Plot AOD values for each site (Turlock, Sacramento, Modesto, Fresno)
    colors = ['b', 'g', 'r', 'purple']
    labels = ['Sacramento', 'Modesto', 'Fresno', 'Turlock']
    
    plt.figure(figsize=(10, 6))
    for idx, df in enumerate(dfs):
        if 'AOD_500nm' in df.columns:
            plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), 
                     color=colors[idx], label=labels[idx])

    # Format the plot
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.ylim(AOD_min, AOD_max)
    plt.legend()
    plt.title("AOD Values at 500nm for Turlock, Sacramento, Modesto, and Fresno")
    st.pyplot(plt.gcf())
