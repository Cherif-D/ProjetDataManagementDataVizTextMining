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

text_4 = """Il y a beaucoup d'incertitude sur le marché des métaux de base 
concernant les implications de l'accord commercial entre les États-Unis et la Chine.

Les prix des métaux de base ont réagi de manière inégale à l'accord tarifaire entre les États-Unis et la Chine. 
Les prix de l'aluminium ont d'abord augmenté, tandis que ceux du nickel et du cuivre ont diminué.

Au moment de la rédaction de cet article, 
le contrat de cuivre de trois mois sur le London Metal Exchange était de 9 574 $ la tonne, 
en baisse de 1,3 %. Le nickel était en hausse de 0,2 % à 15 136 $ la tonne.

L'accord est bénéfique pour les métaux de base car il atténue le risque 
d'une nouvelle escalade du conflit, selon Commerzbank AG (ETR:CBKG).

D'autre part, les droits de douane, en particulier ceux imposés à la Chine, 
continuent d'être considérablement plus élevés que les niveaux d'avant Trump.

Cet environnement tarifaire élevé devrait supprimer la demande sur le marché des métaux, 
ce qui est d'une importance capitale, a déclaré la banque allemande dans un rapport.

Prix de l'aluminium
« Pendant ce temps, la hausse des prix de l'aluminium pourrait être principalement 
due à des problèmes d'approvisionnement », a déclaré Thu Lan Nguyen, 
responsable de la recherche sur les devises et les matières premières chez Commerzbank, dans le rapport.
Les stocks du LME n'ont cessé de diminuer depuis le printemps dernier.

Dans le même temps, des rumeurs suggèrent une concentration importante du marché, 
avec une poignée d'entreprises qui détiendraient des positions substantielles, 
leur permettant de se procurer de grandes quantités d'aluminium, a déclaré M. Nguyen.

Elle a ajouté :

Cela pourrait causer des difficultés aux contreparties compte tenu des faibles
niveaux de stock et conduire à ce que l'on appelle un « short squeeze ».
Les tendances passées du marché, reflétant les conditions actuelles,
ont constamment entraîné des hausses de prix importantes sur les marchés des métaux. 
La hausse spectaculaire des prix du nickel observée en 2022 en est un exemple notable.
Au moment de la rédaction de cet article, le contrat d'aluminium de trois mois sur 
le London Metal Exchange était de 2 485 $ l'once, en baisse de 1,5 % par rapport à la clôture précédente.

Le minerai de fer reste sous pression
Les prix du minerai de fer ont continué de subir une pression à la baisse, 
tombant sous la barre des 95 dollars la tonne à Singapour vendredi. 
Cette baisse s'est produite avant la publication lundi des chiffres de la production industrielle chinoise.
Les importations de minerai de fer de la Chine en mai ont été signalées lundi, 
montrant une baisse de 4 % en glissement annuel à 98,1 millions de tonnes.

Au cours des cinq premiers mois de cette année, une moyenne de 97,3 millions de tonnes a été importée. 
Cela représente une baisse d'environ 5 % par rapport à la même période l'an dernier."""