# AI Data Agent

Ce projet est un prototype d'agent IA capable d'interroger des données métier (Clients, Produits, Commandes) en langage naturel. Il utilise un stack moderne basé sur FastAPI, SQLite, Streamlit et des LLM via OpenRouter.

##  Fonctionnalités

- **Interface Intuitive** : Posez vos questions en français via une interface Streamlit.
- **Agent Intelligent** : Conversion automatique du langage naturel en requêtes SQL SQLite.
- **Génération de Données** : Peuplement automatique de la base de données avec des données réalistes via Faker.
- **Backend Robuste** : API performante avec FastAPI.

##  Stack Technique

- **Backend** : FastAPI
- **Base de Données** : SQLite 
- **Interface** : Streamlit
- **LLM** : OpenRouter 
- **Données** : Faker

##  Installation

1. **Cloner le projet** :
   ```bash
   git clone <repository-url>
   cd ai_data_agent
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration** :
   - Ajoutez votre clé API OpenRouter dans le fichier `.env`.

##  Démarrage

Le projet nécessite de lancer le backend et le frontend simultanément.

1. **Lancer le Backend (FastAPI)** :
   ```bash
   python -m uvicorn backend.main:app --reload
   ```
   Le backend sera accessible sur `http://localhost:8000`. La base de données sera automatiquement créée et peuplée lors du premier démarrage.

2. **Lancer le Frontend (Streamlit)** :
   ```bash
   python -m streamlit run frontend/app.py 
   ```
   L'interface sera accessible sur `http://localhost:8501`.

##  Tests

Pour garantir la fiabilité du code, vous pouvez lancer les tests unitaires avec la commande suivante :

   ```bash
   python -m unittest discover -s tests -v
   ```
