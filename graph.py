import pandas as pd
import matplotlib.pyplot as plt
import math
import plotly.graph_objects as go

import streamlit as st

@st.cache_data
def graph_missing_value(df:pd.DataFrame) -> plt.Figure:

    total_manquants = df['Prix'].isna().groupby(df['Ticker'],observed=False).sum()
    total_observations = df['Prix'].groupby(df['Ticker'],observed=False).count()
    pourcentage_manquants = (total_manquants / (total_manquants + total_observations) * 100).round(2)

    missing_by_ticker = pd.DataFrame(   {   'total_manquants': total_manquants,
                                            'total_observations': total_observations,
                                            'pourcentage_manquants': pourcentage_manquants  }   )

    missing_tickers = missing_by_ticker[missing_by_ticker['total_manquants'] > 0]\
                    .sort_values('pourcentage_manquants', ascending=False)
    
    plt.figure(figsize=(12, 12))

    missing_tickers.head(15)['pourcentage_manquants'].plot(kind='barh', color='salmon')
    plt.title('Top 15 des actifs avec le plus de valeurs manquantes')
    plt.xlabel('% de valeurs manquantes')

    plt.gca().invert_yaxis()
    plt.tight_layout()
    return plt.gcf()

@st.cache_data
def graph_coverage(df: pd.DataFrame) -> plt.Figure:

    df['Date'] = pd.to_datetime(df['Date'])

    df = df.dropna(axis=0, how="any")

    coverage = df.groupby('Ticker',observed=False)['Date'].agg(min='min', max='max').reset_index()
    coverage['duration'] = (coverage['max'] - coverage['min']).dt.days
    coverage = coverage.sort_values('min')

    plt.figure(figsize=(12, 12))
    plt.barh(   y=coverage['Ticker'],
                width=coverage['duration'],
                left=coverage['min'],
                color='skyblue',
                edgecolor='black',
                height=0.3  )
    plt.xlabel("Date")
    plt.ylabel("Ticker")
    plt.title("Couverture temporelle des actifs")
    plt.tight_layout()
    return plt.gcf()

@st.cache_data
def graph_price_distrib(df:pd.DataFrame, df_clean:pd.DataFrame) -> plt.Figure:

    df = df['Prix'].dropna().apply(math.log1p)
    df_clean = df_clean['Prix'].dropna().apply(math.log1p)

    plt.figure(figsize=(12, 12))

    plt.hist(df,alpha=0.5,bins=100,density=True,label="Avant")
    plt.hist(df_clean,alpha=0.5,bins=100,density=True,label="Après")
    plt.title('Comparaison des Distributions de Prix (échelle log) - AVANT vs APRÈS Nettoyage')
    plt.xlabel('Log(1 + Prix)')
    plt.ylabel('Densité')
    plt.legend(loc="best")
    plt.tight_layout()
    return plt.gcf()