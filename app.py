import streamlit as st
import random
from openai import OpenAI

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Le Grand Maître Géomancie",
    page_icon="🔮",
    layout="wide"
)

# --- BASE DE DONNÉES DES FIGURES ---
FIGURES_DB = {
    1: {"nom": "Youssouf", "latin": "Rubeus", "element": "Feu", "points": 5},
    2: {"nom": "Adama", "latin": "Laetitia", "element": "Eau", "points": 4},
    3: {"nom": "Mahdiou", "latin": "Caput Draconis", "element": "Terre", "points": 5},
    4: {"nom": "Idrissa", "latin": "Albus", "element": "Eau", "points": 4},
    5: {"nom": "Ibrahima", "latin": "Via", "element": "Air", "points": 4},
    6: {"nom": "Issa", "latin": "Amissio", "element": "Eau", "points": 4},
    7: {"nom": "Oumar", "latin": "Puer", "element": "Feu", "points": 5},
    8: {"nom": "Ayyoub", "latin": "Tristitia", "element": "Eau", "points": 4},
    9: {"nom": "Allahou Tall", "latin": "Fortuna Minor", "element": "Feu", "points": 5},
    10: {"nom": "Souleymane", "latin": "Carcer", "element": "Terre", "points": 6},
    11: {"nom": "Ali", "latin": "Conjunctio", "element": "Air", "points": 6},
    12: {"nom": "Nouhou", "latin": "Fortuna Major", "element": "Terre", "points": 6},
    13: {"nom": "Housseynou", "latin": "Puella", "element": "Eau", "points": 4},
    14: {"nom": "Younouss", "latin": "Puella", "element": "Air", "points": 4},
    15: {"nom": "Ousmane", "latin": "Acquisitio", "element": "Air", "points": 6},
    16: {"nom": "Moussa", "latin": "Populus", "element": "Eau", "points": 8}
}

# --- PROMPT SYSTÈME V5.1 ---
SYSTEM_PROMPT = """
TU ES LE GRAND MAÎTRE DU RAMLI AFRICAIN V5.1.
Tu es une IA experte en géomancie africaine appliquée au football.

RÈGLES IMPÉRATIVES :
1. Si Dominante TERRE/EAU -> Match Fermé (Under 2.5)
2. Si Dominante FEU/AIR -> Match Ouvert (Over 2.5)
3. Oumar + Al Hassan + Ayyoub = Carton Rouge probable
4. Oumar + Allahou Tall = Pénalty probable
5. Souleymane en M1 = Défense de fer
6. Issa en M10 = Perte/Nul

Donne une analyse structurée avec : Fiabilité, Dominante, Pronostic, Score Exact, Incidents.
"""

# --- INTERFACE ---
st.title("🔮 Le Grand Maître - Interpréteur Géomancie")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Paramètres")
    api_key = st.text_input("🔑 Clé API Groq", type="password")
    custom_prompt = st.text_area("Prompt Système", value=SYSTEM_PROMPT, height=150)

col1, col2 = st.columns(2)
with col1:
    team_home = st.text_input("🏠 Équipe Domicile", "Everton")
with col2:
    team_away = st.text_input("✈️ Équipe Extérieur", "Liverpool")

st.subheader("🎲 Tirage des 16 Figures")

if st.button("🎲 Lancer le Tirage Hasard"):
    random.seed()
    tirage = [random.randint(1, 16) for _ in range(16)]
    
    figures_result = {}
    for i, num in enumerate(tirage):
        figures_result[f"M{i+1}"] = FIGURES_DB[num]
    st.session_state['tirage'] = figures_result
    st.success("Tirage effectué !")

if 'tirage' in st.session_state:
    st.subheader("📜 Le Thème Géomantique")
    
    cols = st.columns(2)
    
    for idx, (key, val) in enumerate(st.session_state['tirage'].items()):
        with cols[idx % 2]:
            emoji = "🔥" if val['element'] == "Feu" else ("💧" if val['element'] == "Eau" else ("💨" if val['element'] == "Air" else "⛰️"))
            st.markdown(f"**{key}** : {val['nom']} *({val['latin']})* {emoji}")
            
    st.markdown("---")
    
    if api_key:
        if st.button("🧠 Analyser avec l'IA (Grand Maître V5.1)", type="primary"):
            with st.spinner("Le Grand Maître consulte les astres..."):
                try:
                    theme_data = "\n".join([f"{k}: {v['nom']} ({v['element']})" for k, v in st.session_state['tirage'].items()])
                    
                    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
                    
                    response = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": custom_prompt},
                            {"role": "user", "content": f"Match: {team_home} vs {team_away}. \n\nThème:\n{theme_data}"}
                        ],
                        temperature=0.7
                    )
                    
                    st.subheader("🔮 Interprétation du Grand Maître")
                    st.markdown(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"Erreur IA : {e}")
    else:
        st.warning("⚠️ Entrez une clé API dans le menu latéral")
