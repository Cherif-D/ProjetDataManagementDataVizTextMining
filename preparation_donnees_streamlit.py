#!/usr/bin/env python
# coding: utf-8

# Phases de préparation des données
# ===

# Importation des packages
# ---

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os


# Lecture du fichier csv téléchargé et informations sur la base de données
# --

# In[2]:


df = pd.read_csv("Data/donnees_financieres_300k_lignes.csv")
df


# In[3]:


print(df.head(10))  # Affiche les 5 premières lignes


# In[4]:


df.columns


# In[5]:


df.index


# In[6]:


df.info()


# In[8]:


df['Date'] = pd.to_datetime(df['Date'])


# In[9]:


df.info()


# In[10]:


df['Ticker'] = df['Ticker'].astype('string')  # Conversion en string


# In[11]:


df.info()


# In[12]:


df.shape


# In[13]:


df.describe()  # Affiche les statistiques descriptives
#df.describe(include='all')  # Inclut les colonnes non numériques


# Analyse exploiratoire des données
# --

# In[14]:


#Vérification des doublons

print("🔍 Nombre de doublons :", df.duplicated().sum()) 



# In[15]:


# vérification de la plage de dates et de la cohérence des dates
# Date minimale et maximale globale du DataFrame
print(f"Date minimale globale : {df['Date'].min()}")
print(f"Date maximale globale : {df['Date'].max()}")

# Date minimale et maximale par ticker (très utile pour voir les débuts d'historique)
print("\nDates minimales et maximales par Ticker :")
print(df.groupby('Ticker')['Date'].agg(['min', 'max']))



# Normal comme résultat car la prémière date de trading est le 03/01/2000 même si le téléchargement commence le 01/01/2000


# In[16]:


# Compter le nombre de jours uniques pour chaque ticker
print("\nNombre de jours d'historique par Ticker :")
print(df.groupby('Ticker')['Date'].nunique().sort_values(ascending=False))


# In[17]:


# Vérification des valeurs manquantes
# Analyse complète des NA
missing_data = df.isnull().sum().sort_values(ascending=False)
missing_percent = (df.isnull().mean()*100).round(2)

print("Valeurs manquantes par colonne:")
print(missing_data[missing_data > 0])  # Affiche seulement les colonnes avec NA

# Visualisation des NA (avec une heatmap)


plt.figure(figsize=(10,6))
sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
plt.title("Carte des valeurs manquantes")
plt.show()
#sortie du graphique : Une heatmap où :

 #Les lignes représentent les observations

# Les colonnes représentent les variables (Date, Ticker, Prix)

# Les zones jaunes/vertes montrent les valeurs manquantes (Prix)

# Les zones violettes montrent les valeurs présentes


# In[18]:


# 1. Calcul des valeurs manquantes par ticker
missing_by_ticker = df.groupby('Ticker')['Prix'].agg([
    ('total_manquants', lambda x: x.isnull().sum()),
    ('total_observations', 'count'),
    ('pourcentage_manquants', lambda x: round(x.isnull().mean()*100, 2))
])

# 2. Filtrage et tri des tickers avec des NA
missing_tickers = missing_by_ticker[missing_by_ticker['total_manquants'] > 0]\
                  .sort_values('pourcentage_manquants', ascending=False)

# 3. Affichage des résultats
print("📊 Analyse détaillée des valeurs manquantes par actif:")
print(f"• {len(missing_tickers)} actifs sur {len(missing_by_ticker)} contiennent des NA")
print(f"• Moyenne de NA par actif: {missing_tickers['pourcentage_manquants'].mean():.1f}%")
print("\nTop 10 des actifs avec le plus de valeurs manquantes:")
print(missing_tickers.head(10))

# 4. Visualisation
plt.figure(figsize=(12, 8))

# Histogramme des pourcentages de NA
plt.subplot(2, 1, 1)
sns.histplot(data=missing_tickers, x='pourcentage_manquants', bins=30)
plt.title('Distribution des pourcentages de valeurs manquantes par actif')
plt.xlabel('% de valeurs manquantes')
plt.ylabel('Nombre d\'actifs')

# Top 15 des actifs avec le plus de NA
plt.subplot(2, 1, 2)
missing_tickers.head(15)['pourcentage_manquants'].plot(kind='barh', color='salmon')
plt.title('Top 15 des actifs avec le plus de valeurs manquantes')
plt.xlabel('% de valeurs manquantes')
plt.tight_layout()
plt.show()

