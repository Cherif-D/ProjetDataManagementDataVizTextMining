import sys
import os
import subprocess

if "__file__" in globals():
    script_dir = os.path.dirname(os.path.abspath(__file__)) 
else:
    script_dir = os.getcwd()
os.chdir(script_dir)

import streamlit as st

import plotly.graph_objects as go
import pandas as pd
import joblib

import texts
import graph
from util import (  ticker_to_name,
                    name_to_ticker,
                    adjust_to_last_friday,
                    compared_by,
                    type_map,
                    secteur_map,
                    benchmark_map   )

if not (    os.path.exists("sentiment_model.joblib") and
            os.path.exists("tfidf_vectorizer.joblib") and
            os.path.exists("classification_report.joblib")  ):
    
    with st.status( label="Entrainement du modèle de sentiment de texte (~30sec)",
                    expanded=True   ) as status:
        
        st.write("Lancement du script")
        subprocess.run([sys.executable,"text_sentiment.py"])
        status.update(label="Entrainement terminé", expanded=False)


from text_sentiment import (    text_cleaner,
                                generer_wordcloud   )

#CREATION D UNE FONCTION D'IMPORT DES DIFFERENTS DATAFRAMES AFIN QU IL SOIT CONSERVE EN MEMOIRE
@st.cache_data
def load_df(path:str) -> pd.DataFrame:

    return pd.read_csv(path)

#IMPORT DU DATAFRAME FINAL
data = load_df("data/dataframe_final_pret_pour_streamlit.csv")
#CONVERSION DE LA COLONNE DATE EN DATETIME POUR L'ANALYSE TEMPORELLE
data["Date"] = pd.to_datetime(data["Date"])
#CONVERTION EN TYPE CATEGORY POUR ACCELERER CERTAINE OPERATION
data["Type_actif"] = data["Type_actif"].astype("category", copy=False)
data["Secteur"] = data["Secteur"].astype("category", copy=False)
data["Benchmark"] = data["Benchmark"].astype("category", copy=False)
data["Ticker"] = data["Ticker"].astype("category", copy=False)

##################################################################################################################
###   CONFIGURATION DE LA SIDEBAR   ##############################################################################
##################################################################################################################

st.sidebar.markdown("### :material/settings: Paremètre")

presentation = st.sidebar.toggle("Présentation du jeu de données",value=True)
text_analysis = st.sidebar.toggle("Analyseur de text")

st.sidebar.subheader("Analyse")
comparison = st.sidebar.toggle("Comparer plusieurs actifs")

