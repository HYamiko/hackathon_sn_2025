# Assistant RAG avec Mistral

Ce projet implémente un assistant virtuel basé sur le modèle Mistral, utilisant la technique de Retrieval-Augmented Generation (RAG) pour fournir des réponses précises et contextuelles à partir d'une base de connaissances personnalisée.


## Installation

1. **Cloner le dépôt**

```bash
git clone <url-du-repo>
cd <nom-du-repo>
```

2. **Créer un environnement virtuel**

```bash

# Création de l'environnement virtuel
python -m venv venv

# Activation de l'environnement virtuel
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Configurer la clé API**

Créez un fichier `.env` dans la racine du projet avec le contenu suivant :

```
MISTRAL_API_KEY=votre_clé_api_mistral
```


### 1. Télécharger les documents

```bash
# Aller dans `src`
cd src
# Ensuite lancer le telechargement
python download_pdf_via_url.py ../data/sources.txt inputs/docs

```

### 2. Indexer les documents

Exécutez le script d'indexation pour traiter les documents et créer l'index FAISS :

```bash
python indexer.py
```

Ce script va :
1. Charger les documents depuis le dossier `inputs/`
2. Découper les documents en chunks
3. Générer des embeddings avec Mistral
4. Créer un index FAISS pour la recherche sémantique
5. Sauvegarder l'index et les chunks dans le dossier `vector_db/`

### 3. Lancer l'application

```bash
streamlit run MistralChat.py
```

L'application sera accessible à l'adresse http://localhost:8501 dans votre navigateur.


Excellente demande 👌 — vous voulez que je **analyse votre code** et **documente les bibliothèques Python utilisées**, afin de comprendre ce qu’elles font et pourquoi elles sont nécessaires dans votre projet.

Voici la **documentation détaillée** des librairies employées dans votre script `app.py`.

---

## 🧩 **Bibliothèques externes utilisées**

### 1. **streamlit**

📦 **Import :**

```python
import streamlit as st
```

📝 **Rôle :**

* Framework Python pour créer des **interfaces web interactives** pour vos applications de data science ou d’IA.
* Il gère ici toute l’interface du **chatbot municipal** (affichage du chat, sidebar, boutons, sliders, feedback…).

🎯 **Fonctions utilisées :**

* `st.set_page_config()`: définit le titre, l’icône et la mise en page.
* `st.sidebar`, `st.title`, `st.caption`, `st.chat_message`, `st.chat_input`, `st.download_button` : construisent l’interface.
* `st.cache_resource`: met en cache certains objets (évite de recharger inutilement les modèles ou bases vectorielles).
* `st.toast()`: affiche des notifications temporaires.

📚 **Doc :** [https://docs.streamlit.io](https://docs.streamlit.io)

---

### 2. **mistralai**

📦 **Imports :**

```python
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
```

📝 **Rôle :**

* SDK officiel pour interagir avec **l’API Mistral AI**, un fournisseur de modèles de langage (LLMs).
* `MistralClient`: gère les appels à l’API.
* `ChatMessage`: structure un message pour les modèles de type chat.

⚠️ **Note importante :**
Ces chemins d’importation (`mistralai.client`, `mistralai.models.chat_completion`) sont **obsolètes** depuis les dernières versions.
👉 Il faut désormais utiliser :

```python
from mistralai import Mistral
```

et appeler le chat via :

```python
client.chat.complete(...)
```

📚 **Doc actuelle :** [https://docs.mistral.ai](https://docs.mistral.ai)

---

### 3. **logging**

📦 **Import :**

```python
import logging
```

📝 **Rôle :**

* Fournit un moyen standard d’enregistrer des messages (informations, avertissements, erreurs).
* Utilisé ici pour suivre l’exécution du code : initialisation des composants, appels à l’API, erreurs, etc.

📚 **Doc :** [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html)

---

### 4. **datetime**

📦 **Import :**

```python
import datetime
```

📝 **Rôle :**

* Manipule les dates et heures (utile pour les logs, les timestamps de conversation, ou les noms de fichiers).
* Exemples :

  * `datetime.datetime.now()` → récupère la date/heure actuelle.
  * `strftime()` → formate la date pour l’affichage ou le nom de fichier.

📚 **Doc :** [https://docs.python.org/3/library/datetime.html](https://docs.python.org/3/library/datetime.html)

---

### 5. **streamlit-feedback**

📦 **Import :**

```python
from streamlit_feedback import streamlit_feedback
```

📝 **Rôle :**

* Composant communautaire pour **collecter le feedback utilisateur** dans une app Streamlit.
* Permet d’ajouter des **boutons “👍 / 👎”**, des zones de commentaire, etc.
* Vous l’utilisez pour évaluer les réponses du chatbot.

📚 **Doc :** [https://pypi.org/project/streamlit-feedback/](https://pypi.org/project/streamlit-feedback/)

---

## 🧱 **Modules internes (locaux)**

Ces modules font partie de **votre propre projet**, dans le dossier `utils/`.

### 6. `utils.config`

📦 **Import :**

```python
from utils.config import APP_TITLE, COMMUNE_NAME, MISTRAL_API_KEY
```

📝 **Rôle :**

* Contient probablement les **constantes de configuration** :

  * Le titre de l’application.
  * Le nom de la commune.
  * La clé API Mistral.

---

### 7. `utils.vector_store`

📦 **Import :**

```python
from utils.vector_store import VectorStoreManager
```

📝 **Rôle :**

* Gère la **base de connaissances vectorielle** utilisée pour la recherche sémantique (RAG).
* Contient les méthodes de recherche (`search`) pour trouver les documents les plus pertinents selon la question.

---

### 8. `utils.database`

📦 **Import :**

```python
from utils.database import log_interaction, update_feedback
```

📝 **Rôle :**

* Gère la **persistance des conversations et du feedback**.
* `log_interaction()` → enregistre chaque interaction (question, réponse, sources).
* `update_feedback()` → met à jour la base avec les retours utilisateur.

---

### 9. `utils.query_classifier`

📦 **Import :**

```python
from utils.query_classifier import QueryClassifier
```

📝 **Rôle :**

* Contient un **classificateur** qui détermine si une requête nécessite une recherche RAG (dans la base documentaire) ou non.
* Retourne une décision binaire (`needs_rag`) avec un **score de confiance** et une **raison**.

---

## 🧩 Récapitulatif général

| Catégorie           | Bibliothèque             | Type     | Rôle principal                      |
| ------------------- | ------------------------ | -------- | ----------------------------------- |
| 🖥️ Interface       | `streamlit`              | externe  | Interface web interactive           |
| 💬 IA / LLM         | `mistralai`              | externe  | Connexion à l’API Mistral           |
| 🪵 Journalisation   | `logging`                | standard | Logs de débogage et suivi           |
| ⏱️ Temps            | `datetime`               | standard | Gestion des dates et heures         |
| 👍 Feedback         | `streamlit-feedback`     | externe  | Collecte des retours utilisateurs   |
| ⚙️ Config           | `utils.config`           | interne  | Variables de configuration          |
| 🔍 RAG / recherche  | `utils.vector_store`     | interne  | Recherche vectorielle               |
| 🗃️ Base de données | `utils.database`         | interne  | Gestion des interactions / feedback |
| 🧠 Classification   | `utils.query_classifier` | interne  | Détection du mode de réponse        |

---