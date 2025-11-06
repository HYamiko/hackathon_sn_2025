#  RAG AVEC MISTRAL HACKATHON SEMAINE DU NUMERIQUE




[Video de presentation](https://www.youtube.com/watch?v=TpCsrKS_Bdw)
## 🧠 Introduction

Ce projet implémente un **système RAG (Retrieval-Augmented Generation)** :
il combine des **modèles de langage (LLMs)** avec un **index vectoriel** pour permettre une recherche intelligente dans un corpus local de documents.

Il repose principalement sur :

* **MistralAI** comme moteur de génération,
* **LangChain** pour la logique d’orchestration,
* **FAISS** ou équivalent pour l’index vectoriel,
* des outils Python classiques pour la donnée et le traitement.

## 🌍 Contexte scientifique et socio-économique

L’agriculture est le **pilier économique du Burkina Faso**.
Selon les données de la **Banque mondiale** et de l’**INSD**, elle :

* contribue à **plus de 30 % du PIB national** ;
* emploie **plus de 70 % de la population active** ;
* constitue la **principale source de revenus et de sécurité alimentaire**.

Malgré cela, le secteur reste fortement exposé à :

* la **variabilité climatique** (sécheresses, irrégularité des pluies) ;
* la **dégradation des sols** ;
* la **faible accessibilité à l’information agronomique** (techniques de culture, maladies des plantes, gestion de l’eau, etc.) ;
* et la **faible diffusion de la recherche scientifique** auprès des producteurs.

---

## 🧩 Problématique scientifique

Les agriculteurs et techniciens agricoles du Burkina Faso disposent souvent de **données dispersées et non structurées** :

* rapports techniques (INERA, CNRST, FAO, etc.),
* publications scientifiques,
* guides de bonnes pratiques,
* bulletins climatiques,
* documents PDF non indexés ou difficilement exploitables.

👉 Le défi est donc **de valoriser ce savoir existant** pour en faire **un outil d’aide à la décision**.

---

## 🧠 Justification du choix de l’agriculture pour un RAG

Le **RAG (Retrieval-Augmented Generation)** permet d’exploiter de grandes quantités d’informations **non structurées** (textes, rapports, documents PDF) afin de :

* extraire automatiquement les **informations pertinentes** ;
* générer des **réponses contextuelles et fiables** à des questions précises ;
* et éviter les **hallucinations des modèles de langage** en s’appuyant sur une **base documentaire vérifiée**.

Appliqué à l’agriculture, cela ouvre la voie à une **IA de vulgarisation scientifique**, capable de répondre à des questions comme :

* « Quelle variété de maïs est la plus adaptée à la région du Centre-Ouest ? »
* « Comment traiter la striga ou la rouille du mil ? »
* « Quelles pratiques de conservation des sols limitent la sécheresse ? »

Scientifiquement, ce choix se justifie car :

* L’agriculture est un **système complexe**, multidimensionnel (climat, biologie, économie, sol, eau).
  → Le RAG aide à **intégrer et interconnecter** ces dimensions.
* Les documents agricoles sont souvent **non structurés et volumineux**,
  → Le RAG est **optimal** pour extraire et synthétiser ce type d’information.
* Il contribue à **la science ouverte et à la diffusion des connaissances** locales et internationales.

---

## 💻 Pertinence technologique du RAG pour l’agriculture

| Enjeu                              | Apport du RAG                                                                                                               |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 🌾 **Vulgarisation agricole**      | Un assistant qui répond aux questions des agriculteurs en langue simple, basé sur des données locales (INERA, FAO, CIRAD…). |
| ☀️ **Changement climatique**       | Accès rapide aux recherches et recommandations sur la résilience, l’adaptation et la gestion de l’eau.                      |
| 🧬 **Maladies et ravageurs**       | Consultation automatisée des guides phytosanitaires et fiches techniques.                                                   |
| 📈 **Optimisation des rendements** | Synthèse de données agronomiques, historiques pluviométriques, et pratiques culturales.                                     |
| 🔗 **Transfert de connaissances**  | Mise à disposition du savoir scientifique des chercheurs vers les acteurs de terrain.                                       |

---


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

## 🧠 **1. LangChain**

📦 **Installation :**

```bash
pip install langchain
```

📚 **Documentation :**
[https://python.langchain.com](https://python.langchain.com)

---

### 📝 **Rôle général**

LangChain est une **bibliothèque de haut niveau pour orchestrer des modèles de langage (LLMs)**.
Elle permet de **chaîner** des étapes logiques : prompts, récupération de contexte, appels à un modèle, post-traitement, stockage, etc.

C’est la **colonne vertébrale typique d’un projet RAG (Retrieval-Augmented Generation)**.

---

### ⚙️ **Fonctionnalités principales**

| Domaine                           | Description                                           | Exemple typique               |
| --------------------------------- | ----------------------------------------------------- | ----------------------------- |
| 🧩 **Chains**                     | Enchaînement d’actions (prompt → LLM → sortie).       | `LLMChain`, `SequentialChain` |
| 💬 **Chat Models**                | Interfaces unifiées pour GPT, Mistral, Claude, etc.   | `ChatOpenAI`, `ChatMistralAI` |
| 📚 **Retrievers / Vector Stores** | Recherche sémantique de documents.                    | `FAISS`, `Chroma`, `Pinecone` |
| 🧠 **Memory**                     | Historique des conversations (chat contextuel).       | `ConversationBufferMemory`    |
| 🔗 **Agents**                     | Systèmes autonomes capables de choisir leurs actions. | `initialize_agent()`          |
| 🧰 **Tools**                      | Intégration d’outils externes (API, fichiers, code).  | `PythonREPLTool`, `SerpAPI`   |

---

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
