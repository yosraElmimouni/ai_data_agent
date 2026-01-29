import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Configuration de la page
st.set_page_config(
    page_title="AI Data Agent | Test Technique",
    layout="wide"
)

load_dotenv()

# Style CSS personnalisé pour une allure plus moderne
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .response-container {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("images/robot.png", width=80)
    st.title("Paramètres")
    
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        api_key = st.sidebar.text_input("Clé API OpenRouter", type="password")

    st.divider()
    st.subheader(" Suggestions")
    examples = [
        "Combien de clients avons-nous ?",
        "Quels sont les 5 produits les plus vendus ?",
        "Quel est le chiffre d'affaires du mois dernier ?",
        "Quels clients n'ont pas commandé depuis 3 mois ?",
        "Compare les ventes de janvier et février"
    ]
    
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state.question = ex

    st.divider()
    st.info("Cet agent utilise un LLM pour traduire vos questions en requêtes SQL sécurisées.")

# --- MAIN INTERFACE ---
st.title("📊 AI Data Agent")
st.subheader("Interrogez vos données métier en langage naturel")

# Initialisation de l'état de la question
if "question" not in st.session_state:
    st.session_state.question = ""

# Zone de saisie principale
col1, col2 = st.columns([4, 1])
with col1:
    question = st.text_input("Posez votre question ici :", 
                            value=st.session_state.question, 
                            placeholder="Ex: Quel est le produit le plus rentable ?",
                            label_visibility="collapsed")
with col2:
    submit_button = st.button("Analyser")

# --- LOGIQUE DE RÉPONSE ---
if submit_button or (question and st.session_state.question != question):
    if not api_key:
        st.error("⚠️ Veuillez configurer votre clé API dans la barre latérale.")
    elif not question:
        st.warning("👉 Veuillez saisir une question.")
    else:
        # Affichage de la question posée
        with st.chat_message("user"):
            st.write(question)

        # Appel au backend
        with st.chat_message("assistant"):
            with st.spinner("Analyse de la base de données en cours..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/ask",
                        json={"question": question, "api_key": api_key},
                        timeout=30
                     )
                    
                    if response.status_code == 200:
                        answer = response.json().get("response")
                        st.markdown("### Résultat de l'analyse")
                        st.markdown(f'<div class="response-container">{answer}</div>', unsafe_allow_html=True)
                        
                        # Optionnel : Ajout d'un bouton pour voir les données brutes si nécessaire
                        # st.expander("Voir les détails techniques").code(answer)
                        
                    else:
                        st.error(f"Erreur du serveur ({response.status_code})")
                        st.info(response.text)
                except Exception as e:
                    st.error(f"Connexion au backend impossible. Vérifiez que le serveur FastAPI est lancé sur le port 8000.")
                    st.exception(e)

# --- FOOTER ---
st.divider()
footer_col1, footer_col2 = st.columns(2)
with footer_col1:
    st.caption("© 2026 AI Data Agent Prototype")
with footer_col2:
    st.markdown("<p style='text-align: right; color: gray; font-size: 0.8em;'>Statut Backend : En ligne ✅</p>", unsafe_allow_html=True)