# 5. Analyse temporelle des NA (exemple pour un ticker problématique)
if not missing_tickers.empty:
    sample_ticker = missing_tickers.index[0]
    ticker_data = df[df['Ticker'] == sample_ticker][['Date', 'Prix']].set_index('Date')
    
    print(f"\n🔍 Analyse temporelle pour {sample_ticker}:")
    plt.figure(figsize=(12, 4))
    plt.plot(ticker_data['Prix'], label='Prix')
    plt.scatter(ticker_data[ticker_data['Prix'].isnull()].index, 
                [0]*len(ticker_data[ticker_data['Prix'].isnull()]), 
                color='red', label='Valeurs manquantes')
    plt.title(f'Emplacement des NA pour {sample_ticker}')
    plt.legend()
    plt.show()


# Pic 0-20% :
# 
# 35 actifs ont peu de NA (<20%)
# 
# Ce sont les actifs les plus fiables (ex: grandes entreprises cotées depuis longtemps)
# 
# Queue droite :
# 
# Quelques outliers (5-10 actifs) ont 40-60% de NA
# 
# Probablement :
# 
# Cryptomonnaies récentes
# 
# Entreprises ayant fait faillite.

# In[19]:


# reserver aux autres qui feront la visualisation
# Première et dernière date disponible par actif
coverage = df.groupby('Ticker')['Date'].agg(['min', 'max', 'count'])
coverage['duration'] = coverage['max'] - coverage['min']
print("\nCouverture temporelle par actif:")
print(coverage.sort_values('duration', ascending=False))

# Visualisation de la couverture (nécessite plotly pour une meilleure interactivité)
fig = px.scatter(coverage.reset_index(), 
                 x='min', y='Ticker', 
                 size='count',
                 title="Couverture temporelle des actifs")
import plotly.io as pio
pio.renderers.default = 'browser'
fig.show()


# Statistiques descriptives avant le traitement des valeurs manquantes
# ----

# In[20]:


print("📊 Statistiques AVANT nettoyage des valeurs manquantes :")
print(df['Prix'].describe())

print("\n🔍 Nombre de valeurs manquantes :", df['Prix'].isna().sum())
print(f"🔎 Nombre de lignes : {df.shape[0]}")
print(f"🔎 Nombre d'actifs : {df['Ticker'].nunique()}")


# Phases de nettoyage des valeurs manquantes des doublons et justifications
# ===

# Les doublons n’ont aucun intérêt analytique ici. Chaque ligne représente une observation unique d’un prix à une date pour un actif donné. Nous les supprimons pour garantir l’unicité des observations.

# In[21]:


# 🔎 1. SUPPRESSION DES DOUBLONS
print("Nombre de doublons avant suppression :", df.duplicated().sum())
df.drop_duplicates(inplace=True)
print("✔️ Doublons supprimés. Nombre de lignes restantes :", df.shape[0])


# 
# Tous les actifs ne sont pas comparables :
# 
# Les cryptomonnaies sont très récentes → historique très court
# 
# Les ETF peuvent aussi avoir été créés tardivement
# 
# Les actions comme TSLA ou META n’étaient pas cotées avant les années 2010
# 
# 🔍 Appliquer un seuil unique (ex. 30%) serait trop rigide et éliminerait des actifs pertinents
# 
# ✅ On adopte une stratégie différenciée selon le type d’actif :
# 
# Type d’actif	Seuil de suppression
# Crypto	> 50 % de NaN
# Action	> 60 % de NaN
# ETF	> 60 % de NaN

# In[28]:


