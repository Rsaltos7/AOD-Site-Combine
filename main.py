import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to load AOD data for all cities
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

# Function to load Turlock wind/temperature data
@st.cache_data
def load_turlock_met_data():
    url = "https://raw.githubusercontent.com/aadi350/AOD/main/turlock_wind_temp.csv"
    df = pd.read_csv(url)

    # Split TMP and WND columns
    df[['TMP_1', 'TMP_2']] = df['TMP'].str.split(',', expand=True)
    df[['WND_1', 'WND_2']] = df['WND'].str.split(',', expand=True)

    # Replace invalid values and convert to float
    df['TMP_C'] = df['TMP_1'].replace('+9999', np.nan).astype(float) / 10  # Kelvin to °C
    df['WindSpeed'] = df['WND_2'].replace('+9999', np.nan).astype(float) * 0.1

    # Convert date
    df['DATE'] = pd.to_datetime(df['DATE'])

    return df[['DATE', 'TMP_C', 'WindSpeed']]

# Load AOD data for different locations
turlock_df = load_data("https://raw.githubusercontent.com/aadi350/AOD/main/Turlock.csv")
modesto_df = load_data("https://raw.githubusercontent.com/aadi350/AOD/main/Modesto.csv")
sacramento_df = load_data("https://raw.githubusercontent.com/aadi350/AOD/main/Sacramento.csv")
fresno_df = load_data("https://raw.githubusercontent.com/aadi350/AOD/main/Fresno.csv")

# Load Turlock wind/temp data
turlock_met_df = load_turlock_met_data()

# Convert date column to datetime in AOD data
for df in [turlock_df, modesto_df, sacramento_df, fresno_df]:
    df['Date'] = pd.to_datetime(df['Date'])

# Merge Turlock AOD and meteorology data on date
merged_df = pd.merge(turlock_df, turlock_met_df, how='inner', left_on='Date', right_on='DATE')

# Streamlit app layout
st.title("AOD & Meteorological Data Viewer")
st.write("Showing AOD values from multiple locations and temperature/wind for Turlock.")

# Plotting section
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot AOD from multiple cities
ax1.plot(turlock_df['Date'], turlock_df['AOD'], label='Turlock AOD', color='orange')
ax1.plot(modesto_df['Date'], modesto_df['AOD'], label='Modesto AOD', linestyle='--', color='gray')
ax1.plot(sacramento_df['Date'], sacramento_df['AOD'], label='Sacramento AOD', linestyle=':', color='green')
ax1.plot(fresno_df['Date'], fresno_df['AOD'], label='Fresno AOD', linestyle='-.', color='red')
ax1.set_ylabel("AOD")
ax1.set_xlabel("Date")
ax1.tick_params(axis='x', rotation=45)
ax1.legend(loc='upper left')

# Create a second y-axis for temperature and wind
ax2 = ax1.twinx()
ax2.plot(merged_df['Date'], merged_df['TMP_C'], label='Turlock Temp (°C)', color='blue')
ax2.plot(merged_df['Date'], merged_df['WindSpeed'], label='Turlock Wind (m/s)', color='purple')
ax2.set_ylabel("Temperature / Wind Speed")
ax2.legend(loc='upper right')

st.pyplot(fig)


