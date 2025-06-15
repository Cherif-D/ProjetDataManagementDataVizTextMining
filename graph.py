import pandas as pd
import matplotlib.pyplot as plt
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Union
import datetime

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

def graph_price(    df:pd.DataFrame,
                    asset_ticker:Union[str,pd.Categorical,list],
                    start_date:datetime,
                    end_date:datetime   ) -> go.Figure:
    
    asset_ticker = [asset_ticker] if not isinstance(asset_ticker,list) else asset_ticker

    fig = go.Figure()

    df1 = df.copy()
    for ticker in asset_ticker:

        df = df1[["Date","Prix"]][df1["Ticker"] == ticker]
        df.set_index("Date",inplace=True)
        df = df.loc[start_date:end_date,:]

        fig.add_trace(  go.Scatter( x=df.index,
                                    y=df["Prix"],
                                    name = str(ticker)    )   )
    
    fig.update_layout(  xaxis_title = "Date",
                        yaxis_title = "Prix"    )

    return fig

def graph_returns_distrib(  df:pd.DataFrame,
                            asset_ticker:Union[str,pd.Categorical],
                            start_date:datetime,
                            end_date:datetime   ) -> go.Figure:
    
    df = df[["Date","Rendement"]][df["Ticker"] == asset_ticker]
    df["Rendement"] /= 100
    df.set_index("Date",inplace=True)
    df = df.loc[start_date:end_date,:]

    fig = go.Figure(    data=go.Histogram(  histnorm="probability",
                                            x=df["Rendement"],
                                            name="Rendements",
                                            nbinsx=300  )   )
    
    fig.update_layout(  xaxis_title = "Rendements",
                        yaxis_title = "Probabilité" )
    
    return fig

def graph_volatility(   df:pd.DataFrame,
                        asset_ticker:Union[str,pd.Categorical],
                        start_date:datetime,
                        end_date:datetime   ) -> go.Figure:

    df = df[["Date","Volatilité_30j"]][df["Ticker"] == asset_ticker]
    df.set_index("Date",inplace=True)
    df = df.loc[start_date:end_date,:]

    fig = go.Figure(    data=go.Scatter(    x=df.index,
                                            y=df["Volatilité_30j"],
                                            name = str(asset_ticker),    )   )
    
    fig.update_layout(  xaxis_title = "Date",
                        yaxis_title = "Volatilité mensuelle"  )

    return fig

def graph_asset_vs_benchmark(   df:pd.DataFrame,
                                asset_ticker:Union[str,pd.Categorical],
                                benchmark_ticker:Union[str,pd.Categorical],
                                start_date:datetime,
                                end_date:datetime   ) -> go.Figure:
    df1 = df.copy()
    df1 = df1[["Date","Volatilité_30j","Rendement"]][df1["Ticker"] == asset_ticker]
    df1["Rendement"] /= 100
    df1.set_index("Date",inplace=True)
    df1 = df1.loc[start_date:end_date,:]
    mean_return = df1["Rendement"].rolling(30).mean().mean()
    mean_vol = df1["Volatilité_30j"].mean()

    df = df[["Date","Volatilité_30j","Rendement"]][df["Ticker"] == benchmark_ticker]
    df["Rendement"] /= 100
    df.set_index("Date",inplace=True)
    df = df.loc[start_date:end_date,:]
    mean_return_benchmark = df["Rendement"].rolling(30).mean().mean()
    mean_vol_benchmark = df["Volatilité_30j"].mean()

    fig = make_subplots(    rows=1, 
                            cols=2, 
                            subplot_titles=(    "Moyenne des moyennes des rendements", 
                                                "Moyenne des écart-types des rendements"    )   )

    fig.add_trace(  go.Bar  (   name=f"{asset_ticker}", 
                                x=["Actif"], 
                                y=[mean_return], 
                                marker_color="green"    ), 
                    row=1, 
                    col=1   )
    
    fig.add_trace(  go.Bar( name=f"{benchmark_ticker}", 
                            x=["Benchmark"], 
                            y=[mean_return_benchmark], 
                            marker_color="lightgreen"   ), 
                    row=1, 
                    col=1   )

    fig.add_trace(  go.Bar( name=f"{asset_ticker}", 
                            x=["Actif"], 
                            y=[mean_vol], 
                            marker_color="red"  ), 
                    row=1, 
                    col=2   )
    
    fig.add_trace(  go.Bar( name=f"{benchmark_ticker}", 
                            x=["Benchmark"], 
                            y=[mean_vol_benchmark], 
                            marker_color="salmon"   ), 
                    row=1, 
                    col=2   )

    fig.update_layout(  barmode="group",
                        yaxis_title="Valeur",
                        xaxis_title="Indicateur"    )

    return fig

