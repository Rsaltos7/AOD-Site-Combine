# Add these new URLs
city_files = {
    "Turlock":"https://raw.githubusercontent.com/Rsaltos7/TurlockAOD2024/refs/heads/main/20240101_20241231_Turlock_CA_USA.lev15",  # already loaded
    "Sacramento": "https://raw.githubusercontent.com/Rsaltos7/SacromentoAOD/refs/heads/main/20240101_20241231_Sacramento_River.lev15",
    "Modesto": "https://raw.githubusercontent.com/Rsaltos7/ModestoAOD/refs/heads/main/20240101_20241231_Modesto.lev15",
    "Fresno": "https://raw.githubusercontent.com/Rsaltos7/FresnoAOD/refs/heads/main/20240101_20241231_Fresno_2.lev15"
}

# Load and process new city AOD files
city_dfs = {}
for city, url in city_files.items():
    if isinstance(url, str):
        df = load_data(url)
        if df is not None and 'AOD_500nm' in df.columns:
            city_dfs[city] = df
    else:
        city_dfs[city] = url  # Turlock is already a DataFrame

# Temperature from TMP
Tdf = Wdf.loc[StartDate:EndDate,'TMP'].str.split(pat=',', expand = True)
Tdf.replace('+9999', np.nan, inplace=True)

fig, axes = plt.subplots(1,1, figsize=(16,9))
try:
    ax = axes[0,0]
except:
    try:
        ax = axes[0]
    except:
        ax = axes

fig.autofmt_xdate()
ax.set_title('AOD (500 nm), Modesto Wind Vectors, and Temperature')
ax.grid(True)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

ax.set_ylabel('AOD_500nm')
plot_handles = []
colors = {'Turlock': 'k', 'Sacramento': 'purple', 'Modesto': 'orange', 'Fresno': 'teal'}
for city, df in city_dfs.items():
    h, = ax.plot(df.loc[StartDate:EndDate, 'AOD_500nm'].resample(SampleRate).mean(), 
                 marker='o', linestyle='-', color=colors.get(city, 'gray'), label=f'{city} AOD')
    plot_handles.append(h)

ax.set_ylim(AOD_min, AOD_max)

# Temperature
ax2 = ax.twinx()
ax2.spines.right.set_position(('axes', 1.05))
ax2.set_ylabel('Temperature °C')
temp_series = Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10)
ax2.set_ylim(temp_series.min()//1, temp_series.max()//1 + 3)
temp_handle, = ax2.plot(temp_series, '.r-', label='Temperature', figure=fig)
plot_handles.append(temp_handle)

# Wind
ax3 = ax.twinx()
ax3.set_ylabel("Wind Mag m/s")
ax3.set_ylim(0, maxWind)
wind_handle = ax3.quiver(WNDdf[5].resample(windSampleRate).mean().index, maxWind - 1,
                         -WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                         -WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                         color='b', label='Wind Vector', width=0.005)

plot_handles.append(wind_handle)

plt.legend(handles=plot_handles, loc='best')
plt.tight_layout()

# Show in Streamlit
st.pyplot(fig)

