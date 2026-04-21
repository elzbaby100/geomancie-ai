import streamlit as st
import random
from openai import OpenAI
from datetime import datetime

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Le Grand Maître", page_icon="🔮", layout="wide")

# --- CSS PERSONNALISÉ (Style Lovable) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(145deg, #0a0a0a 0%, #1a1510 50%, #0a0a0a 100%);
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
.stTitle, .stSubheader, .stMarkdown {
    font-family: 'Playfair Display', serif;
}
.title-main {
    text-align: center;
    font-size: 2.5em;
    font-weight: 700;
    background: linear-gradient(90deg, #d4af37, #f4e4a0, #d4af37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2em;
}
.subtitle-match {
    text-align: center;
    font-size: 1.1em;
    color: #8b7355;
    margin-bottom: 1.5em;
    font-family: 'Inter', sans-serif;
}
.card-figure {
    background: linear-gradient(145deg, #1e1a14, #2a2318);
    border: 1px solid #3d3425;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    margin: 5px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
}
.card-figure:hover {
    border-color: #d4af37;
    box-shadow: 0 4px 20px rgba(212,175,55,0.2);
}
.figure-name {
    font-size: 1.3em;
    font-weight: 700;
    color: #d4af37;
    font-family: 'Playfair Display', serif;
}
.figure-latin {
    font-size: 0.85em;
    color: #6b5d4d;
    font-style: italic;
    margin: 3px 0;
}
.figure-element {
    font-size: 0.9em;
    margin-top: 5px;
}
.section-title {
    font-size: 1.4em;
    font-weight: 700;
    color: #d4af37;
    border-bottom: 1px solid #3d3425;
    padding-bottom: 8px;
    margin-top: 25px;
    margin-bottom: 15px;
    font-family: 'Playfair Display', serif;
}
.analysis-box {
    background: rgba(30, 26, 20, 0.8);
    border: 1px solid #3d3425;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
}
.pronostic-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #2a2318;
}
.confidence-stars {
    color: #d4af37;
    font-size: 1.1em;
}
.input-dark {
    background-color: #1e1a14 !important;
    border: 1px solid #3d3425 !important;
    color: #d4af37 !important;
}
.stTextInput input, .stNumberInput input {
    background-color: #1e1a14 !important;
    border: 1px solid #3d3425 !important;
    color: #d4af37 !important;
}
.stButton button {
    background: linear-gradient(90deg, #d4af37, #b8941e) !important;
    color: #0a0a0a !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
}
.stButton button:hover {
    background: linear-gradient(90deg, #f4e4a0, #d4af37) !important;
}
</style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES FIGURES ---
FIGURES = {
    1: {"nom": "Youssouf", "latin": "Rubeus", "element": "Feu", "icon": "🔥", "desc": "Agressivité, violence, faute"},
    2: {"nom": "Adama", "latin": "Laetitia", "element": "Eau", "icon": "💧", "desc": "Joie, but, victoire"},
    3: {"nom": "Mahdiou", "latin": "Caput Draconis", "element": "Terre", "icon": "⛰️", "desc": "Entrée, progression lente"},
    4: {"nom": "Idrissa", "latin": "Albus", "element": "Eau", "icon": "💧", "desc": "Calme, défense, sagesse"},
    5: {"nom": "Ibrahima", "latin": "Via", "element": "Air", "icon": "💨", "desc": "Mouvement, chemin, transition"},
    6: {"nom": "Issa", "latin": "Amissio", "element": "Eau", "icon": "💧", "desc": "Perte, chute, défaite"},
    7: {"nom": "Oumar", "latin": "Puer", "element": "Feu", "icon": "🔥", "desc": "Combat, énergie, carton"},
    8: {"nom": "Ayyoub", "latin": "Tristitia", "element": "Eau", "icon": "💧", "desc": "Tristesse, annulation, blocage"},
    9: {"nom": "Allahou Tall", "latin": "Fortuna Minor", "element": "Feu", "icon": "🔥", "desc": "Rapidité, pénalty, VAR"},
    10: {"nom": "Souleymane", "latin": "Carcer", "element": "Terre", "icon": "⛰️", "desc": "Mur, défense, prison"},
    11: {"nom": "Ali", "latin": "Conjunctio", "element": "Air", "icon": "💨", "desc": "Union, équilibre, nul"},
    12: {"nom": "Nouhou", "latin": "Fortuna Major", "element": "Terre", "icon": "⛰️", "desc": "Force, puissance, domination"},
    13: {"nom": "Housseynou", "latin": "Puella", "element": "Eau", "icon": "💧", "desc": "Chute, erreur, immaturité"},
    14: {"nom": "Younouss", "latin": "Puella", "element": "Air", "icon": "💨", "desc": "Flottement, imprévu"},
    15: {"nom": "Ousmane", "latin": "Acquisitio", "element": "Air", "icon": "💨", "desc": "Gain, succès, victoire"},
    16: {"nom": "Moussa", "latin": "Populus", "element": "Eau", "icon": "💧", "desc": "Foule, attente, statu quo"}
}

ELEMENT_COLORS = {"Feu": "#ff6b35", "Eau": "#4a90d9", "Air": "#7ec8e3", "Terre": "#8b7355"}

DEFAULT_PROMPT = """Tu es LE GRAND MAÎTRE DU RAMLI AFRICAIN, expert suprême en géomancie africaine appliquée au football.

📜 RÈGLES ABSOLUES DU CODEX V5.1 :

1. DOMINANTE ÉLÉMENTAIRE (PRIORITÉ MAXIME) :
   - Calcule la somme des points par élément dans les 16 figures.
   - TERRE/EAU dominante (>35%) = MATCH FERMÉ → Under 2.5 obligatoire.
   - FEU/AIR dominante (>35%) = MATCH OUVERT → Over 2.5 probable.

2. CONTEXTE M10 (RÉSULTAT) :
   - M10 ne s'interprète JAMAIS seul. Compare avec M1 (Domicile) et M7 (Extérieur).
   - Si M1 ou M7 = Souleymane/Idrissa/Moussa → Match fermé, score max 1-0/0-1/1-1.
   - Si M10 = Nouhou + M1/M7 faibles → Victoire large possible.

3. INCIDENTS (COMBINAISONS SECRÈTES) :
   - Carton Rouge : (M6=Al Hassan/Oumar) ET (M9=Ayyoub/Allahou Tall)
   - Pénalty : (M3/M6=Oumar) ET (M9=Allahou Tall) ET (M2/M8=Adama/Ousmane)
   - But annulé VAR : (M2/M3=Oumar) ET (M13/M15=Ayyoub)

4. HEURE DU MATCH (CHRONOMANCIE) :
   - L'heure influence le timing des buts et l'énergie du match.
   - Matinée (8h-12h) = Jeu lent, Under probable.
   - Après-midi (14h-18h) = Énergie haute, Over probable.
   - Soir (19h-23h) = Match intense, incidents probables.
   - Nuit (0h-5h) = Imprévisible, surprises possibles.

5. DOUBLE MÉTHODE BUTS :
   - Sikidy (M2+M8+M10) : 8-12pts=0-1 | 13-16pts=2 | 17-20pts=3 | 21+=4+
   - Triade (M3+M5+M11) : Mesure l'intensité du jeu.

FORMAT DE RÉPONSE EXACT :

🔮 ANALYSE DU GRAND MAÎTRE

1. Rapport de Force
[Analyse M1 vs M7 avec contexte M10]

2. Indicateurs Clés
- Points Ouverts : [Domicile] (X) vs [Extérieur] (Y)
- Dominante [Élément] : Match [fermé/ouvert]
- [Autres indicateurs]

3. Scénario Temporel
- 1ère MT : [Prédiction basée sur M3/M5]
- 2ème MT : [Prédiction basée sur M11/M13]

4. Incidents Prévus
[Alertes rouges, pénaltys, VAR]

✅ PRONOSTICS OFFICIELS
| Type de Pari | Prédiction | Confiance |
| Vainqueur (1X2) | [Équipe] | ⭐⭐⭐⭐ |
| Total Buts | [Over/Under X.5] | ⭐⭐⭐⭐ |
| Mi-temps | [Score] | ⭐⭐⭐ |
| Score Exact | [X-Y] | ⭐⭐ |
| Cartons/VAR | [Prédiction] | ⭐⭐⭐ |

💡 CONSEIL STRATÉGIQUE
[Phrase percutante basée sur la figure clé]

🧠 ENRICHISSEMENT IA
INTERPRÉTATION PROFONDE : [Analyse détaillée des éléments et figures]
RÉFÉRENCE TRADITIONNELLE : [Contexte culturel Ramli]
CONSEIL SPIRITUEL : [Phrase de sagesse]

Sois précis, technique, et utilise le langage du Ramli africain."""

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_PROMPT
if "tirage" not in st.session_state:
    st.session_state.tirage = None

# --- INTERFACE PRINCIPALE ---
st.markdown('<div class="title-main">🔮 Le Grand Maître</div>', unsafe_allow_html=True)

# Input match
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    team_home = st.text_input("🏠 Équipe Domicile", "Everton")
with col2:
    team_away = st.text_input("✈️ Équipe Extérieur", "Liverpool")
with col3:
    match_time = st.text_input("🕐 Heure", "16:30")

if st.button("🎲 Consulter le Fa", type="primary"):
    st.session_state.tirage = {f"M{i+1}": FIGURES[random.randint(1, 16)] for i in range(16)}
    st.rerun()

if st.session_state.tirage:
    # Affichage des figures
    st.markdown('<div class="subtitle-match">Les Figures du Thème</div>', unsafe_allow_html=True)
    
    # Grille 4x4 des figures
    cols = st.columns(4)
    for i, (key, val) in enumerate(st.session_state.tirage.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="card-figure">
                <div style="font-size:0.7em; color:#6b5d4d; margin-bottom:5px;">{key}</div>
                <div style="font-size:1.8em; margin:8px 0;">{"●" * (7 if val['element']=='Terre' else 6 if val['element']=='Air' else 5 if val['element']=='Feu' else 4)}</div>
                <div class="figure-name">{val['nom']}</div>
                <div class="figure-latin">({val['latin']})</div>
                <div class="figure-element">{val['icon']} {val['element']}</div>
                <div style="font-size:0.7em; color:#8b7355; margin-top:5px;">{val['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Analyse IA
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        api_key = st.sidebar.text_input("🔑 Clé API", type="password")
    
    if api_key and st.button("🧠 Analyse du Grand Maître", type="primary"):
        with st.spinner("🔮 Le Grand Maître consulte les astres..."):
            try:
                client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
                theme_str = "\n".join([f"{k}: {v['nom']} ({v['element']}) - {v['desc']}" for k, v in st.session_state.tirage.items()])
                
                prompt_final = f"""
                Match : {team_home} vs {team_away}
                Heure du coup d'envoi : {match_time}
                
                THÈME GÉOMANTIQUE COMPLET :
                {theme_str}
                
                {st.session_state.system_prompt}
                """
                
                rep = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt_final}],
                    temperature=0.3
                )
                
                st.markdown('<div class="section-title">🧠 Analyse du Grand Maître</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="analysis-box">
                {rep.choices[0].message.content.replace('\n', '<br>').replace('**', '').replace('*', '')}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
    elif not api_key:
        st.sidebar.warning("⚠️ Clé API requise")
