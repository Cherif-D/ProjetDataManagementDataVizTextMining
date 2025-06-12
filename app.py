import streamlit as st

import plotly.graph_objects as go
import pandas as pd

import texts
from util import (  ticker_to_name,
                    name_to_ticker,
                    adjust_to_last_friday,
                    compared_by,
                    type_map,
                    secteur_map,
                    benchmark_map   )

#CREATION D UNE FONCTION D'IMPORT DES DIFFERENTS DATAFRAMES AFIN QU IL SOIT CONSERVE EN MEMOIRE
@st.cache_data
def load_df(path):
    return pd.read_csv(path)

#IMPORT DU DATAFRAME FINAL
data = load_df("data/dataframe_final_pret_pour_streamlit.csv")
#CONVERSION DE LA COLONNE DATE EN DATETIME POUR L'ANALYSE TEMPORELLE
data["Date"] = pd.to_datetime(data["Date"])
#CONVERTION EN TYPE CATEGORY POUR ACCELERER CERTAINE OPERATION
data["Type_actif"] = data["Type_actif"].astype("category", copy=False)
data["Secteur"] = data["Secteur"].astype("category", copy=False)
data["Benchmark"] = data["Benchmark"].astype("category", copy=False)

##################################################################################################################
###   CONFIGURATION DE LA SIDEBAR   ##############################################################################
##################################################################################################################

st.sidebar.markdown("### :material/settings: Paremètre")

presentation = st.sidebar.toggle("Présentation du jeu de données")

st.sidebar.subheader("Analyse")
comparison = st.sidebar.toggle("Comparer plusieurs actifs")

if not comparison:

    asset_name = st.sidebar.selectbox("Sélectionner un actif", list(ticker_to_name.values()))
    asset_ticker = name_to_ticker[asset_name]

    first_value = data["Prix"][data["Ticker"] == asset_ticker].iloc[0]
    date_first_different_price = data["Date"][(data["Ticker"] == asset_ticker) & (first_value != data["Prix"])].iloc[0]
    date_first_different_price -= pd.Timedelta(days=1)

    start_date = st.sidebar.date_input( "Date de début",
                                        date_first_different_price,
                                        date_first_different_price,
                                        max_value=data["Date"][data["Ticker"] == asset_ticker].iloc[-20] )
    
    end_date = st.sidebar.date_input(   "Date de fin",
                                        data["Date"][data["Ticker"] == asset_ticker].iloc[-1],
                                        min_value=start_date + pd.Timedelta(days=20),
                                        max_value=data["Date"][data["Ticker"] == asset_ticker].iloc[-1]  )
    
    start_date = adjust_to_last_friday(start_date)
    end_date = adjust_to_last_friday(end_date)

    submit = st.sidebar.button("Analyser", use_container_width=True)

else:

    comparison_type = st.sidebar.selectbox("Comparaison par :", list(compared_by.keys()))

    if comparison_type == "Actif":

        asset_list = list(ticker_to_name.values())

    elif comparison_type == "Type d'actif":

        asset_type = st.sidebar.multiselect("Sélectionner une ou plusieurs catégories d'actifs", list(data["Type_actif"].unique()))
        asset_list = [name for name in ticker_to_name.values() if type_map[name_to_ticker[name]] in asset_type]

    elif comparison_type == "Secteur":

        asset_sector = st.sidebar.multiselect("Sélectionner un ou plusieurs secteurs d'activité", list(data["Secteur"].unique()))
        asset_list = [name for name in ticker_to_name.values() if secteur_map[name_to_ticker[name]] in asset_sector]

    elif comparison_type == "Benchmark":

        asset_benchmark = st.sidebar.multiselect("Sélectionner un ou plusieurs benchmarks", list(data["Benchmark"].unique()))
        asset_list = [name for name in ticker_to_name.values() if benchmark_map[name_to_ticker[name]] in asset_benchmark]

    asset_names =  st.sidebar.multiselect("Sélectionner plusieurs actifs", asset_list)
    asset_tickers = [name_to_ticker[name] for name in asset_names]

    submit = st.sidebar.button("Comparer", use_container_width=True)

##################################################################################################################
###   MISE EN PAGE   #############################################################################################
##################################################################################################################

if presentation and not submit:

    pre_data =load_df("data/donnees_financieres_300k_lignes.csv")
    pre_data_2 = load_df("data/donnees_financieres_clean.csv")
    st.header("Présentation du jeu de données")

    st.markdown(f":blue-badge[:material/info: Information] {texts.text_1}")
    st.subheader("Jeu de données avant nettoyage")
    st.dataframe(pre_data, use_container_width=True)
    st.info(    f"nombre de ligne : **{pre_data.shape[0]}**"
                f"\n\nnombre de colonne : **{pre_data.shape[1]}**"  )

    st.subheader("Jeu de données après nettoyage")
    st.dataframe(pre_data_2, use_container_width=True)
    st.info(    f"nombre de ligne : **{pre_data_2.shape[0]}**"
                f"\n\nnombre de colonne : **{pre_data_2.shape[1]}**"  )

    st.subheader("Jeu de données après traitement")
    st.dataframe(data, use_container_width=True)
    st.info(    f"nombre de ligne : **{data.shape[0]}**"
                f"\n\nnombre de colonne : **{data.shape[1]}**"  )