# Crée un dictionnaire manuel pour mapper les tickers à leur catégorie d’actif
type_map = {
    # 🔶 Cryptomonnaies
    'BTC-USD': 'Crypto',     # Bitcoin
    'ETH-USD': 'Crypto',     # Ethereum
    'XRP-USD': 'Crypto',     # Ripple
    'LTC-USD': 'Crypto',     # Litecoin

    # 🔷 ETF
    'SPY': 'ETF',            # S&P 500 ETF
    'QQQ': 'ETF',            # Nasdaq-100 ETF
    'DIA': 'ETF',            # Dow Jones ETF
    'TLT': 'ETF',            # Treasury Bonds ETF (20+ years)
    'IEF': 'ETF',            # Treasury Bonds ETF (7–10 years)
    'GLD': 'ETF',            # Gold ETF
    'SLV': 'ETF',            # Silver ETF

    # 🔵 Actions technologiques / GAFAM
    'AAPL': 'Action',        # Apple – Technologie
    'MSFT': 'Action',        # Microsoft – Technologie
    'GOOGL': 'Action',       # Alphabet/Google – Technologie
    'META': 'Action',        # Meta (Facebook) – Réseaux sociaux
    'AMZN': 'Action',        # Amazon – E-commerce & Cloud
    'NFLX': 'Action',        # Netflix – Streaming
    'NVDA': 'Action',        # Nvidia – Semi-conducteurs
    'ADBE': 'Action',        # Adobe – Logiciels

    # 🔵 Actions financières
    'JPM': 'Action',         # JPMorgan Chase – Banque
    'BAC': 'Action',         # Bank of America – Banque
    'WFC': 'Action',         # Wells Fargo – Banque
    'GS': 'Action',          # Goldman Sachs – Banque d'investissement
    'MS': 'Action',          # Morgan Stanley – Banque d'investissement
    'V': 'Action',           # Visa – Paiements
    'MA': 'Action',          # Mastercard – Paiements

    # 🔵 Actions industrielles
    'GE': 'Action',          # General Electric – Industrie
    'CAT': 'Action',         # Caterpillar – Machines industrielles
    'BA': 'Action',          # Boeing – Aéronautique

    # 🔵 Actions énergie
    'XOM': 'Action',         # ExxonMobil – Pétrole
    'CVX': 'Action',         # Chevron – Pétrole

    # 🔵 Actions santé
    'JNJ': 'Action',         # Johnson & Johnson – Santé
    'LLY': 'Action',         # Eli Lilly – Santé
    'PFE': 'Action',         # Pfizer – Pharmaceutique
    'MRK': 'Action',         # Merck & Co – Pharmaceutique
    'ABBV': 'Action',        # AbbVie – Biotechnologie
    'UNH': 'Action',         # UnitedHealth – Assurance santé
    'TMO': 'Action',         # Thermo Fisher – Biotechnologie

    # 🔵 Actions consommation
    'WMT': 'Action',         # Walmart – Distribution
    'HD': 'Action',          # Home Depot – Bricolage
    'COST': 'Action',        # Costco – Grande distribution
    'DIS': 'Action',         # Disney – Divertissement
    'NKE': 'Action',         # Nike – Équipement sportif
    'KO': 'Action',          # Coca-Cola – Boissons
    'PEP': 'Action',         # PepsiCo – Boissons et snacks
    'PG': 'Action',          # Procter & Gamble – Produits ménagers

    # 🔵 Actions télécoms & communication
    'VZ': 'Action',          # Verizon – Télécom
    'TMUS': 'Action',        # T-Mobile US – Télécom
    'CMCSA': 'Action',       # Comcast – Télécom/Câble

    # 🔵 Actions technologiques (divers)
    'CRM': 'Action',         # Salesforce – Logiciels
    'CSCO': 'Action',        # Cisco – Réseaux
    'TXN': 'Action',         # Texas Instruments – Semi-conducteurs
    'AVGO': 'Action',        # Broadcom – Semi-conducteurs
    'DHR': 'Action',          # Danaher – Santé/Instrumentation
    # 🔵 Actions automobiles
    'TSLA': 'Action',     # Tesla – Véhicules électriques / Technologie

}



# Pour ne pas modifier le DataFrame original (df), on crée une copie indépendante.
# On y ajoutera la colonne Type_actif pour appliquer notre stratégie de filtrage.

# In[29]:


# On travaille sur une copie pour préserver le DataFrame original
df_copy = df.copy()

# Ajoute une colonne Type_actif grâce au mapping manuel
df_copy['Type_actif'] = df_copy['Ticker'].map(type_map)


# In[30]:


# Extraction des tickers dont le Type_actif est manquant
tickers_manquants = df_copy[df_copy['Type_actif'].isna()]['Ticker'].unique()

# Affichage du résultat
print(f"⚠️ {len(tickers_manquants)} ticker(s) n'ont pas encore de Type_actif défini :")
print(sorted(tickers_manquants))


# In[31]:


# Conversion de la colonne 'Date' au format datetime
df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce')

# Conversion des colonnes catégorielles en string propre
df_copy['Ticker'] = df_copy['Ticker'].astype('string')
df_copy['Type_actif'] = df_copy['Type_actif'].astype('string')