if not comparison:

    st.session_state["skip"] = False

    asset_name = st.sidebar.selectbox("Sélectionner un actif", list(ticker_to_name.values()))
    asset_ticker = name_to_ticker[asset_name]

    first_value = data["Prix"][data["Ticker"] == asset_ticker].iloc[0]
    date_first_different_price = data["Date"][(data["Ticker"] == asset_ticker) & (first_value != data["Prix"])].iloc[0]
    date_first_different_price -= pd.Timedelta(days=1)

    start_date = st.sidebar.date_input( "Date de début",
                                        date_first_different_price,
                                        min_value=date_first_different_price,
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

    group = st.sidebar.toggle("Par groupe",value=True) if comparison_type != "Actif" else None
    asset_names =  st.sidebar.multiselect("Sélectionner plusieurs actifs", asset_list) if not group else asset_list
    asset_tickers = [name_to_ticker[name] for name in asset_names]

    submit = st.sidebar.button("Comparer", use_container_width=True)

    if "skip" in st.session_state:
        if "asset_names" in st.session_state:
            st.session_state["skip"] = True if st.session_state["asset_names"] == set(asset_names) else False
            presentation = False if st.session_state["asset_names"] == set(asset_names) else presentation

    if len(asset_names) < 2:
        submit = False
        group_small = st.sidebar.badge( "Ce groupe contient moins de 2 actifs",
                                        icon=":material/error:",
                                        color="red" ) if group else None
        st.sidebar.badge("Sélectionner au moins 2 actifs",icon=":material/error:",color="red")

##################################################################################################################
###   MISE EN PAGE DE LA PRESENTATION DU JEU DE DONNEES   ########################################################
##################################################################################################################

if presentation and not submit:

    st.session_state["skip"] = False

    pre_data = load_df("data/donnees_financieres_300k_lignes.csv")
    pre_data_2 = load_df("data/donnees_financieres_clean.csv")
    pre_data["Ticker"] = pre_data["Ticker"].astype("category", copy=False)
    pre_data_2["Ticker"] = pre_data_2["Ticker"].astype("category", copy=False)

    st.header("Présentation du jeu de données")

    st.markdown(f":blue-badge[:material/info: Information] \n\n{texts.text_1}")
    st.subheader("Jeu de données avant nettoyage")
    st.dataframe(pre_data, use_container_width=True)
    st.info(    f"nombre de ligne : **{pre_data.shape[0]}**"
                f"\n\nnombre de colonne : **{pre_data.shape[1]}**"  )

    st.subheader("Jeu de données après nettoyage")
    st.markdown(f":blue-badge[:material/info: Information] \n\n{texts.text_2}")
    col_1, col_2= st.columns([4,1])
    with col_2:
        see_more = st.toggle("En voir plus",  key="voir_plus_1")
    if see_more:
        col_1, col_2= st.columns(2)
        with col_1:
            st.markdown("###### Description de la colonne prix")
            st.dataframe(pre_data.describe())
            st.markdown("###### Période de couverture des données")
            st.pyplot(graph.graph_coverage(pre_data))
        with col_2:
            st.markdown("###### Actifs avec le plus de valeurs manquantes")
            st.pyplot(graph.graph_missing_value(pre_data))
            st.markdown("###### Distribution Avant/Après nettoyage")
            st.pyplot(graph.graph_price_distrib(pre_data,pre_data_2))
    st.dataframe(pre_data_2, use_container_width=True)
    st.info(    f"nombre de ligne : **{pre_data_2.shape[0]}**"
                f"\n\nnombre de colonne : **{pre_data_2.shape[1]}**"  )

    st.subheader("Jeu de données après traitement")
    if st.toggle("En voir plus",  key="voir_plus_2"):
        st.markdown(f":blue-badge[:material/info: Information] \n\n{texts.text_3}")
        st.markdown(f":blue-badge[:material/pie_chart: Pie Chart]")
        st.plotly_chart(graph.graph_category_pie_chart(data,data["Ticker"].unique()))
    st.dataframe(data, use_container_width=True)
    st.info(    f"nombre de ligne : **{data.shape[0]}**"
                f"\n\nnombre de colonne : **{data.shape[1]}**"  )
    
##################################################################################################################
###   MISE EN PAGE SANS COMPARAISON   ############################################################################
##################################################################################################################
    
if submit and not comparison:
    
    st.markdown(f"# :green-badge[:material/analytics: Analyse] Analyse de {asset_name}")

    st.markdown(f"### :green-badge[:material/finance_mode: Prix] Graphique de {asset_name}")
    st.plotly_chart(graph.graph_price(data,asset_ticker,start_date,end_date))

    st.markdown(f"### :green-badge[:material/bar_chart_4_bars: Distribution] Histogramme des rendements de {asset_name}")
    st.plotly_chart(graph.graph_returns_distrib(data,asset_ticker,start_date,end_date))

    st.markdown(f"### :green-badge[:material/electric_bolt: Risque] Volatilité des rendements de {asset_name}")
    st.plotly_chart(graph.graph_volatility(data,asset_ticker,start_date,end_date))

    st.markdown(f"### :green-badge[:material/electric_bolt: Risque] Volatilité des rendements de {asset_name}")
    st.plotly_chart(graph.graph_boxplot_vol(data,asset_ticker,start_date,end_date))

    if asset_ticker not in data["Benchmark"].unique():

        st.markdown(f"### :green-badge[:material/balance: Versus] {asset_name} VS benchmark : {benchmark_map[asset_ticker]}")
        st.plotly_chart(graph.graph_asset_vs_benchmark(data,asset_ticker,benchmark_map[asset_ticker],start_date,end_date))

        st.markdown(f"### :green-badge[:material/balance: Versus] {asset_name} & benchmark : {benchmark_map[asset_ticker]}")
        st.plotly_chart(graph.graph_price_asset_and_benchmark(data,asset_ticker,benchmark_map[asset_ticker],start_date,end_date))

##################################################################################################################
###   MISE EN PAGE AVEC COMPARAISON   ############################################################################
##################################################################################################################

if (submit and comparison) or (st.session_state.get("skip", False)):

    st.session_state["skip"] = True
    st.session_state["asset_names"] = set(asset_names)

    match len(asset_names):

        case 2:
            comparison_title = f"Comparaison entre {asset_names[0]} et {asset_names[1]}"
        case 3:
            comparison_title = f"Comparaison entre {asset_names[0]}, {asset_names[1]} et {asset_names[2]}"
        case x if x>3:
            noms = ", ".join(asset_names[:-1])
            comparison_title = f"Comparaison entre {noms} et {asset_names[-1]}"

    st.markdown(f"# :violet-badge[:material/balance: Versus] {comparison_title}")

    first_values = []
    for ticker in asset_tickers:
        
        first_value = data["Prix"][data["Ticker"] == ticker].iloc[0]
        date_first_different_price = data["Date"][(data["Ticker"] == ticker) & (first_value != data["Prix"])].iloc[0]
        date_first_different_price -= pd.Timedelta(days=1)
        first_values.append(date_first_different_price)

    first_value = max(first_values)

    col_1, col_2 = st.columns(2)

    with col_1:

        start_date = st.date_input( "Date de début",
                                    first_value,
                                    min_value=first_value,
                                    max_value=data["Date"][data["Ticker"] == ticker].iloc[-20]    )

    with col_2:

        end_date = st.date_input(   "Date de fin",
                                    data["Date"][data["Ticker"] == ticker].iloc[-1],
                                    min_value=start_date + pd.Timedelta(days=20),
                                    max_value=data["Date"][data["Ticker"] == ticker].iloc[-1]   )
        
    st.markdown(f"### :violet-badge[:material/pie_chart: Pie Chart] Répartition")
    st.plotly_chart(graph.graph_category_pie_chart(data,asset_tickers))

    st.markdown(f"### :violet-badge[:material/finance_mode: Prix] Graphique des actifs")
    st.plotly_chart(graph.graph_price(data,asset_tickers,start_date,end_date))

    st.markdown(f"### :violet-badge[:material/grid_on: Matrice] Heatmap de corrélation des actifs")
    st.plotly_chart(graph.graph_corr(data,asset_tickers,start_date,end_date))

    st.markdown(f"### :violet-badge[:material/stacked_bar_chart: Barplot] Volatilité des actifs")
    st.plotly_chart(graph.graph_boxplot_vol(data,asset_tickers,start_date,end_date))

##################################################################################################################
###   MISE EN PAGE TEXT MINING   #################################################################################
##################################################################################################################

if text_analysis:

    st.markdown(f"# :grey-badge[:material/notes:] Text mining")

    col_1, col_2 = st.columns(2)

    with col_1:

        text = st.text_area(label="Texte à analyser", value=texts.text_4)

    with col_2:
        
        text = text_cleaner(text)
        st.pyplot(generer_wordcloud(text))

    st.markdown(f"# :grey-badge[:material/star:] Résultat")

    @st.cache_data
    def joblib_load(path:str):

        return joblib.load(path)

    model = joblib_load("sentiment_model.joblib")
    vectorizer = joblib_load("tfidf_vectorizer.joblib")
    classification_report = joblib_load("classification_report.joblib")

    text = vectorizer.transform([text])
    y_pred = model.predict(text)

    match y_pred:

        case 0:
            sentiment = "Négatif"
            badge_sentiment = ":material/sentiment_dissatisfied:"
            sentiment_color = "red"
        case 1:
            sentiment = "Neutre"
            badge_sentiment = ":material/sentiment_neutral:"
            sentiment_color = "grey"
        case 2:
            sentiment = "Positif"
            badge_sentiment = ":material/sentiment_satisfied:"
            sentiment_color = "green"

    st.badge(label=f"Le sentiment de l'article est {sentiment}", icon=badge_sentiment, color=sentiment_color)

    if st.toggle("En voir plus",  key="voir_plus_3"):

        st.markdown(f"### :blue-badge[:material/info: Information] Rapport de Classification")
        st.pyplot(graph.graph_report(classification_report))