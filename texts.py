text_1 = """Les données pour chaque actif proviennent de **l'api de Yahoo Finance**, 
puis un dataframe regroupant toutes les données à été constitué en utilisant successivement
la fonction pandas : **pd.concat([],axis=1)**"""

text_2 = """Chaque actif possède une **date d'introduction en bourse différente**, par conséquent, 
sur la période du 01-01-2000 au 31-12-2024, certains actifs n'étaient pas encore côtés en bourse générant 
ainsi **des valeurs NaN jusqu'à leur date d'introduction**.\n

La méthode utilisée pour néttoyer les valeurs manquuantes est la suivante :\n

On **supprime** l'actif si c'est une **Crypto** avec plus de **50% de valeurs manquantes**, 
pour les **ETFs** et les **Actions** si il y a plus de **60% de valeurs manquantes**.\n

**Autrement**, on **rempli** les valeurs manquantes en utilisant pour chaque actif les méthodes 
**.ffill()** et **.bfill()**"""

text_3 = """Présentation des variables :\n
**Date** : datetime — date de l'observation des données de marché.\n
**Ticker** : category — abréviation unique (ex: AAPL, BTC-USD) représentant un actif financier coté.\n
**Prix** : float64 — prix de clôture de l'actif à la date donnée.\n
**Type_actif** : category — nature de l'actif (ex: Action, Crypto, ETF).\n
**Secteur** : category — secteur économique auquel appartient l'actif (ex: Technologie, Santé).\n
**Rendement** : float64 — variation du prix entre deux jours (souvent en pourcentage).\n
**Année** : Int64 — année civile de l'observation (utile pour des regroupements temporels).\n
**Volatilité_30j** : float64 — écart-type des rendements sur les 30 derniers jours (risque à court terme).\n
**Volatilité_30j_annualisée** : float64 — projection annuelle de la volatilité sur 30 jours (standardisée sur 252 jours).\n
**Volatilité_quotidienne** : float64 — volatilité observée sur une base quotidienne.\n
**Benchmark** : category — indice de référence associé à l'actif (ex: S&P 500, Nasdaq).\n
**Performance_vs_Benchmark** : float64 — différence de performance entre l'actif et son benchmark sur une période donnée."""