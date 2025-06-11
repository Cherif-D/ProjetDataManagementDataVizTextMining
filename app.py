import streamlit as st

import plotly.graph_objects as go
import pandas as pd

from util import ticker_to_names, names_to_ticker

#IMPORT DU DATAFRAME FINAL
data = pd.read_csv("data/dataframe_final_pret_pour_streamlit.csv")
#CONVERSION DE LA COLONNE DATE EN DATETIME POUR L'ANALYSE TEMPORELLE
data["Date"] = pd.to_datetime(data["Date"])

#################################
###CONFIGURATION DE LA SIDEBAR###
#################################

st.sidebar.header("Paremètre")

comparaison = st.sidebar.toggle("Comparer plusieurs actifs")

if not comparaison:

    st.sidebar.subheader("Analyse")

    asset_name = st.sidebar.selectbox("Sélectionner un actif", list(ticker_to_names.values()))
    asset_ticker = names_to_ticker[asset_name]

    start_date = st.sidebar.date_input( "Date de début",
                                        data["Date"][data["Ticker"] == asset_ticker].iloc[0],
                                        min_value=data["Date"][data["Ticker"] == asset_ticker].iloc[0],
                                        max_value=data["Date"][data["Ticker"] == asset_ticker].iloc[-20] )
    
    end_date = st.sidebar.date_input(   "Date de fin",
                                        data["Date"][data["Ticker"] == asset_ticker].iloc[-1],
                                        min_value=start_date + pd.Timedelta(days=20),
                                        max_value=data["Date"][data["Ticker"] == asset_ticker].iloc[-1]  )