print(df_copy.info())


# In[32]:


df_copy


# On récupère les résultats de l’analyse des valeurs manquantes (missing_tickers)
# On y ajoute aussi le type d’actif pour pouvoir filtrer selon les règles définies.

# In[33]:


df_na = missing_tickers.copy()
df_na['Type_actif'] = df_na.index.map(type_map)


# Application de règles spécifiques par type d’actif :
# 
# Suppression des cryptos avec >50 % de NaN
# 
# Suppression des actions et ETF avec >60 % de NaN

# In[34]:


# Définition des conditions selon le type d’actif
condition_cryptos = (df_na['Type_actif'] == 'Crypto') & (df_na['pourcentage_manquants'] > 50)
condition_actions = (df_na['Type_actif'] == 'Action') & (df_na['pourcentage_manquants'] > 60)
condition_etf = (df_na['Type_actif'] == 'ETF') & (df_na['pourcentage_manquants'] > 60)

# Liste finale des tickers à exclure
tickers_exclus = df_na[condition_cryptos | condition_actions | condition_etf]
actifs_supprimes = tickers_exclus.index.tolist()


# On supprime uniquement les lignes correspondant aux tickers trop incomplets,
# et on conserve les autres dans une nouvelle version propre : df_clean.

# In[35]:


# Création du DataFrame nettoyé (tickers filtrés)
df_clean = df_copy[~df_copy['Ticker'].isin(actifs_supprimes)].copy()


# On applique un double remplissage (ffill() + bfill()) :
# 
# ffill() pour remplir les trous par la dernière valeur connue (logique financière)
# 
# bfill() pour compléter les valeurs initiales manquantes si aucune valeur connue avant

# In[36]:


# Tri nécessaire avant le remplissage temporel
df_clean.sort_values(by=['Ticker', 'Date'], inplace=True)

# Remplissage par actif
df_clean['Prix'] = df_clean.groupby('Ticker')['Prix'].transform(lambda x: x.ffill().bfill())


# In[38]:


print("🧼 Actifs supprimés selon stratégie personnalisée :\n")
print(tickers_exclus[['Type_actif', 'total_manquants', 'pourcentage_manquants']])

print(f"\n❗ Nombre total d'actifs supprimés : {len(actifs_supprimes)}")
print("🔻 Tickeurs supprimés :")
print(", ".join(actifs_supprimes))

print(f"\n✅ Données prêtes pour analyse avec {df_clean.shape[0]} lignes et {df_clean['Ticker'].nunique()} actifs conservés.")


# In[39]:


print("📊 Statistiques APRÈS nettoyage des valeurs manquantes :")
print(df_clean['Prix'].describe())

print("\n🧼 Nombre de valeurs manquantes restantes :", df_clean['Prix'].isna().sum())
print(f"✅ Nombre de lignes restantes : {df_clean.shape[0]}")
print(f"✅ Nombre d'actifs conservés : {df_clean['Ticker'].nunique()}")


# In[40]:


fig, ax = plt.subplots(1, 2, figsize=(15, 5))
sns.boxplot(data=df, x='Prix', ax=ax[0]).set_title("AVANT nettoyage")
sns.boxplot(data=df_clean, x='Prix', ax=ax[1]).set_title("APRÈS nettoyage")
plt.show()


# Difficile à interpréter 

# In[41]:


# --- Visualisation des Distributions de Prix (AVANT vs APRÈS nettoyage) ---
print("\n--- Visualisation des Distributions de Prix (AVANT vs APRÈS nettoyage) avec KDE et échelle Log ---")

# Utilisez np.log1p sur les prix, en gérant les NaN pour la visualisation
# (les NaN sont déjà gérés dans df_clean, mais on les retire pour df pour la visualisation)
prix_avant_log = np.log1p(df['Prix'].dropna())
prix_apres_log = np.log1p(df_clean['Prix'].dropna())

plt.figure(figsize=(12, 7))

# Superposition des deux distributions pour une comparaison directe
sns.kdeplot(prix_avant_log, fill=True, color='skyblue', label='AVANT Nettoyage', alpha=0.6)
sns.kdeplot(prix_apres_log, fill=True, color='lightgreen', label='APRÈS Nettoyage', alpha=0.6)

