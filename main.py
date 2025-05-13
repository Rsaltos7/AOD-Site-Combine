import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="AOD Site Comparison", layout="wide")

# ---- DATA LOADER ----
@st.cache_data
def load_data(url):
    try:
        df = pd.read_csv(
            url,
            comment='#',
            skiprows=6,  # Skipping the metadata header rows typical in AERONET
            delimiter=',',
            low_memory=False
        )
        # Combine date and time into one datetime column
        df['DateTime'] = pd.to_datetime(
            df['Date(dd:mm:yyyy)'] + ' ' + df['Time(hh:mm:ss)'],
            errors='coerce'
        )
        df.set_index('DateTime', inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading {url}: {e}")
        return None

# ---- SIDEBAR ----
st.sidebar.title("Settings")
url = st.sidebar.text_input("CSV URL or File Path", value="https://aeronet.gsfc.nasa.gov/path_to_file.csv")

# ---- MAIN APP ----
st.title("Aerosol Optical Depth (AOD) Site Comparison Tool")

if url:
    df = load_data(url)

    if df is not None:
        st.success("Data loaded successfully!")
        st.write("Preview of the data:")
        st.dataframe(df.head())

        # Allow user to choose wavelength column (example: 'AOD_500nm')
        aod_columns = [col for col in df.columns if 'AOD' in col]
        if aod_columns:
            selected_col = st.selectbox("Select AOD Wavelength Column", aod_columns)
            df_clean = df[[selected_col]].dropna()

            # Plot
            st.line_chart(df_clean)
        else:
            st.warning("No AOD columns found in the data.")
    else:
        st.warning("Could not load or parse the file. Check the URL and format.")
else:
    st.info("Please enter a CSV URL or file path to begin.")


