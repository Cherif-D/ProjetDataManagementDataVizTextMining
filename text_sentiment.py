import pandas as pd
import re
import joblib
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
from wordcloud import WordCloud
from unidecode import unidecode
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

def text_cleaner(texte:str) -> str:

    if not isinstance(texte, str):
        return ""

    texte = texte.lower()
    texte = unidecode(texte)
    texte = re.sub(r'[^\w\s]', ' ', texte)
    texte = re.sub(r'\d+', '', texte)

    stop_words = set(stopwords.words('french'))
    mots_suppr = ['a', 'h', 'he']

    tokens = texte.split()
    tokens = [mot for mot in tokens if mot not in stop_words and mot not in mots_suppr and len(mot) > 2]

    return ' '.join(tokens)

def generer_wordcloud(texte_nettoye:str) -> plt.Figure:

    wc = WordCloud(
        background_color="white",
        width=1200,
        height=600,
        colormap='plasma'
    ).generate(texte_nettoye)

    plt.figure(figsize=(12, 12))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()

    return plt.gcf()

if __name__ == "__main__":

    CSV_PATH = "sentiment_training.csv"
    df = pd.read_csv(CSV_PATH)

    texte_col = df.columns[0]
    df["clean_text"] = df[texte_col].apply(text_cleaner)

    label_col = df.columns[1]
    y = df[label_col].map({'negatif': 0, 'neutre': 1, 'positif': 2})

    X_text_train, X_text_test, y_train, y_test = train_test_split(df["clean_text"], y, test_size=0.2, random_state=100)

    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(X_text_train)
    X_test = vectorizer.transform(X_text_test)

    model = LogisticRegression(class_weight='balanced')
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    classification_report_text = classification_report(y_test, y_pred)

    joblib.dump(model, "sentiment_model.joblib")
    joblib.dump(vectorizer, "tfidf_vectorizer.joblib")
    joblib.dump(classification_report_text, "classification_report.joblib")
    print("\n Modèle et vectorizer sauvegardés.")