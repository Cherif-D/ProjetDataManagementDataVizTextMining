

# --- IMPORTS DES LIBRAIRIES ---
import yfinance as yf             # Pour télécharger les données financières
import pandas as pd               # Pour manipuler les tableaux
import os                         # Pour créer le dossier de sauvegarde

# --- FONCTION PRINCIPALE DE TÉLÉCHARGEMENT ---
def telecharger_donnees_massives(tickers, start_date='2000-01-01', end_date='2024-12-31'):
    """
    Télécharge les cours de clôture pour une liste de tickers depuis Yahoo Finance.
    Combine toutes les séries de prix dans un seul DataFrame.

    Args:
        tickers (list): Liste des symboles boursiers.
        start_date (str): Date de début au format 'YYYY-MM-DD'.
        end_date (str): Date de fin au format 'YYYY-MM-DD'.

    Returns:
        DataFrame: Données de prix de clôture pour chaque ticker (format large).
    """
    all_data = pd.DataFrame()
    successful_tickers = []

    print(f"Téléchargement de {len(tickers)} tickers entre {start_date} et {end_date}...\n")

    for ticker in tickers:
        try:
            print(f"  ▶️ {ticker}")
            data = yf.download(ticker, start=start_date, end=end_date)

            if 'Close' in data.columns and not data['Close'].empty:
                prices = data['Close']
                prices.name = ticker
                all_data = pd.concat([all_data, prices], axis=1)
                successful_tickers.append(ticker)
            else:
                print(f"    ⚠️ Aucune donnée 'Close' valide pour {ticker}.")
        except Exception as e:
            print(f"    ❌ Erreur pour {ticker} : {e}")

    if not all_data.empty:
        all_data.columns = successful_tickers

    return all_data

# --- EXÉCUTION PRINCIPALE DU SCRIPT ---
if __name__ == "__main__":
    # Liste de tickers à télécharger (actions, cryptos, ETF…)
    extended_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX', 'ADBE', 'CRM',
        'JPM', 'BAC', 'WFC', 'GS', 'MS',
        'KO', 'PG', 'PEP', 'DIS', 'NKE',
        'XOM', 'CVX', 'GE', 'CAT', 'BA',
        'SPY', 'QQQ', 'DIA', 'TLT', 'IEF',
        'GLD', 'SLV',
        'BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD',
        'V', 'MA', 'COST', 'WMT', 'HD', 'UNH', 'LLY', 'JNJ', 'PFE', 'MRK',
        'ABBV', 'TMO', 'DHR', 'AVGO', 'TXN', 'CSCO', 'CMCSA', 'VZ', 'TMUS'
    ]

    start_date_data = '2000-01-01'
    end_date_data = '2024-12-31'

    print("📥 Début du téléchargement...")
    donnees_financieres_wide = telecharger_donnees_massives(
        extended_tickers,
        start_date=start_date_data,
        end_date=end_date_data
    )

    print("\n✅ Données téléchargées.")
    print(f"  - Nombre de dates : {len(donnees_financieres_wide)}")
    print(f"  - Nombre d’actifs : {len(donnees_financieres_wide.columns)}")
    print(f"  - Points valides  : {donnees_financieres_wide.count().sum()}")

    # --- TRANSFORMATION AU FORMAT LONG ---
    print("\n🔁 Transformation en format long...")
    donnees_financieres_wide = donnees_financieres_wide.reset_index()
    donnees_financieres_long = pd.melt(
        donnees_financieres_wide,
        id_vars=['Date'],
        var_name='Ticker',
        value_name='Prix'
    )


    print(f"  - Lignes après nettoyage : {len(donnees_financieres_long)}")
    print("  - Aperçu :")
    print(donnees_financieres_long.head())

    # --- ENREGISTREMENT DANS LE DOSSIER 'data/' ---
    output_dir = 'Data'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'donnees_financieres_300k_lignes.csv')

    donnees_financieres_long.to_csv(output_path, index=False)

    print(f"\n💾 Fichier sauvegardé dans : {output_path}")
    print("🎉 Données prêtes à être utilisées dans le notebook ou Streamlit.")
