# 📚 Import des librairies nécessaires
import pandas as pd
import numpy as np
import re
import os
import urllib.request
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from wordcloud import WordCloud

from unidecode import unidecode
import nltk
from nltk.corpus import stopwords

# Téléchargement des stopwords français
nltk.download('stopwords')

# Fonction de nettoyage de texte (text mining)
def nettoyer_texte_basique(texte):
    """
    Nettoie un texte brut :
    - Mise en minuscules
    - Suppression accents
    - Retrait ponctuation et chiffres
    - Suppression des stopwords et mots inutiles
    """
    texte = texte.lower()
    texte = unidecode(texte)
    texte = re.sub(r'[^\w\s]', ' ', texte)
    texte = re.sub(r'\d+', '', texte)

    stop_words = set(stopwords.words('french'))
    mots_suppr = ['a', 'h', 'he']

    tokens = texte.split()
    tokens = [mot for mot in tokens if mot not in stop_words and mot not in mots_suppr]

    return ' '.join(tokens)

# Interface Streamlit
st.title("NLP + sentiment des articles")

# Zone de texte utilisateur
user_article = st.text_area("Veuillez coller l'article :", height=300)

# Nettoyage et affichage du texte
if st.button("Nettoyer le texte"):
    if user_article.strip() == "":
        st.warning("Merci de coller un article avant de lancer l'analyse.")
    else:
        texte_nettoye = nettoyer_texte_basique(user_article)
        st.session_state['texte_nettoye'] = texte_nettoye
        st.success("Texte nettoyé ✅")
        st.write(texte_nettoye)

# BOW & TF-IDF si texte disponible
if 'texte_nettoye' in st.session_state:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Bag of Words"):
            vectorizer = CountVectorizer()
            X_counts = vectorizer.fit_transform([st.session_state['texte_nettoye']])
            counts_df = pd.DataFrame(X_counts.toarray(), columns=vectorizer.get_feature_names_out()).T
            counts_df.columns = ["Fréquence"]
            counts_df = counts_df.sort_values("Fréquence", ascending=False)
            st.dataframe(counts_df)

    with col2:
        if st.button("TF-IDF"):
            tfidf_vectorizer = TfidfVectorizer()
            X_tfidf = tfidf_vectorizer.fit_transform([st.session_state['texte_nettoye']])
            tfidf_df = pd.DataFrame(X_tfidf.toarray(), columns=tfidf_vectorizer.get_feature_names_out()).T
            tfidf_df.columns = ["Score TF-IDF"]
            tfidf_df = tfidf_df.sort_values("Score TF-IDF", ascending=False)
            st.dataframe(tfidf_df) 

# Chargement et entraînement du modèle sentiment
URL_CSV = "https://raw.githubusercontent.com/Cherif-D/ProjetDataManagementDataVizTextMining/main/sentiment_finance.csv"
LOCAL_CSV = "sentiment_training.csv"

if not os.path.exists(LOCAL_CSV):
    st.info("Téléchargement des données d'entraînement...")
    try:
        urllib.request.urlretrieve(URL_CSV, LOCAL_CSV)
        st.success("Données téléchargées 📥")
    except Exception as e:
        st.error(f"Erreur : {e}")

if os.path.exists(LOCAL_CSV):
    df = pd.read_csv(LOCAL_CSV)
    st.write(f"📄 Jeu de données chargé ({len(df)} lignes)")

    # Extraction colonnes texte et label
    texte_col = df.columns[0]
    label_col = df.columns[1]

    # TF-IDF sur le dataset entier
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df[texte_col])
    y = df[label_col].map({'negatif': 0, 'neutre': 1, 'positif': 2})

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entraînement modèle
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Évaluation du modèle
    y_pred = model.predict(X_test)
    st.write("Évaluation du modèle")
    st.text(classification_report(y_test, y_pred))
    st.write("Accuracy :", accuracy_score(y_test, y_pred))

    # Zone pour tester un nouveau texte
    user_article_2 = st.text_area("Collez un article pour prédire le sentiment :", height=200, key="user2")

    if st.button("Prédire le sentiment", key="analyse_sentiment"):
        if user_article_2.strip() == "":
            st.warning("Merci de coller un texte avant d'analyser.")
        else:
            texte_nettoye_2 = nettoyer_texte_basique(user_article_2)
            vect = vectorizer.transform([texte_nettoye_2])
            pred = model.predict(vect)[0]
            proba = model.predict_proba(vect)[0]

            sentiment_label = {0: "🟥 Négatif", 1: "🟨 Neutre", 2: "🟩 Positif"}
            st.write(f"**Sentiment prédit : {sentiment_label[pred]}**")
            st.write(f"Probabilités : Négatif = {proba[0]:.2f}, Neutre = {proba[1]:.2f}, Positif = {proba[2]:.2f}")

else:
    st.error("Aucun fichier de données d'entraînement détecté.")
    
if 'texte_nettoye' in st.session_state:
    st.markdown("---")
    st.subheader("Nuage de mots du texte analysé")

    wc = WordCloud(
        background_color="white",
        width=1200,
        height=600,
        colormap='plasma'
    ).generate(st.session_state['texte_nettoye'])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
    
