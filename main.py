import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

# ------------------------------ CONFIG -------------------------------- #
SampleRate = "1h"
windSampleRate = '3h'

# URLs for each city's AOD data
city_urls = {
    "Turlock": "https://raw.githubusercontent.com/Rsaltos7/TurlockAOD2024/refs/heads/main/20240101_20241231_Turlock_CA_USA.lev15",
    "Sacramento": "https://raw.githubusercontent.com/Rsaltos7/SacromentoAOD/refs/heads/main/20240101_20241231_Sacramento_River.lev15",
    "Modesto": "https://raw.githubusercontent.com/Rsaltos7/ModestoAOD/refs/heads/main/20240101_20241231_Modesto.lev15",
    "Fresno": "https://raw.githubusercontent.com/Rsaltos7/FresnoAOD/refs/heads/main/20240101_20241231_Fresno_2.lev15",
}
windfile = 'https://raw.githubusercontent.com/Rsaltos7/TurlockAOD2024/refs/heads/main/72492623258%20(4).csv'

# ------------------------------ FUNCTIONS ------------------------------ #
def load_aod_data(file_url):
    try:
        df = pd.read_csv(file_url, skiprows=6, parse_dates={'datetime': [0, 1]})
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading AOD data from {file_url}: {e}")
        return None

def load_wind_temp_data(file_url):
    df = pd.read_csv(file_url, parse_dates={'datetime': [1]}, low_memory=False)
    datetime_utc = pd.to_datetime(df["datetime"], format='%d-%m-%Y %H:%M:%S')
    datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df.set_index(datetime_pac, inplace=True)
    return df

def compute_wind_components(df):
    wnd = df['WND'].str.split(',', expand=True)
    wnd = wnd[wnd[4] == '5']  # Valid wind records
    magnitude = wnd[3].astype(float)
    direction = wnd[0].astype(float)
    x = magnitude * np.sin(np.radians(direction))
    y = magnitude * np.cos(np.radians(direction))
    wnd[5], wnd[6] = x, y
    return wnd

# ------------------------------ STREAMLIT UI ------------------------------ #
st.title("AOD, Wind Vectors, and Temperature")
StartDate = st.date_input("Start Date", datetime.date(2024, 5, 1))
EndDate = st.date_input("End Date", datetime.date(2024, 5, 8))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

AOD_min = st.sidebar.slider("Y-Axis Min", 0.0, 1.0, 0.0, 0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", 0.0, 1.0, 0.3, 0.01)

# ------------------------------ LOAD DATA ------------------------------ #
wind_df = load_wind_temp_data(windfile)
wind_components = compute_wind_components(wind_df)
temp_df = wind_df['TMP'].str.split(',', expand=True).replace('+9999', np.nan).astype(float)

# ------------------------------ PLOT ------------------------------ #
fig, ax = plt.subplots(figsize=(16, 9))
fig.autofmt_xdate()
ax.set_title('AOD (500nm), Wind Vectors & Temperature')

# Time formatting
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# Plot AOD for each city
colors = {"Turlock": "black", "Sacramento": "blue", "Modesto": "green", "Fresno": "red"}
handles = []
for city, url in city_urls.items():
    df = load_aod_data(url)
    if df is not None and 'AOD_500nm' in df.columns:
        series = df["AOD_500nm"].loc[StartDateTime:EndDateTime].resample(SampleRate).mean()
        h, = ax.plot(series, marker='o', linestyle='-', label=f"{city} AOD_500nm", color=colors[city])
        handles.append(h)

ax.set_ylabel('AOD (500nm)')
ax.set_ylim(AOD_min, AOD_max)

# Temperature Axis
ax2 = ax.twinx()
temp_series = temp_df[0].loc[StartDateTime:EndDateTime].resample(SampleRate).mean().div(10)
ax2.plot(temp_series, '.r-', label='Temperature (°C)')
ax2.set_ylabel("Temperature (°C)")
ax2.set_ylim(temp_series.min() - 1, temp_series.max() + 3)

# Wind Vectors
ax3 = ax.twinx()
ax3.spines.right.set_position(("axes", 1.1))
max_wind = np.sqrt((wind_components[5].astype(float).max() / 10)**2 + (wind_components[6].astype(float).max() / 10)**2)
ax3.set_ylim(0, max_wind)
ax3.set_ylabel("Wind Speed (m/s)")

ax3.quiver(
    wind_components[5].resample(windSampleRate).mean().index,
    max_wind - 1,
    -wind_components[5].resample(windSampleRate).mean().div(10),
    -wind_components[6].resample(windSampleRate).mean().div(10),
    color='b', width=0.005, scale=1
)

# Legend & Layout
plt.legend(handles=handles, loc='upper left')
plt.tight_layout()
st.pyplot(fig)


