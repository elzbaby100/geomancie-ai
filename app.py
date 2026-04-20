import streamlit as st
import random
from openai import OpenAI

st.set_page_config(page_title="Le Grand Maître", page_icon="🔮")

FIGURES = {
    1: {"nom": "Youssouf", "element": "Feu"}, 2: {"nom": "Adama", "element": "Eau"},
    3: {"nom": "Mahdiou", "element": "Terre"}, 4: {"nom": "Idrissa", "element": "Eau"},
    5: {"nom": "Ibrahima", "element": "Air"}, 6: {"nom": "Issa", "element": "Eau"},
    7: {"nom": "Oumar", "element": "Feu"}, 8: {"nom": "Ayyoub", "element": "Eau"},
    9: {"nom": "Allahou Tall", "element": "Feu"}, 10: {"nom": "Souleymane", "element": "Terre"},
    11: {"nom": "Ali", "element": "Air"}, 12: {"nom": "Nouhou", "element": "Terre"},
    13: {"nom": "Housseynou", "element": "Eau"}, 14: {"nom": "Younouss", "element": "Air"},
    15: {"nom": "Ousmane", "element": "Air"}, 16: {"nom": "Moussa", "element": "Eau"}
}

PROMPT = "Tu es un expert en géomancie africaine. Analyse ce thème pour le match et donne: vainqueur, score, buts, incidents."

st.title("🔮 Le Grand Maître")
api_key = st.sidebar.text_input("Clé API", type="password")
equipes = st.columns(2)
domicile = equipes[0].text_input("Domicile", "Everton")
exterieur = equipes[1].text_input("Extérieur", "Liverpool")

if st.button("🎲 Tirage"):
    st.session_state.tirage = {f"M{i+1}": FIGURES[random.randint(1,16)] for i in range(16)}

if "tirage" in st.session_state:
    st.write("### Thème")
    cols = st.columns(2)
    for i, (k, v) in enumerate(st.session_state.tirage.items()):
        cols[i%2].write(f"{k}: {v['nom']}")
    
    if api_key and st.button("🧠 Analyser"):
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            theme = "\n".join([f"{k}: {v['nom']}" for k,v in st.session_state.tirage.items()])
            
            with st.spinner("Analyse..."):
                rep = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": f"Match {domicile} vs {exterieur}\n{theme}\n{PROMPT}"}]
                )
            st.success("✅")
            st.write(rep.choices[0].message.content)
        except Exception as e:
            st.error(f"Erreur: {e}")
