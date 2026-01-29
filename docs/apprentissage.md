# Apprentissage & Communication

## 3.1 - Quelque chose de nouveau : Le Text-to-SQL

Pendant ce test, j'ai approfondi le concept de **Text-to-SQL**. C'est une technologie qui permet de traduire une intention exprimée en langage naturel (comme le français) en une requête structurée compréhensible par une base de données.

Imaginez que vous parlez à un traducteur qui ne traduit pas entre deux langues humaines, mais entre une langue humaine et le "langage des machines". Pour que cela fonctionne bien, il ne suffit pas de donner la question au traducteur ; il faut aussi lui donner le "contexte" (le schéma de la base de données) pour qu'il sache quels mots correspondent à quelles tables.

## 3.2 - Votre approche

### Organisation du temps
- **Jour 1** : Analyse du besoin et conception de la structure du projet.
- **Jour 2** : Mise en place du backend FastAPI et de la base de données SQLite avec Faker.
- **Jour 3** : Intégration du LLM et développement de la logique de l'agent (Text-to-SQL).
- **Jour 4** : Création de l'interface Streamlit et tests de bout en bout.
- **Jour 5** : Rédaction de la documentation et finalisation du projet.

### Sources d'aide
- **Documentation officielle** : FastAPI, SQLAlchemy et Streamlit pour les détails d'implémentation.
- **OpenRouter Docs** : Pour comprendre comment appeler différents modèles via une API unique.
- **IA (Manus)** : Pour m'aider à structurer le code et générer des exemples de données réalistes.

### Ce que j'aurais fait différemment
Avec plus de temps, j'aurais ajouté :
1. **Tests Unitaires** : Pour garantir que chaque composant (génération SQL, exécution, réponse) fonctionne isolément.
2. **Visualisation de données** : Intégrer des graphiques (Plotly ou Altair) dans Streamlit pour accompagner les réponses textuelles de l'agent.
3. **Gestion de contexte** : Permettre à l'agent de se souvenir des questions précédentes pour une expérience plus conversationnelle.
