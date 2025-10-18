import streamlit as st
import pandas as pd
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords

# Stopwords
nltk.download("stopwords", quiet = True)
default_stopwords = set(stopwords.words("turkish")).union({
    "bi","bir","de","ki","ve","ey","ah","mi","mı"})

# Duygu sözcükleri
positive_words = {
    "sevgi", "mutluluk", "neşe", "huzur", "coşku", "aşk", "gurur", "umut", "şükür", "keyif", "iyi", "tatil",
    "tatmin", "ilham", "sevinç", "neşelen", "rahatlık", "başarı", "minnet", "huzurlu", "takdir", "merhamet"}

negative_words = {
    "acı", "hüzün", "keder", "yalnızlık", "mutsuzluk", "öfke", "korku", "kayıp", "ölüm", "yıkım",
    "hastalık", "karamsarlık", "lanet", "felaket", "pişmanlık", "suçluluk", "çaresizlik", "sıkıntı", "hayal kırıklığı", "ihanet"}


# Sayfa düzeni
st.set_page_config(page_title="Şarkı Sözleri Analizi", page_icon="🎵")
st.title("🎧 Şarkı Sözleri Uygulaması")
st.markdown("---")

# Yan panel
st.sidebar.header("Ek özellikler") 
extra_stopwords_input = st.sidebar.text_area(
    "Filtrelenecek kelimeleri yaz",
    placeholder="örnek: ey, yo, skrrt")

st.sidebar.markdown("---")
top_chorus = st.sidebar.slider(
    "Nakarat satır sayısı", 
    min_value=1, 
    max_value=8,
    value=4, 
    step=1)


extra_stopwords = set(w.strip() for w in extra_stopwords_input.lower().split(",") if w.strip())
stop_words = default_stopwords.union(extra_stopwords)


# Kullanıcı girdisi
text_input = st.text_area(
    "Şarkı Sözleri buraya girin",
    height = 200,
    placeholder = "Örnek: Seni seviyorum...")

def clean_words(text):
    words = re.findall(r"[a-zA-zğüşıöç]+", text.lower())
    return [w for w in words if w not in stop_words and len(w) > 1]

def word_frequency(words,top_n=10):
    return pd.DataFrame(Counter(words).most_common(top_n), columns=["Word","Count"])

def repeated_lines(text, top_n=5):
    lines = text.lower().split("\n")
    lines = [line.strip() for line in lines if line.strip()]
    line_count = Counter(lines)
    return pd.DataFrame(line_count.most_common(top_n), columns=["Line","Count"])

def generate_wordcloud(words):
    text = " ".join(words)
    wc = WordCloud(width=800, height=400, background_color="#fff", #0e1117 
                   collocations=False, font_path="arial.ttf").generate(text)
    fig, ax = plt.subplots(figsize=(10,5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    return fig
    
def generate_wordcloud_exlude_chorus(words, chorus_lines):
    chorus_words = set()
    for line in chorus_lines:
        chorus_words.update(re.findall(r"[a-zA-Zğüışçö']+",line.lower()))
    filtered_words = [w for w in words if w not in chorus_words]
    return generate_wordcloud(filtered_words)
    

def sentiment_score(words):
    if not words:
        return 0
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    score = (pos_count - neg_count) / len(words)
    return score
    
# Ana program
if st.button("Analiz Et"):
    if not text_input.strip():
        st.warning("⚠️ Analiz etmek için bir şarkı sözü giriniz!")
    else:
        words = clean_words(text_input)
        
        
        # Düzenlemeler
        repeat_df = repeated_lines(text_input, top_n=4)
        chorus_lines = repeat_df["Line"].tolist()
        filtered_words = [w for w in words if w not in set(re.findall(r"[a-zA-Zğüışçö']+", " ".join(chorus_lines).lower()))]
        freq_df = word_frequency(filtered_words, top_n=10)
        
        # En çok kullanılan 10 kelime
        st.subheader("En çok kullanılan 10 kelime")
        fig,ax = plt.subplots(figsize=(10,5))
        ax.bar(freq_df["Word"], freq_df["Count"], color="violet")
        ax.set_ylabel("Sıklık")
        st.pyplot(fig)
         
        # Tekrar eden Satırlar (Olası Nakarat)
        repeat_df = repeated_lines(text_input, top_n=top_chorus)
        st.subheader("Tekrar eden Satırlar (Olası Nakarat)")
        st.table(repeat_df)
        chorus_lines = repeat_df["Line"].tolist()
        
        # Word Cloud (Kelime Bulutu)
        st.subheader("Kelime Bulutu")
        wc_fig_full = generate_wordcloud(words)
        st.pyplot(wc_fig_full)
        
        # Word Cloud (Nakaratsız Kelime Bulutu)
        st.subheader("Kelime Bulutu (Nakaratsız)")
        wc_fig_full = generate_wordcloud_exlude_chorus(words,chorus_lines)
        st.pyplot(wc_fig_full)
        
        
        # Basit Duygu Analizi
        st.subheader("Basit Duygu Analizi")
        score = sentiment_score(words)
        if score > 0:
            st.success("🎉 Olumlu duygular içeriyor")
        elif score < 0:
            st.error("💔 Olumsuz duygular içeriyor")
        else:
            st.info("😐 Şarkı sözleri Nötr")
            
        
        
        
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    