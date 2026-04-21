import streamlit as st
import random
from openai import OpenAI

st.set_page_config(page_title="Le Grand Maître", page_icon="🔮", layout="wide")

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

DEFAULT_PROMPT = """Tu es LE GRAND MAÎTRE DU RAMLI AFRICAIN. Analyse ce thème géomantique pour un match de football.
DONNE EXACTEMENT :
1. Fiabilité du thème (%)
2. Dominante élémentaire & type de match (Fermé/Ouvert)
3. Vainqueur probable & Score exact
4. Total buts (Over/Under) & Les 2 marquent ?
5. Incidents (Cartons rouges/jaunes, Pénalty, VAR)
6. Conseil stratégique
Utilise les règles strictes du Ramli africain. Sois précis."""

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_PROMPT
if "last_theme" not in st.session_state:
    st.session_state.last_theme = ""
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = ""

st.title("🔮 Le Grand Maître - Géomancie Football")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 🔑 GESTION AUTOMATIQUE DE LA CLÉ API
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        api_key = st.text_input("🔑 Clé API Groq", type="password", value=st.session_state.get("temp_key", ""))
        if api_key:
            st.session_state.temp_key = api_key
            st.success("🔑 Clé active pour cette session")
    else:
        st.success("🔑 Clé chargée automatiquement (sécurisée)")
    
    st.markdown("---")
    st.subheader("📜 Éducation IA")
    new_prompt = st.text_area("Prompt Système", value=st.session_state.system_prompt, height=180)
    if st.button("💾 Sauvegarder les règles"):
        st.session_state.system_prompt = new_prompt
        st.success("✅ Règles mises à jour !")

col1, col2 = st.columns(2)
with col1:
    team_home = st.text_input("🏠 Domicile", "Everton")
with col2:
    team_away = st.text_input("✈️ Extérieur", "Liverpool")

if st.button("🎲 Lancer un Tirage"):
    st.session_state.tirage = {f"M{i+1}": FIGURES[random.randint(1, 16)] for i in range(16)}
    st.session_state.last_theme = "\n".join([f"{k}: {v['nom']} ({v['element']})" for k, v in st.session_state.tirage.items()])
    st.success("✅ Thème généré !")

if "tirage" in st.session_state:
    st.subheader("📜 Figures du Thème")
    cols = st.columns(2)
    for i, (k, v) in enumerate(st.session_state.tirage.items()):
        emoji = {"Feu":"🔥", "Eau":"💧", "Air":"💨", "Terre":"⛰️"}.get(v["element"], "•")
        cols[i%2].write(f"**{k}**: {v['nom']} {emoji}")
        
    st.markdown("---")
    if api_key:
        if st.button("🧠 Analyser avec l'IA", type="primary"):
            with st.spinner("Le Grand Maître consulte les astres..."):
                try:
                    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
                    rep = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": st.session_state.system_prompt},
                            {"role": "user", "content": f"Match: {team_home} vs {team_away}\n\nThème:\n{st.session_state.last_theme}"}
                        ]
                    )
                    st.session_state.last_prediction = rep.choices[0].message.content
                    st.success("✅ Analyse terminée")
                    st.subheader("🔮 Interprétation")
                    st.markdown(st.session_state.last_prediction)
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
    else:
        st.warning("⚠️ Ajoute ta clé dans secrets.toml ou via le champ ci-dessus.")

# MODULE POST-MATCH
if "last_prediction" in st.session_state and st.session_state.last_prediction:
    st.markdown("---")
    with st.expander("🔄 Match terminé ? Corrige l'IA ici"):
        st.info("Entre le résultat réel pour générer une nouvelle règle.")
        real_score = st.text_input("Score final réel")
        real_events = st.text_area("Événements clés (VAR, cartons, pénaltys...)")
        
        if st.button("🧠 Analyser l'erreur & Générer une règle"):
            if real_score and real_events and api_key:
                with st.spinner("Analyse post-match..."):
                    try:
                        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
                        prompt_corr = f"""
                        Tu es expert en géomancie africaine.
                        THÈME: {st.session_state.last_theme}
                        PRÉDICTION IA: {st.session_state.last_prediction}
                        RÉSULTAT RÉEL: Score {real_score} | Événements: {real_events}
                        
                        TÂCHE: Explique brièvement l'erreur, puis propose UNE NOUVELLE RÈGLE précise au format:
                        "NOUVELLE RÈGLE: [Condition] -> [Correction]."
                        """
                        rep = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt_corr}])
                        st.markdown(rep.choices[0].message.content)
                        if st.button("✅ Appliquer cette règle au système"):
                            st.session_state.system_prompt += "\n\n" + rep.choices[0].message.content
                            st.success("🎉 Règle ajoutée !")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
            else:
                st.warning("Remplis tous les champs et vérifie ta clé API.")