def graph_price_asset_and_benchmark(    df:pd.DataFrame,
                                        asset_ticker:Union[str,pd.Categorical],
                                        benchmark_ticker:Union[str,pd.Categorical],
                                        start_date:datetime,
                                        end_date:datetime   ) -> go.Figure:

    df1 = df.copy()
    df1 = df1[["Date","Prix"]][df1["Ticker"] == asset_ticker]
    df1.set_index("Date",inplace=True)
    df1 = df1.loc[start_date:end_date,:]

    df = df[["Date","Prix"]][df["Ticker"] == benchmark_ticker]
    df.set_index("Date",inplace=True)
    df = df.loc[start_date:end_date,:]    

    fig = go.Figure(    data=go.Scatter(    x=df1.index,
                                            y=df1["Prix"],
                                            name = str(asset_ticker)    )   )

    fig.add_scatter(    x=df1.index,
                        y=df["Prix"],
                        name=str(benchmark_ticker)  )

    fig.update_layout(  xaxis_title = "Date",
                        yaxis_title = "Prix"    )
    
    return fig

def graph_corr( df:pd.DataFrame,
                asset_tickers:Union[str,pd.Categorical],
                start_date:datetime,
                end_date:datetime   ) -> go.Figure:
    
    df = df[df["Ticker"].isin(asset_tickers)]
    df = df.pivot_table(index="Date", columns="Ticker",values="Prix")
    df = df.loc[start_date:end_date]
    df = df.pct_change()
    df = df.corr()

    fig = go.Figure(    go.Heatmap( z=df.values,
                                    x=df.columns,
                                    y=df.index,
                                    colorscale='RdBu',
                                    zmin=-1,
                                    zmax=1,
                                    colorbar=dict(title="Corrélation")  )   )

    fig.update_layout(  xaxis_title="Ticker",
                        yaxis_title="Ticker"    )

    return fig

def graph_boxplot_vol(  df:pd.DataFrame,
                        asset_ticker:Union[str,pd.Categorical,list],
                        start_date:datetime,
                        end_date:datetime   ) -> go.Figure:
    
    asset_ticker = [asset_ticker] if not isinstance(asset_ticker,list) else asset_ticker

    fig = go.Figure()

    df1 = df.copy()
    for ticker in asset_ticker:

        df = df1[["Date","Volatilité_30j"]][df1["Ticker"] == ticker]
        df.set_index("Date",inplace=True)
        df = df.loc[start_date:end_date,:]

        fig.add_trace(  go.Box( y=df["Volatilité_30j"],
                                name=ticker,
                                boxmean=True    )   )
    
    fig.update_layout(  xaxis_title="Ticker",
                        yaxis_title="Volatilité"    )
    
    return fig

def graph_category_pie_chart(   df:pd.DataFrame,
                                asset_ticker:Union[str,pd.Categorical,list] ) -> go.Figure:

    df = df[["Ticker","Secteur","Benchmark","Type_actif"]][df["Ticker"].isin(asset_ticker)]
    df.drop_duplicates(inplace=True)

    type_counts = df["Type_actif"].value_counts()
    type_counts = type_counts[type_counts>0]
    sector_counts = df["Secteur"].value_counts()
    sector_counts = sector_counts[sector_counts>0]
    benchmark_counts = df["Benchmark"].value_counts()
    benchmark_counts = benchmark_counts[benchmark_counts>0]

    fig = make_subplots(    rows=1, 
                            cols=3,
                            subplot_titles=(    "Répartition des types d'actifs",
                                                "Répartition des secteurs",
                                                "Répartition des benchmarks"    ),
                            specs=[ [   {'type': 'domain'},
                                        {'type': 'domain'}, 
                                        {'type': 'domain'}  ]   ]   )

    fig.add_pie(labels=type_counts.index, values=type_counts.values, row=1, col=1)
    fig.add_pie(labels=sector_counts.index, values=sector_counts.values, row=1, col=2)
    fig.add_pie(labels=benchmark_counts.index, values=benchmark_counts.values, row=1, col=3)

    return fig
