import os
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import text
import re

class AIAgent:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1" ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
        # Modèle spécialisé pour le SQL (très précis sur la structure)
        self.model_sql = "tngtech/deepseek-r1t2-chimera:free"
        
        # Modèle spécialisé pour le langage naturel (plus fluide et "humain")
        self.model_chat = "liquid/lfm-2.5-1.2b-thinking:free"

    def sqlGeneration(self, question: str) -> str:
        prompt = f"""
        Tu es un expert SQL spécialisé en SQLite.

        Contexte :
        Tu disposes uniquement du schéma suivant :

        Table customers (
            id INTEGER,
            name TEXT,
            email TEXT,
            city TEXT,
            created_at DATETIME
        )

        Table products (
            id INTEGER,
            name TEXT,
            category TEXT,
            price REAL
        )

        Table orders (
            id INTEGER,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date DATETIME,
            total_amount REAL
        )

        Règles STRICTES :
        - Utilise UNIQUEMENT les tables et colonnes listées ci-dessus
        - N’invente JAMAIS de colonnes ou de tables
        - Respecte la syntaxe SQLite
        - Si une jointure est nécessaire, utilise les clés logiques (customer_id, product_id)
        - Ne mets AUCUN commentaire
        - Ne mets AUCUN texte explicatif
        - Retourne UNIQUEMENT la requête SQL valide

        Tâche :
        Génère la requête SQL correspondant exactement à la question suivante :

        "{question}"
        Si la question ne concerne pas les clients, produits ou commandes, retourne "NON_LIE".
                """
        
        response = self.client.chat.completions.create(
            model=self.model_sql,  
            messages=[{"role": "user", "content": prompt}]
        )
        
        sql = response.choices[0].message.content.strip()
        
        sql = re.sub(r'```sql|```', '', sql).strip()
        match = re.search(r'(SELECT|WITH|INSERT|UPDATE|DELETE|CREATE)\b', sql, re.IGNORECASE)
        if match:
            sql = sql[match.start():]
            
        return sql

    def ececution(self, db: Session, sql: str):
        try:
            result = db.execute(text(sql))
            return [dict(row._mapping) for row in result]
        except Exception:
            return None

    def genererReponseNaturelle(self, question: str, data: list) -> str:
        prompt = f"""
        Tu es un assistant intelligent. Un utilisateur a posé la question : "{question}"
        Les données récupérées de la base de données sont : {data}
        
        Rédige une réponse claire et concise en français en langage naturel basée sur ces données.
        Si les données sont vides, indique qu'aucune information n'a été trouvée.
        """
        
        response = self.client.chat.completions.create(
            model=self.model_chat,  # Utilise le modèle Chat
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    
    def question(self, db: Session, question_text: str):
        sql = self.sqlGeneration(question_text)
        
        if sql == "NON_LIE":
            return "Désolé, je ne peux répondre qu'aux questions concernant les clients, les produits et les commandes."
        
        data = self.ececution(db, sql)

        if data is None:
            # Correction ici : utilisation de sqlGeneration au lieu de generate_sql
            sql = self.sqlGeneration(
                question_text + " (attention : génère une requête SQL valide SQLite)"
            )
            # Correction ici : utilisation de ececution au lieu de execute_query
            data = self.ececution(db, sql)

        if data is None:
            return "Je n’ai pas pu répondre correctement. Merci de reformuler."
            
        # Correction ici : utilisation de genererReponseNaturelle au lieu de generate_natural_response
        return self.genererReponseNaturelle(question_text, data)
