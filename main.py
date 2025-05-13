import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Function to load AOD data
@st.cache_data
def load_aod_data(url):
    df = pd.read_csv(url, skiprows=6)
    df['Date'] = pd.to_datetime(df['Date(dd:mm:yyyy)'] + ' ' + df['Time(hh:mm:ss)'])
    df = df[['Date', 'AOD_500nm']]
    df = df.dropna()
    df = df[df['AOD_500nm'] < 2.0]  # Filter out extreme outliers
    return df

# Function to load Turlock meteorological data
@st.cache_data
def load_turlock_meteo(url):
    df = pd.read_csv(url)
    df['datetime'] = pd.to_datetime(df['valid'])
    df[['TMP', 'UGRD', 'VGRD']] = df[['TMP', 'UGRD', 'VGRD']].replace('+9999', np.nan)
    df[['TMP', 'UGRD', 'VGRD']] = df[['TMP', 'UGRD', 'VGRD']].astype(float)
    df['TMP_C'] = df['TMP'] - 273.15  # Convert from Kelvin to Celsius
    return df

# URLs for AOD Data
turlock_url = "https://raw.githubusercontent.com/Rsaltos7/TurlockAOD/main/20240101_20241231_Turlock.lev15"
sacramento_url = "https://raw.githubusercontent.com/Rsaltos7/SacromentoAOD/refs/heads/main/20240101_20241231_Sacramento_River.lev15"
modesto_url = "https://raw.githubusercontent.com/Rsaltos7/ModestoAOD/refs/heads/main/20240101_20241231_Modesto.lev15"
fresno_url = "https://raw.githubusercontent.com/Rsaltos7/FresnoAOD/refs/heads/main/20240101_20241231_Fresno_2.lev15"

# URL for Turlock Wind and Temperature
wind_url = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=MCE&data=tmpf&data=sknt&data=drct&year1=2024&month1=1&day1=1&year2=2024&month2=12&day2=31&tz=Etc/UTC&format=comma&latlon=yes&missing=+9999&trace=0.0001&direct=no&report_type=3&report_type=4"

# Load data
turlock_df = load_aod_data(turlock_url)
sacramento_df = load_aod_data(sacramento_url)
modesto_df = load_aod_data(modesto_url)
fresno_df = load_aod_data(fresno_url)
wind_df = load_turlock_meteo(wind_url)

# Streamlit UI
st.title("California AOD + Turlock Wind & Temperature")
st.write("Visualizing AOD across four cities with Turlock's temperature and wind overlay.")

# Date range selection
min_date = max([
    df['Date'].min() for df in [turlock_df, sacramento_df, modesto_df, fresno_df]
])
max_date = min([
    df['Date'].max() for df in [turlock_df, sacramento_df, modesto_df, fresno_df]
])
start_date, end_date = st.date_input("Select Date Range", [min_date.date(), max_date.date()])

# AOD range slider
aod_min, aod_max = st.slider("Adjust AOD Y-axis Range", 0.0, 2.0, (0.0, 0.5), 0.01)

# Filter by date
def filter_date(df):
    return df[(df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))]

turlock_df = filter_date(turlock_df)
sacramento_df = filter_date(sacramento_df)
modesto_df = filter_date(modesto_df)
fresno_df = filter_date(fresno_df)
wind_df = wind_df[(wind_df['datetime'] >= pd.Timestamp(start_date)) & (wind_df['datetime'] <= pd.Timestamp(end_date))]

# Plot
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot AOD data
ax1.plot(turlock_df['Date'], turlock_df['AOD_500nm'], label='Turlock AOD', color='blue')
ax1.plot(sacramento_df['Date'], sacramento_df['AOD_500nm'], label='Sacramento AOD', color='green')
ax1.plot(modesto_df['Date'], modesto_df['AOD_500nm'], label='Modesto AOD', color='orange')
ax1.plot(fresno_df['Date'], fresno_df['AOD_500nm'], label='Fresno AOD', color='red')
ax1.set_ylabel("AOD at 500nm")
ax1.set_ylim(aod_min, aod_max)
ax1.legend(loc="upper left")

# Twin axis for temperature
ax2 = ax1.twinx()
ax2.plot(wind_df['datetime'], wind_df['TMP_C'], label='Temperature (°C)', color='black', linestyle='dotted')
ax2.set_ylabel("Temperature (°C)", color='black')

# Wind vectors as quivers
step = len(wind_df) // 20 or 1
times = wind_df['datetime'].iloc[::step]
u = wind_df['UGRD'].iloc[::step]
v = wind_df['VGRD'].iloc[::step]
temps = wind_df['TMP_C'].iloc[::step]
aod_vals = np.interp(times.astype(np.int64), turlock_df['Date'].astype(np.int64), turlock_df['AOD_500nm'])

# Normalize wind vector lengths for plotting
quiver_scale = 50
ax1.quiver(times, aod_vals, u, v, scale=quiver_scale, width=0.0025, color='purple', label='Wind Vectors')

st.pyplot(fig)
