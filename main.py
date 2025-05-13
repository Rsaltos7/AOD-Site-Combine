import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import StringIO
import datetime

# URLs for AOD data
AOD_URLS = {
    "Turlock": "https://raw.githubusercontent.com/Rsaltos7/TurlockAOD/main/20240101_20241231_Turlock.lev15",
    "Sacramento": "https://raw.githubusercontent.com/Rsaltos7/SacromentoAOD/refs/heads/main/20240101_20241231_Sacramento_River.lev15",
    "Modesto": "https://raw.githubusercontent.com/Rsaltos7/ModestoAOD/refs/heads/main/20240101_20241231_Modesto.lev15",
    "Fresno": "https://raw.githubusercontent.com/Rsaltos7/FresnoAOD/refs/heads/main/20240101_20241231_Fresno_2.lev15"
}

# Turlock wind and temperature data (same as before)
TURLOCK_METEOROLOGY_URL = "https://raw.githubusercontent.com/Rsaltos7/TurlockAOD/main/wind_temperature.csv"

def load_aod_data(url):
    try:
        response = requests.get(url)
        df = pd.read_csv(StringIO(response.text), comment='#', header=None, delim_whitespace=True)
        df.columns = ['Date', 'Time', 'AOD']
        df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + df['Time'].astype(str).str.zfill(4), format='%Y%m%d%H%M')
        df = df[['Datetime', 'AOD']]
        df = df.replace(999.999, np.nan).dropna()
        return df
    except Exception as e:
        st.error(f"Error loading AOD data: {e}")
        return pd.DataFrame(columns=['Datetime', 'AOD'])

def load_turlock_meteorology(url):
    try:
        df = pd.read_csv(url)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df[['U', 'V', 'TMP']] = df[['U', 'V', 'TMP']].replace('+9999', np.nan).astype(float)
        df['TMP'] = df['TMP'] - 273.15  # Convert from Kelvin to Celsius
        return df
    except Exception as e:
        st.error(f"Error loading Turlock meteorology data: {e}")
        return pd.DataFrame(columns=['datetime', 'U', 'V', 'TMP'])

# Load all data
aod_data = {city: load_aod_data(url) for city, url in AOD_URLS.items()}
turlock_met = load_turlock_meteorology(TURLOCK_METEOROLOGY_URL)

# Streamlit interface
st.title("AOD + Turlock Meteorology Viewer")

# Date filter
min_date = min(df['Datetime'].min() for df in aod_data.values())
max_date = max(df['Datetime'].max() for df in aod_data.values())
date_range = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Y-axis AOD value slider
y_min, y_max = st.slider("AOD Y-axis range", 0.0, 1.5, (0.0, 1.0), 0.05)

# Filter data based on selected date range
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_aod_data = {
    city: df[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)]
    for city, df in aod_data.items()
}
filtered_met = turlock_met[(turlock_met['datetime'] >= start_date) & (turlock_met['datetime'] <= end_date)]

# Plotting
fig, ax1 = plt.subplots(figsize=(14, 6))

# Plot AOD data
for city, df in filtered_aod_data.items():
    ax1.plot(df['Datetime'], df['AOD'], label=f'{city} AOD')

ax1.set_ylabel('AOD')
ax1.set_ylim(y_min, y_max)
ax1.set_xlabel('Date')
ax1.legend(loc='upper left')
ax1.grid(True)

# Add temperature on secondary y-axis
if not filtered_met.empty:
    ax2 = ax1.twinx()
    ax2.plot(filtered_met['datetime'], filtered_met['TMP'], color='red', label='Turlock Temp (°C)', alpha=0.5)
    ax2.set_ylabel('Temperature (°C)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    # Wind vectors (as quiver plot approximation using lines)
    for i in range(0, len(filtered_met), max(len(filtered_met)//100, 1)):  # limit number of arrows for readability
        dt = filtered_met.iloc[i]
        ax1.arrow(dt['datetime'], y_min, dt['U'], dt['V'], head_width=0.02, head_length=0.01, fc='blue', ec='blue', alpha=0.5)

st.pyplot(fig)
