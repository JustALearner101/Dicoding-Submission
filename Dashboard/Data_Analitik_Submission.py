# -*- coding: utf-8 -*-
"""Untitled14.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1B0_qn0ckIh3qdNEoAXy6Ds9yJZNyntfd
"""


#Import Library
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Load data
df = pd.read_csv('Dashboard/PRSA_Data_Shunyi_20130301-20170228.csv')

# Cek kolom
print(df.columns)

# 1. Convert kolom datetime (kalo datanya udah bener formatnya)
df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']], errors='coerce')

# 2. Drop rows dengan datetime gagal parse (NA)
df.dropna(subset=['datetime'], inplace=True)

# 3. Set datetime sebagai index
df.set_index('datetime', inplace=True)

# 4. Sort index buat jaga-jaga
df.sort_index(inplace=True)

# 5. Pilih kolom polutan
pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']

# 6. Pastikan semua kolom polutan tipe datanya numeric (incase ada string nyelip)
for pollutant in pollutants:
    df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')

# 7. Cek missing values & handle
# Cek missing values summary
print("Missing values per pollutant:\n", df[pollutants].isnull().sum())

# Handle missing values
# Kalau missingnya di tengah-tengah, fill pakai interpolasi
df[pollutants] = df[pollutants].interpolate(method='time')

# Kalau masih ada missing di awal/akhir, fill pakai metode lain
df[pollutants] = df[pollutants].fillna(method='bfill').fillna(method='ffill')

# 8. Optional: Filter outlier pake IQR biar datanya gak toxic, seperti dirinya
def remove_outliers_iqr(df, columns):
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    return df

df_clean = remove_outliers_iqr(df, pollutants)

# 9. Buat data monthly buat tren time series
df_monthly = df_clean[pollutants].resample('M').mean()

# 10. Optional: tambahin kolom bantu buat analisis musiman
df_clean['month'] = df_clean.index.month
df_clean['year'] = df_clean.index.year

# Result
print("Data siap digunakan 🚀")
print(df_clean.head())

# =================================================================================

# Streamlit app layout
st.title("Dashboard Kualitas Udara 🚀")

# Sidebar Navigation
st.sidebar.header("Navigasi 📌")
menu = st.sidebar.radio("Pilih visualisasi:", [
    "Tren Waktu",
    "Analisis Musiman",
    "Distribusi Polutan",
    "Korelasi Polutan",
    "Polusi per Hari (Weekday)",
    "Perbandingan Siang vs Malam",
    "Kalender Polusi",
    "Anomali Hari Polusi Tinggi",
    "AQI Calculator",
    # "statsmodel",
    "Interaktif",
])

if menu == "Tren Waktu":
    st.header("Tren Kualitas Udara dari Waktu ke Waktu 📈")
    fig, ax = plt.subplots(figsize=(12, 6))
    for pollutant in pollutants:
        ax.plot(df_monthly.index, df_monthly[pollutant], label=pollutant)
    ax.set_title("Tren Kualitas Udara dari Waktu ke Waktu")
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Konsentrasi Polutan (µg/m³ atau ppb)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

#Analisis Musiman
elif menu == "Analisis Musiman":
    st.header("Analisis Musiman PM2.5 📊")

    # Setup figure & axis
    fig, ax = plt.subplots(figsize=(14, 7))

    # Buat boxplot yang lebih kece
    sns.boxplot(
        x=df.index.month,
        y=df["PM2.5"],
        ax=ax,
        palette="coolwarm",  # Warna kece: dari biru ke merah
        medianprops=dict(linestyle='-', linewidth=2.5, color='firebrick')
    )

    # Tambahin custom label biar ga cuma angka bulan doang
    bulan_labels = [
        "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
        "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
    ]
    ax.set_xticks(range(12))
    ax.set_xticklabels(bulan_labels)

    # Set judul & label sumbu
    ax.set_xlabel("Bulan", fontsize=14)
    ax.set_ylabel("PM2.5 (µg/m³)", fontsize=14)
    ax.set_title("Variasi Musiman PM2.5 (µg/m³)\nBagaimana Polusi Udara Berubah Sepanjang Tahun", fontsize=16)

    # Batas Y (opsional, buat nge-cut outlier tinggi yang ganggu)
    ax.set_ylim(0, 500)

    # Kasih grid biar pembaca ga sipit mata
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Tampilkan di Streamlit
    st.pyplot(fig)


elif menu == "Distribusi Polutan":
    st.header("Distribusi Polutan 📊")
    
    pollutant = st.selectbox("Pilih polutan", pollutants)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df[pollutant].dropna(), kde=True, bins=30, ax=ax)
    ax.set_title(f'Distribusi {pollutant}')
    ax.set_xlabel(f'{pollutant} (µg/m³)')
    st.pyplot(fig)

elif menu == "Korelasi Polutan":
    st.header("Korelasi Antar Polutan & Cuaca 🔗")
    
    corr_cols = pollutants + ['TEMP', 'PRES', 'DEWP', 'WSPM']
    corr_matrix = df[corr_cols].corr()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('Matriks Korelasi Polutan & Cuaca')
    st.pyplot(fig)

elif menu == "Polusi per Hari (Weekday)":
    st.header("Rata-rata Polusi per Hari dalam Seminggu 📅")
    
    df['weekday'] = df.index.day_name()  # Nama hari
    
    fig, ax = plt.subplots(figsize=(12, 6))
    weekday_avg = df.groupby('weekday')[pollutants].mean().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
    weekday_avg.plot(kind='bar', ax=ax)
    ax.set_ylabel('Rata-rata Konsentrasi (µg/m³)')
    ax.set_title('Rata-rata Polusi Berdasarkan Hari')
    st.pyplot(fig)