plt.title('Comparaison des Distributions de Prix (échelle log) - AVANT vs APRÈS Nettoyage')
plt.xlabel('Log(1 + Prix)')
plt.ylabel('Densité')
plt.legend()
plt.grid(True)
plt.show()

print("\nCommentaire sur le graphique KDE :")
print("Ce graphique de densité en échelle logarithmique permet de mieux visualiser la forme de la distribution des prix avant et après le nettoyage.")
print("La transformation logarithmique compresse les grandes valeurs et étire les petites, rendant les différences subtiles plus apparentes.")
print("Vous pouvez observer si la forme de la distribution a changé, si des modes ont disparu ou sont apparus, ou si la dispersion s'est modifiée suite à la suppression des actifs avec de nombreux NaN.")


# Commentaire sur la Comparaison des Distributions de Prix (AVANT vs APRÈS Nettoyage)
# Ce graphique montre comment les prix de nos actifs sont répartis, avant et après que nous ayons nettoyé les données. Comme les prix peuvent être très différents (certains très petits, d'autres très grands comme le Bitcoin), nous utilisons une échelle spéciale appelée "échelle logarithmique" sur l'axe des prix. Cela nous permet de bien voir toutes les valeurs, petites et grandes.
# 
# Courbe bleue ("AVANT Nettoyage") : Elle représente la répartition des prix bruts, tels qu'ils étaient quand nous avons téléchargé les données.
# Courbe verte ("APRÈS Nettoyage") : Elle représente la répartition des prix après que nous ayons corrigé les données manquantes (par exemple, en supprimant les actifs qui n'existaient pas au début de notre période d'étude parce qu'ils avaient trop de données manquantes à ces dates).
# Ce que nous pouvons observer :
# 
# Forme Générale Similaire : Les deux courbes se ressemblent beaucoup. Cela veut dire que notre nettoyage n'a pas radicalement changé la façon dont les prix sont répartis dans l'ensemble. La majorité des prix se regroupent toujours autour des mêmes valeurs (autour de 3 à 4 sur l'échelle log, ce qui correspond à des prix moyens après transformation).
# Légères différences :
# La courbe verte ("APRÈS Nettoyage") est un peu plus concentrée et a un pic légèrement plus élevé autour de la valeur moyenne. Cela est probablement dû au fait que nous avons supprimé certains actifs qui avaient beaucoup de données manquantes, surtout ceux qui n'existaient que sur une courte période ou qui avaient des prix très bas au début de leur historique. En les retirant, les données restantes sont un peu plus "homogènes" et mieux représentées.
# On peut voir que la courbe bleue a une "queue" un peu plus large à l'extrême gauche (autour de 0-1 sur l'échelle log) qui est moins présente dans la courbe verte. Cela pourrait indiquer que le nettoyage a permis de retirer des prix très bas associés à des données incomplètes ou peu représentatives.
# En résumé, le nettoyage des données n'a pas bouleversé la distribution générale des prix, mais il l'a rendue un peu plus précise et cohérente en enlevant les actifs qui rendaient l'analyse plus difficile à cause de leurs nombreuses valeurs manquantes.

# In[ ]:


# Nom du dossier pour sauvegarder le fichier
output_dir = 'Data'

# Nom du fichier CSV pour les données nettoyées
output_filename = 'donnees_financieres_clean.csv'

# Chemin complet vers le fichier de sortie
output_path = os.path.join(output_dir, output_filename)

# Vérifier si le dossier existe, sinon le créer
# exist_ok=True évite une erreur si le dossier existe déjà
os.makedirs(output_dir, exist_ok=True)

# Enregistrer le DataFrame df_clean en tant que fichier CSV
# index=True est important pour inclure l'index (qui contient les dates) dans le fichier CSV
df_clean.to_csv(output_path, index=True)

print(f"Le fichier '{output_filename}' a été enregistré avec succès dans le dossier '{output_dir}'.")
print(f"Chemin complet : {os.path.abspath(output_path)}")


# Phase de création de variables pertinentes pour l’analyse & Streamlit
# ===

# Créer des variables qui :
# 
# 🧭 permettent une exploration intuitive dans Streamlit
# 
# 📊 facilitent les visualisations dynamiques (filtres, regroupements)
# 
# 🔍 aident à révéler des tendances et anomalies sur les actifs

