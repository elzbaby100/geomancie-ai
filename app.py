import streamlit as st
import random
import json
from openai import OpenAI # Nécessite: pip install openai streamlit

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Le Grand Maître Géomancie",
    page_icon="🔮",
    layout="wide"
)

# --- BASE DE DONNÉES DES FIGURES (Noms & Éléments) ---
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
    13: {"nom": "Housseynou", "latin": "Puella", "element": "Eau", "points": 4}, # Adaptation locale
    14: {"nom": "Younouss", "latin": "Puella", "element": "Air", "points": 4},
    15: {"nom": "Ousmane", "latin": "Acquisitio", "element": "Air", "points": 6},
    16: {"nom": "Moussa", "latin": "Populus", "element": "Eau", "points": 8}
}

# --- LE PROMPT SYSTÈME V5.1 (C'est ici que vous mettez l'intelligence) ---
SYSTEM_PROMPT = """
TU ES LE GRAND MAÎTRE DU RAMLI AFRICAIN V5.1.
Tu es une IA experte en géomancie africaine appliquée au football.
Voici tes règles impératives (Codex V5.1) :

1. ANALYSE ÉLÉMENTAIRE (PRIORITÉ) : 
   - Si Dominante TERRE/EAU -> Match Fermé (Under 2.5).
   - Si Dominante FEU/AIR -> Match Ouvert (Over 2.5).

2. RÈGLE DES FIGURES FANTÔMES & OMBRES :
   - Vérifie si M1 et M7 ont la même parité que le Juge (M16).
   - Parité opposée = Ombre négative (affaiblissement).

3. COMBINAISONS ODU :
   - Oumar + Ousmane adjacents = Domination totale.
   - Idrissa + Allahou Tall adjacents = Conflit/Rouge.

4. INCIDENTS :
   - Carton Rouge si : (M6=Al Hassan/Oumar) ET (M9=Ayyoub/Allahou Tall).
   - Pénalty si : (M3/M6=Oumar) ET (M9=Allahou Tall).

5. FORMAT DE RÉPONSE :
   Retourne une analyse structurée avec :
   - Fiabilité du thème (%)
   - Dominante Élémentaire
   - Pronostic Vainqueur & Score Exact
   - Alerte Incidents (Rouge/Penalty)
   - Conseil de Paris
    
TA RÉPONSE DOIT ÊTRE CLAIRE, PROFESSIONNELLE ET DIRECTE.
"""

# --- INTERFACE UTILISATEUR ---

st.title("🔮 Le Grand Maître - Interpréteur Géomancie")
st.markdown("---")

# Barre latérale pour la configuration (Cachée sur mobile, accessible par le menu hamburger)
with st.sidebar:
    st.header("⚙️ Paramètres")
    api_key = st.text_input("🔑 Clé API (Groq ou OpenAI)", type="password", help="Nécessaire pour l'IA")
    
    st.subheader("📜 Éducation IA")
    st.info("Modifiez le 'System Prompt' ci-dessous pour mettre à jour les règles du Grand Maître en temps réel.")
    custom_prompt = st.text_area("Prompt Système", value=SYSTEM_PROMPT, height=200)
    if st.button("💾 Mettre à jour les règles"):
        st.success("Règles mises à jour ! L'IA utilisera cette nouvelle logique.")

# Section Match
col1, col2 = st.columns(2)
with col1:
    team_home = st.text_input("🏠 Équipe Domicile", "Everton")
with col2:
    team_away = st.text_input("✈️ Équipe Extérieur", "Liverpool")

# Section Tirage
st.subheader("🎲 Tirage des 16 Figures")
method = st.radio("Méthode de tirage", ["Aléatoire (Auto)", "Manuel (Saisie)"], horizontal=True)

figures_result = {}

if method == "Aléatoire (Auto)":
    if st.button("🎲 Lancer le Tirage Hasard"):
        # Génération de 16 chiffres aléatoires entre 1 et 16
        random.seed()
        tirage = [random.randint(1, 16) for _ in range(16)]
        
        # Mapping vers les figures
        for i, num in enumerate(tirage):
            figures_result[f"M{i+1}"] = FIGURES_DB[num]
        st.session_state['tirage'] = figures_result
        st.success("Tirage effectué !")
else:
    st.write("Saisissez les numéros des figures (1-16) ou sélectionnez les noms.")
    # Pour simplifier sur mobile, on peut faire une saisie simple ou des selectbox
    # Ici, simulons une saisie rapide pour la démo, mais en vrai il faudrait 16 inputs
    st.info("Mode Saisie Manuel : Utilisez le mode Aléatoire pour tester rapidement, ou fournissez la liste des chiffres.")
    # Si vous avez une liste de chiffres (ex: [7, 2, 2...]), on peut les parser ici

# Affichage du Thème
if 'tirage' in st.session_state:
    st.subheader("📜 Le Thème Géomantique")
    
    # Affichage en grille adaptative (2 colonnes sur mobile, plus sur PC)
    cols = st.columns(2) # 2 colonnes pour mobile
    
    for idx, (key, val) in enumerate(st.session_state['tirage'].items()):
        with cols[idx % 2]:
            emoji = "🔥" if val['element'] == "Feu" else ("💧" if val['element'] == "Eau" else ("💨" if val['element'] == "Air" else "⛰️"))
            st.markdown(f"**{key}** : {val['nom']} *({val['latin']})* {emoji}")
            
    st.markdown("---")
    
    # Bouton d'interprétation
    if api_key:
        if st.button("🧠 Analyser avec l'IA (Grand Maître V5.1)", type="primary"):
            with st.spinner("Le Grand Maître consulte les astres et les algorithmes..."):
                try:
                    # Préparation des données pour l'IA
                    theme_data = "\n".join([f"{k}: {v['nom']} ({v['element']})" for k, v in st.session_state['tirage'].items()])
                    
                    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1") # Utilisation de Groq (Rapide/Gratuit)
                    
                    response = client.chat.completions.create(
                        model=, model="llama-3.1-70b-versatile",  # Change en:
# model="llama3-70b-8192",  # ✅ Nouveau modèle recommandé 
                        messages=[
                            {"role": "system", "content": custom_prompt},
                            {"role": "user", "content": f"Match: {team_home} vs {team_away}. \n\nVoici le thème :\n{theme_data}"}
                        ],
                        temperature=0.7
                    )
                    
                    st.subheader("🔮 Interprétation du Grand Maître")
                    st.markdown(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"Erreur IA : {e}. Vérifiez votre clé API.")
    else:
        st.warning("⚠️ Veuillez entrer une clé API dans le menu latéral pour activer l'IA.")

else:
    st.info("Lancez un tirage pour commencer !")
