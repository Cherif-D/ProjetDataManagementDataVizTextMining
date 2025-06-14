import pandas as pd
from datetime import datetime

ticker_to_name = {
    'AAPL': 'Apple Inc.',
    'ABBV': 'AbbVie Inc.',
    'ADBE': 'Adobe Inc.',
    'AMZN': 'Amazon.com Inc.',
    'AVGO': 'Broadcom Inc.',
    'BA': 'Boeing Co.',
    'BAC': 'Bank of America Corp.',
    'BTC-USD': 'Bitcoin',
    'CAT': 'Caterpillar Inc.',
    'CMCSA': 'Comcast Corp.',
    'COST': 'Costco Wholesale Corp.',
    'CRM': 'Salesforce Inc.',
    'CSCO': 'Cisco Systems Inc.',
    'CVX': 'Chevron Corp.',
    'DHR': 'Danaher Corp.',
    'DIA': 'SPDR Dow Jones Industrial Average ETF',
    'DIS': 'The Walt Disney Company',
    'GE': 'General Electric Co.',
    'GLD': 'SPDR Gold Shares',
    'GOOGL': 'Alphabet Inc. (Class A)',
    'GS': 'Goldman Sachs Group Inc.',
    'HD': 'Home Depot Inc.',
    'IEF': 'iShares 7-10 Year Treasury Bond ETF',
    'JNJ': 'Johnson & Johnson',
    'JPM': 'JPMorgan Chase & Co.',
    'KO': 'Coca-Cola Co.',
    'LLY': 'Eli Lilly and Co.',
    'LTC-USD': 'Litecoin',
    'MA': 'Mastercard Inc.',
    'META': 'Meta Platforms Inc.',
    'MRK': 'Merck & Co. Inc.',
    'MS': 'Morgan Stanley',
    'MSFT': 'Microsoft Corp.',
    'NFLX': 'Netflix Inc.',
    'NKE': 'Nike Inc.',
    'NVDA': 'NVIDIA Corp.',
    'PEP': 'PepsiCo Inc.',
    'PFE': 'Pfizer Inc.',
    'PG': 'Procter & Gamble Co.',
    'QQQ': 'Invesco QQQ Trust',
    'SLV': 'iShares Silver Trust',
    'SPY': 'SPDR S&P 500 ETF Trust',
    'TLT': 'iShares 20+ Year Treasury Bond ETF',
    'TMO': 'Thermo Fisher Scientific Inc.',
    'TMUS': 'T-Mobile US Inc.',
    'TSLA': 'Tesla Inc.',
    'TXN': 'Texas Instruments Inc.',
    'UNH': 'UnitedHealth Group Inc.',
    'V': 'Visa Inc.',
    'VZ': 'Verizon Communications Inc.',
    'WFC': 'Wells Fargo & Co.',
    'WMT': 'Walmart Inc.',
    'XOM': 'Exxon Mobil Corp.'
}

name_to_ticker = {v: k for k, v in ticker_to_name.items()}

def adjust_to_last_friday(date:datetime) -> datetime:
    weekday = date.weekday()
    if weekday == 5:
        return date - pd.Timedelta(days=1)
    elif weekday == 6:
        return date - pd.Timedelta(days=2)
    return date

compared_by = { "Actif":"Ticker",
                "Type d'actif":"Type_actif",
                "Secteur":"Secteur",
                "Benchmark":"Benchmark" }

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

secteur_map = {
    'AAPL': 'Technologie', 
    'MSFT': 'Technologie', 
    'GOOGL': 'Technologie', 
    'META': 'Technologie', 
    'ADBE': 'Technologie', 
    'CRM': 'Technologie',
    'AMZN': 'E-commerce', 
    'NFLX': 'Divertissement', 
    'DIS': 'Divertissement',
    'NVDA': 'Semi-conducteurs', 
    'AVGO': 'Semi-conducteurs', 
    'TXN': 'Semi-conducteurs', 
    'CSCO': 'Technologie réseaux',
    'TSLA': 'Automobile', 
    'CAT': 'Industrie', 
    'GE': 'Industrie', 
    'BA': 'Aéronautique', 
    'DHR': 'Matériel médical',
    'JNJ': 'Santé', 
    'PFE': 'Santé', 
    'MRK': 'Santé', 
    'LLY': 'Santé', 
    'ABBV': 'Biotechnologie', 
    'TMO': 'Biotechnologie', 
    'UNH': 'Assurance santé',
    'JPM': 'Banque', 
    'BAC': 'Banque', 
    'WFC': 'Banque', 
    'GS': 'Banque', 
    'MS': 'Banque', 
    'V': 'Paiements', 
    'MA': 'Paiements',
    'WMT': 'Grande distribution', 
    'COST': 'Grande distribution', 
    'HD': 'Bricolage',
    'NKE': 'Consommation', 
    'PG': 'Consommation', 
    'KO': 'Consommation', 
    'PEP': 'Consommation',
    'SPY': 'ETF',
    'QQQ': 'ETF',
    'DIA': 'ETF', 
    'TLT': 'ETF', 
    'IEF': 'ETF', 
    'GLD': 'ETF', 
    'SLV': 'ETF',
    'BTC-USD': 'Crypto', 
    'ETH-USD': 'Crypto',
    'XRP-USD': 'Crypto', 
    'LTC-USD': 'Crypto',
    'CMCSA': 'Télécom', 
    'VZ': 'Télécom', 
    'TMUS': 'Télécom',
    'CVX': 'Énergie', 
    'XOM': 'Énergie'
}

# 📊 Association des actifs à leur benchmark logique
benchmark_map = {
    # Actions Tech → QQQ
    'AAPL': 'QQQ',
    'MSFT': 'QQQ', 
    'GOOGL': 'QQQ', 
    'META': 'QQQ', 
    'AMZN': 'QQQ', 
    'NVDA': 'QQQ', 
    'ADBE': 'QQQ', 
    'CRM': 'QQQ',

    # Actions industrielles ou Dow Jones → DIA
    'BA': 'DIA', 
    'CAT': 'DIA', 
    'GE': 'DIA',

    # Santé & large-cap divers → SPY
    'JNJ': 'SPY', 
    'PFE': 'SPY', 
    'MRK': 'SPY', 
    'LLY': 'SPY', 
    'UNH': 'SPY', 
    'TMO': 'SPY',
    'PG': 'SPY',
    'KO': 'SPY', 
    'PEP': 'SPY', 
    'DIS': 'SPY', 
    'NKE': 'SPY',
    'JPM': 'SPY', 
    'BAC': 'SPY', 
    'WFC': 'SPY', 
    'GS': 'SPY', 
    'MS': 'SPY', 
    'V': 'SPY', 
    'MA': 'SPY',
    'WMT': 'SPY', 
    'HD': 'SPY', 
    'COST': 'SPY', 
    'TSLA': 'SPY',

    # Obligations longues → TLT
    'TLT': 'TLT',

    # Obligations courtes → IEF
    'IEF': 'IEF',

    # Matières premières
    'GLD': 'GLD', 
    'SLV': 'SLV',

    # Crypto → BTC comme référence
    'ETH-USD': 'BTC-USD',
    'XRP-USD': 'BTC-USD', 
    'LTC-USD': 'BTC-USD',
    'BTC-USD': 'BTC-USD',

    # Benchmarks eux-mêmes → 100%
    'SPY': 'SPY',
    'QQQ': 'QQQ', 
    'DIA': 'DIA',
    
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