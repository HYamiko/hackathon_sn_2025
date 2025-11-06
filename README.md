# Assistant IA Contextuel – Agriculture au Burkina Faso

## Sujet choisi

**Domaine : Agriculture au Burkina Faso**
 Ce projet vise à construire un **assistant IA contextuel open source**, capable de répondre à des questions sur l’agriculture burkinabè
 L’objectif est de **faciliter l’accès à l’information agricole locale**, même sans connexion Internet, grâce à un système **RAG (Retrieval-Augmented Generation)** exécuté localement.

**Architecture Technique**

**Pipeline RAG**

Question utilisateur
       ↓
Embeddings (HuggingFace)
       ↓
Recherche vectorielle (ChromaDB)
       ↓
Documents pertinents
       ↓
Génération (LLM - Mistral via Ollama)
       ↓
Réponse + Sources



**Composants open source utilisés**

| Composant        | Technologie                                                  | Licence    | Lien |
| ---------------- | ------------------------------------------------------------ | ---------- | ---- |
| LLM              | [Mistral (via Ollama)](https://ollama.ai/library/mistral)    | Apache 2.0 | ✅    |
| Embeddings       | [HuggingFace Embeddings (Sentence-Transformers - paraphrase-multilingual-mpnet-base-v2)](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2) | Apache 2.0 | ✅    |
| Base vectorielle | [ChromaDB](https://www.trychroma.com/)                       | Apache 2.0 | ✅    |
| RAG Framework    | [LlamaIndex](https://github.com/run-llama/llama_index)       | MIT        | ✅    |
| Backend API      | [Django REST Framework](https://www.django-rest-framework.org/) | BSD        | ✅    |
| Frontend         | [Streamlit](https://streamlit.io)                            | Apache 2.0 | ✅    |
| Parsing          | BeautifulSoup4, Requests                                     | MIT        | ✅    |

**Description du code – `RAGService`**

Le fichier `rag_service.py` contient la classe `RAGService`, responsable de toute la logique RAG (singleton, initialisation, requêtes, statistiques).

### **Principales fonctionnalités :**

- **Initialisation automatique du pipeline** (`_initialize_pipeline`)
- **Connexion à ChromaDB** et chargement des embeddings
- **Configuration dynamique** à partir de `settings.RAG_CONFIG`
- **Récupération des sources pertinentes** (`retrieve_sources`)
- **Requêtes avec ou sans streaming** (`query` et `query_streaming`)
- **Statistiques du système** (`get_stats`)

**Commandes d'installation**

**Requirement: mistral en local**

- git clone https://github.com/HYamiko/hackathon_sn_2025.git
- cd hackathon_sn_2025
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- cd src
- python indexer.py
- cd backend
- python manage.py runserver
- cd ../../frontend
- streamlit run app.py