# Variable secteur : Le type d’actif (Action, Crypto, ETF) est trop général pour les analyses comparatives.
# On crée une variable Secteur pour regrouper les entreprises selon leur activité (technologie, santé, énergie...).
# Cela permettra :
# 
# de filtrer dans Streamlit selon le secteur,
# 
# de visualiser la performance moyenne ou la volatilité par secteur,
# 
# d’identifier des secteurs plus risqués ou plus stables.

# In[71]:


# 🧬 1. Copier le DataFrame de base pour enrichissement
df_enrichi = df_clean.copy()


# 🧭 2. Appliquer le mapping secteur à partir du dictionnaire
secteur_map = {
    'AAPL': 'Technologie', 'MSFT': 'Technologie', 'GOOGL': 'Technologie', 'META': 'Technologie', 'ADBE': 'Technologie', 'CRM': 'Technologie',
    'AMZN': 'E-commerce', 'NFLX': 'Divertissement', 'DIS': 'Divertissement',
    'NVDA': 'Semi-conducteurs', 'AVGO': 'Semi-conducteurs', 'TXN': 'Semi-conducteurs', 'CSCO': 'Technologie réseaux',
    'TSLA': 'Automobile', 'CAT': 'Industrie', 'GE': 'Industrie', 'BA': 'Aéronautique', 'DHR': 'Matériel médical',
    'JNJ': 'Santé', 'PFE': 'Santé', 'MRK': 'Santé', 'LLY': 'Santé', 'ABBV': 'Biotechnologie', 'TMO': 'Biotechnologie', 'UNH': 'Assurance santé',
    'JPM': 'Banque', 'BAC': 'Banque', 'WFC': 'Banque', 'GS': 'Banque', 'MS': 'Banque', 'V': 'Paiements', 'MA': 'Paiements',
    'WMT': 'Grande distribution', 'COST': 'Grande distribution', 'HD': 'Bricolage',
    'NKE': 'Consommation', 'PG': 'Consommation', 'KO': 'Consommation', 'PEP': 'Consommation',
    'SPY': 'ETF', 'QQQ': 'ETF', 'DIA': 'ETF', 'TLT': 'ETF', 'IEF': 'ETF', 'GLD': 'ETF', 'SLV': 'ETF',
    'BTC-USD': 'Crypto', 'ETH-USD': 'Crypto', 'XRP-USD': 'Crypto', 'LTC-USD': 'Crypto',
    'CMCSA': 'Télécom', 'VZ': 'Télécom', 'TMUS': 'Télécom',
    'CVX': 'Énergie', 'XOM': 'Énergie'
}

df_enrichi['Secteur'] = df_enrichi['Ticker'].map(secteur_map).astype('string')


# In[72]:


# 🔎 3. Vérifier les valeurs manquantes dans la colonne 'Secteur'
secteurs_vides = df_enrichi[df_enrichi['Secteur'].isna()]['Ticker'].unique()

if len(secteurs_vides) == 0:
    print("✅ Tous les tickers ont un secteur attribué.")
else:
    print(f"⚠️ {len(secteurs_vides)} ticker(s) n'ont pas de secteur défini :")
    print(sorted(secteurs_vides))


# Variable "Rendement" (Returns)
# 
# Objectif : Calculer le rendement quotidien pour analyser la performance.
# Définition : variation relative du prix entre deux jours consécutifs pour un même actif

# In[73]:


# 🧮 4. Calculer le rendement quotidien en pourcentage
df_enrichi.sort_values(['Ticker', 'Date'], inplace=True)  # Tri nécessaire
df_enrichi['Rendement'] = df_enrichi.groupby('Ticker')['Prix'].pct_change() * 100  # En %

print("✅ Variable 'Rendement' (en %) créée avec succès.")


# In[74]:


df_enrichi


#  Vérifier le nombre de valeurs manquantes dans Rendement
# Donc, nombre valeurs manquantes attendu ≈ nombre de tickers dans le dataset.

# In[75]:


nb_na_rendement = df_enrichi['Rendement'].isna().sum()
nb_total = len(df_enrichi)

print(f"📊 Nombre de rendements manquants : {nb_na_rendement} / {nb_total} lignes")

pourcentage_na = (nb_na_rendement / nb_total) * 100
print(f"🔎 Pourcentage de valeurs manquantes dans 'Rendement' : {pourcentage_na:.2f}%")