elif menu == "Perbandingan Siang vs Malam":
    st.header("Perbandingan Siang vs Malam 🌞🌙")
    
    # Kategori waktu
    def get_time_of_day(hour):
        if 5 <= hour < 12:
            return 'Pagi'
        elif 12 <= hour < 17:
            return 'Siang'
        elif 17 <= hour < 21:
            return 'Sore'
        else:
            return 'Malam'
    
    df['time_of_day'] = df.index.hour.map(get_time_of_day)
    
    pollutant = st.selectbox("Pilih polutan", pollutants)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='time_of_day', y=pollutant, data=df, ax=ax, order=['Pagi', 'Siang', 'Sore', 'Malam'])
    ax.set_title(f'Konsentrasi {pollutant} Berdasarkan Waktu')
    st.pyplot(fig)

elif menu == "Kalender Polusi":
    st.header("Kalender Polusi Harian 🗓️")
    
    pollutant = st.selectbox("Pilih polutan", pollutants)
    
    df_daily = df[pollutant].resample('D').mean()
    df_daily = df_daily.to_frame(name=pollutant)
    
    df_daily['year'] = df_daily.index.year
    df_daily['month'] = df_daily.index.month
    df_daily['day'] = df_daily.index.day
    
    # Pivot table buat heatmap bulan x hari (per tahun)
    year = st.selectbox("Pilih Tahun", sorted(df_daily['year'].unique()))
    
    df_year = df_daily[df_daily['year'] == year].pivot_table(
        index='month', columns='day', values=pollutant
    )
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(df_year, cmap='YlOrRd', ax=ax)
    ax.set_title(f'Heatmap {pollutant} Tahun {year}')
    ax.set_xlabel('Tanggal')
    ax.set_ylabel('Bulan')
    st.pyplot(fig)

elif menu == "Anomali Hari Polusi Tinggi":
    st.header("Deteksi Hari dengan Polusi Ekstrem 🚨")
    
    pollutant = st.selectbox("Pilih polutan", pollutants)
    
    threshold = st.slider(f"Threshold {pollutant}", float(df[pollutant].min()), float(df[pollutant].max()), float(df[pollutant].quantile(0.95)))
    
    outliers = df[df[pollutant] >= threshold]
    
    st.write(f"{len(outliers)} hari ditemukan dengan {pollutant} >= {threshold}")
    st.dataframe(outliers[[pollutant]].sort_values(by=pollutant, ascending=False).head(10))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df[pollutant], label=pollutant)
    ax.scatter(outliers.index, outliers[pollutant], color='red', label='Anomali')
    ax.set_title(f'Anomali {pollutant}')
    ax.legend()
    st.pyplot(fig)

elif menu == "AQI Calculator":
    st.header("AQI Calculator PM2.5 🌫️")
    
    def calculate_pm25_aqi(concentration):
        # AQI breakpoints WHO China Standard (simplified)
        if concentration <= 35:
            return "Good (0-50)"
        elif concentration <= 75:
            return "Moderate (51-100)"
        elif concentration <= 115:
            return "Unhealthy for Sensitive (101-150)"
        elif concentration <= 150:
            return "Unhealthy (151-200)"
        elif concentration <= 250:
            return "Very Unhealthy (201-300)"
        else:
            return "Hazardous (300+)"
    
    df_daily = df['PM2.5'].resample('D').mean()
    df_daily_aqi = df_daily.apply(calculate_pm25_aqi)
    
    st.dataframe(df_daily_aqi.value_counts().rename_axis('AQI Category').reset_index(name='Jumlah Hari'))
    
    fig, ax = plt.subplots(figsize=(8, 5))
    df_daily_aqi.value_counts().plot(kind='bar', ax=ax, color='orange')
    ax.set_ylabel('Jumlah Hari')
    ax.set_title('Distribusi Kategori AQI PM2.5')
    st.pyplot(fig)

# Testing Site
# elif menu == "statsmodel":
#     result = seasonal_decompose(df["PM2.5"], model='additive', period=12)

#     fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(15, 10))
#     result.observed.plot(ax=ax1); ax1.set_title("Observed")
#     result.trend.plot(ax=ax2); ax2.set_title("Trend")
#     result.seasonal.plot(ax=ax3); ax3.set_title("Seasonal")
#     result.resid.plot(ax=ax4); ax4.set_title("Residual")

#     st.pyplot(fig)


elif menu == "Interaktif":
    st.header("Variasi Musiman PM2.5 Interaktif 📊")

    # nama bulan
    bulan_labels = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    # Plotly chart
    fig = px.box(
        df, 
        x=df.index.month, 
        y="PM2.5", 
        points="all",  # Tampilkan outlier
        labels={"x": "Bulan", "PM2.5": "PM2.5 (µg/m³)"},
        color=df.index.month.astype(str),
        title="Variasi Musiman PM2.5 Interaktif"
    )

    # label sumbu X
    fig.update_layout(
        xaxis=dict(
            tickmode='array', 
            tickvals=list(range(1, 13)),  # 1-12 sesuai month
            ticktext=bulan_labels  # Nama bulan
        )
    )

    st.plotly_chart(fig)
