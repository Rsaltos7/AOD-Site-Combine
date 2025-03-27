import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
st.header = "AOD Data Viewer"

# Dropdown to select site
site_options = ["Turlock CA USA", "Modesto CA USA", "Fresno CA USA"]  # Add your sites here
selected_site = st.selectbox("Select a Site", site_options)

# Start and End Date Inputs
StartDate = st.date_input("Start Date", datetime.date(2024, 5, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("End Date", datetime.date(2024, 5, 8))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Allow the user to set y-axis limits
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# Set file URLs based on the selected site
site_urls = {
    "Turlock CA USA": "https://raw.githubusercontent.com/Rsaltos7/TurlockAOD2024/refs/heads/main/20240101_20241231_Turlock_CA_USA.lev15",
    "Modesto CA USA": "https://raw.githubusercontent.com/YourRepo/ModestoAOD2024/refs/heads/main/20240101_20241231_Modesto_CA_USA.lev15",  # Replace with actual URL
    "Fresno CA USA": "https://raw.githubusercontent.com/YourRepo/FresnoAOD2024/refs/heads/main/20240101_20241231_Fresno_CA_USA.lev15"  # Replace with actual URL
}

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

# Load data for the selected site
file_url = site_urls.get(selected_site, "")
df = None
if file_url:
    df = load_data(file_url)

# Ensure data is loaded and columns are correct
if df is not None:
    if 'AOD_440nm' not in df.columns or 'AOD_500nm' not in df.columns or 'AOD_675nm' not in df.columns:
        st.error(f"Missing expected columns in the dataset. Available columns: {df.columns}")

    # Plot data if columns are correct
    if 'AOD_440nm' in df.columns and 'AOD_500nm' in df.columns and 'AOD_675nm' in df.columns:
        # Plot AOD_440nm, AOD_500nm, and AOD_675nm as initial plot
        plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.k', label="AOD 440nm")
        plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="AOD 500nm")
        plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.r', label="AOD 675nm")

        # Format the plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        plt.title(f"AOD for {selected_site}")  # Dynamically update the title based on selected site
        st.pyplot(plt.gcf())

        # Ask user to match wavelengths to positions
        st.text("\nMatch the wavelengths to the positions on the graph:")
        positions = ["Highest", "Medium", "Lowest"]
        user_matches = {}
        for pos in positions:
            user_matches[pos] = st.selectbox(f"What Wavelength will have the {pos} measurement on the graph?", 
                                             options=["Select an option", "440 nm", "500 nm", "675 nm"], 
                                             key=pos)

        # Once the user submits, show the second graph (same as the first)
        if st.button("Submit"):
            # Plot the second graph (same as the first one)
            plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.b', label="440 nm")
            plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="500 nm")
            plt.plot(df.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.r', label="675 nm")

            # Format the second plot
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
            plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
            plt.gca