# Création de la variable Année
# 📌 Justification :
# Extraire des composantes temporelles permet d'analyser les données à différentes échelles.
# La colonne Année est essentielle pour :
# 
# Étudier l’évolution des performances ou des risques année par année ;
# 
# Construire des moyennes ou courbes annuelles dans Streamlit ;
# 
# Appliquer des filtres temporels dans des tableaux ou des graphiques.

# In[76]:


# 🕓 S'assurer que la colonne 'Date' est bien au format datetime
df_enrichi['Date'] = pd.to_datetime(df_enrichi['Date'], errors='coerce')

# 📅 Création de la colonne 'Année'
df_enrichi['Année'] = df_enrichi['Date'].dt.year

# ✅ Vérification que toutes les années sont bien remplies
nb_na_annee = df_enrichi['Année'].isna().sum()

if nb_na_annee == 0:
    print("✅ La colonne 'Année' a été ajoutée avec succès, sans valeur manquante.")
else:
    print(f"⚠️ Attention : {nb_na_annee} valeur(s) manquante(s) dans la colonne 'Année'.")


# In[77]:


df_enrichi


# Création de deux colonnes de volatilité
# 
# La volatilité 30 jours est utile pour détecter rapidement les périodes de forte instabilité.
# 
# La version annualisée est plus facilement comparable entre actifs, car c’est une norme du secteur financier.
# 
# La volatilité quotidienne moyenne permet de :comparer le risque moyen historique des actifs (Crypto vs Actions vs ETF),générer un classement de stabilité des actifs,tracer un barplot par secteur ou par capitalisation dans Streamlit.

# In[78]:


# ✅ 1. Volatilité glissante sur 30 jours (en % journalier)
df_enrichi['Volatilité_30j'] = df_enrichi.groupby('Ticker')['Rendement'].transform(
    lambda x: x.rolling(window=30).std()
)

# ✅ 2. Volatilité annualisée sur 30 jours
df_enrichi['Volatilité_30j_annualisée'] = df_enrichi['Volatilité_30j'] * np.sqrt(252)

# ✅ 3. Volatilité quotidienne globale par actif
volatilite_quotidienne = df_enrichi.groupby('Ticker')['Rendement'].std()

# ➕ On la réinjecte dans le DataFrame principal (même valeur répétée par ticker)
df_enrichi['Volatilité_quotidienne'] = df_enrichi['Ticker'].map(volatilite_quotidienne)

print("✅ Variables 'Volatilité_30j', 'Volatilité_30j_annualisée' et 'Volatilité_quotidienne' ajoutées avec succès.")


# In[79]:


df_enrichi


# Variable : Performance relative actif vs benchmark
# 
#  Objectif :
# Comparer la performance quotidienne d’un actif à un benchmark de marché adapté pour voir si l’actif surperforme ou sous-performe en pourcentage par rapport au marché.
# 
# Type d’actif / Secteur	Benchmark recommandé
# 📈 Actions (US large-cap)	SPY
# 💻 Tech / Nasdaq	QQQ
# 🛢️ Énergie / Industrie	DIA
# 🏦 Obligations longues	TLT
# 💰 Obligations courtes	IEF
# 🪙 Crypto-monnaies	BTC-USD (optionnel)
# 🥇 Or / Argent / matières	GLD ou SLV
# 
# Créer une variable Performance_vs_Benchmark dynamique, qui :
# 
# 🔁 Compare chaque actif à son benchmark adapté (et pas toujours SPY),
# 
# 🎯 Donne plus de sens aux classements dans Streamlit (une action tech comparée au Nasdaq, pas au Dow Jones !).

# In[80]:


# 📊 Association des actifs à leur benchmark logique
benchmark_map = {
    # Actions Tech → QQQ
    'AAPL': 'QQQ', 'MSFT': 'QQQ', 'GOOGL': 'QQQ', 'META': 'QQQ', 'AMZN': 'QQQ', 'NVDA': 'QQQ', 'ADBE': 'QQQ', 'CRM': 'QQQ',

    # Actions industrielles ou Dow Jones → DIA
    'BA': 'DIA', 'CAT': 'DIA', 'GE': 'DIA',

    # Santé & large-cap divers → SPY
    'JNJ': 'SPY', 'PFE': 'SPY', 'MRK': 'SPY', 'LLY': 'SPY', 'UNH': 'SPY', 'TMO': 'SPY',
    'PG': 'SPY', 'KO': 'SPY', 'PEP': 'SPY', 'DIS': 'SPY', 'NKE': 'SPY',
    'JPM': 'SPY', 'BAC': 'SPY', 'WFC': 'SPY', 'GS': 'SPY', 'MS': 'SPY', 'V': 'SPY', 'MA': 'SPY',
    'WMT': 'SPY', 'HD': 'SPY', 'COST': 'SPY', 'TSLA': 'SPY',

    # Obligations longues → TLT
    'TLT': 'TLT',

    # Obligations courtes → IEF
    'IEF': 'IEF',

    # Matières premières
    'GLD': 'GLD', 'SLV': 'SLV',

    # Crypto → BTC comme référence
    'ETH-USD': 'BTC-USD', 'XRP-USD': 'BTC-USD', 'LTC-USD': 'BTC-USD',
    'BTC-USD': 'BTC-USD',

    # Benchmarks eux-mêmes → 100%
    'SPY': 'SPY', 'QQQ': 'QQQ', 'DIA': 'DIA',
    
     # 🔬 Biotechnologie / Santé → SPY
    'ABBV': 'SPY',      # AbbVie – Biotech large-cap

    # ⚙️ Semi-conducteurs → QQQ
    'AVGO': 'QQQ',      # Broadcom – Tech / Semi
    'TXN': 'QQQ',       # Texas Instruments – Semi
    'CSCO': 'QQQ',      # Cisco – Réseaux

    # 📺 Communication / Streaming → QQQ
    'NFLX': 'QQQ',      # Netflix – Streaming (tech orientée consommation)

    # 🏭 Instrumentation / Santé → SPY
    'DHR': 'SPY',       # Danaher – Santé/Instrumentation

    # 📡 Télécoms → DIA ou SPY selon préférence (ici SPY pour uniformité)
    'CMCSA': 'SPY',     # Comcast – Télécom
    'VZ': 'SPY',        # Verizon – Télécom
    'TMUS': 'SPY',      # T-Mobile – Télécom

    # 🛢️ Énergie → DIA ou SPY (ici SPY pour large-cap classique)
    'XOM': 'SPY',       # ExxonMobil – Pétrole
    'CVX': 'SPY',       # Chevron – Pétrole
}


# In[81]:


# ➕ Ajout d'une colonne qui contient le benchmark adapté pour chaque ligne
df_enrichi['Benchmark'] = df_enrichi['Ticker'].map(benchmark_map)

# 📈 Création d’un dictionnaire avec les prix de chaque benchmark
benchmark_prices = df_enrichi[df_enrichi['Ticker'].isin(set(benchmark_map.values()))]
benchmark_series = benchmark_prices.pivot(index='Date', columns='Ticker', values='Prix')


# 🧮 Calcul dynamique par ligne
df_enrichi['Performance_vs_Benchmark'] = df_enrichi.apply(
    lambda row: (row['Prix'] / benchmark_series.loc[row['Date'], row['Benchmark']] * 100)
    if pd.notnull(row['Benchmark']) and row['Ticker'] != row['Benchmark']
    else 100,  # Benchmark lui-même = 100
    axis=1
)

print("✅ Variable 'Performance_vs_Benchmark' ajoutée avec succès.")



# In[82]:


# 1. Liste de tous les tickers de ton type_map
type_map_keys = set(type_map.keys())

# 2. Ton benchmark_map (doit être défini en amont comme dans la réponse précédente)
benchmark_map_keys = set(benchmark_map.keys())

# 3. Vérification des tickers manquants
tickers_sans_benchmark = sorted(type_map_keys - benchmark_map_keys)

if not tickers_sans_benchmark:
    print("✅ Tous les tickers de type_map ont un benchmark défini dans benchmark_map.")
else:
    print(f"❌ {len(tickers_sans_benchmark)} ticker(s) n'ont PAS de benchmark dans benchmark_map :")
    print(tickers_sans_benchmark)


# In[83]:


df_enrichi


# In[84]:


df_enrichi.columns


# In[85]:


# 🔄 Création de la version finale pour Streamlit
dataframe_final_pret_pour_streamlit = df_enrichi.copy()

# 💾 Sauvegarde dans le dossier 'Data'
dataframe_final_pret_pour_streamlit.to_csv("Data/dataframe_final_pret_pour_streamlit.csv", index=False)

print("✅ DataFrame sauvegardé sous le nom 'dataframe_final_pret_pour_streamlit.csv' dans le dossier 'Data'.")

