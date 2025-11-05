# @title Imports
import os
import pandas as pd
from datasets import Dataset
import asyncio
import nest_asyncio
from typing import List, Optional, Any, Dict # Garder pour type hints si besoin
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_mistralai.embeddings import MistralAIEmbeddings
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

MISTRAL_API_KEY = "StthE16bt5IReMHPxgjbwtQLGggjOGtq"
# Appliquer nest_asyncio
nest_asyncio.apply()

questions_test = [
    "Qu'est ce que La demi-lune ?",
    "Quelles sont les résultats de deux années d'essai de la demi-lune à Pougyango ont montré"
]
answers = [
    "La demi-lune est une technique de conservation des sols et d'amélioration de la production agricole, particulièrement utilisée dans les zones arides et semi-arides. Elle consiste à créer des micro-bassins de rétention d'eau en forme de demi-lune autour des plantes ou des cultures. Ces demi-lunes aident à capturer et à retenir l'eau de pluie, réduisant ainsi le ruissellement et permettant une meilleure infiltration de l'eau dans le sol. Cette technique est souvent utilisée dans les régions où les précipitations sont irrégulières et où la conservation de l'eau est cruciale pour la croissance des cultures",
    """Les résultats de deux années d'essai à Pougyango ont montré que :

La combinaison demi-lune et fumier donne une production variant entre 1,2 à 1,6 t/ha de grains de sorgho local.
La combinaison demi-lune et compost obtient un rendement de 15 à 24 fois supérieur à celui de la demi-lune sans apport de fertilisant.
Les apports d'amendements organiques non encore décomposés (paillage) associés au Burkina Phosphate fournissent des productions moyennes de l'ordre de 0,6 t/ha de grains de sorgho local.
La demi-lune seule sans aucune fumure donne une production inférieure à 0,1 t/ha de grains.
En cas de pluviométrie excédentaire, les rendements baissent en raison des inondations temporaires qui influencent négativement le développement des cultures."""
]

placeholder_contexts = [
    "La demi-lune est une technique de conservation des sols et d'amélioration de la production agricole, particulièrement utilisée dans les zones arides et semi-arides. Elle consiste à créer des micro-bassins de rétention d'eau en forme de demi-lune autour des plantes ou des cultures. Ces demi-lunes aident à capturer et à retenir l'eau de pluie, réduisant ainsi le ruissellement et permettant une meilleure infiltration de l'eau dans le sol. Cette technique est souvent utilisée dans les régions où les précipitations sont irrégulières et où la conservation de l'eau est cruciale pour la croissance des cultures",
    "récupération_terre_par_technique_demi-lune"
]
ground_truths = [
    "La demi-lune est une cuvette de la forme d'un demi-cercle ouverte à l'aide de pic, pioche et pelle",
"""
La combinaison demi-lune et fumier donne une production variant entre 1,2 à 1,6 t/ha de grains de sorgho local 
La combinaison demi-lune et compost obtient un rendement de 15 à 24 fois supérieur à celui de la demi-lune 
sans apport de fertilisant 
Les apports d'amendements organiques non encore décomposés (paille) associés au Burkina Phosphate 
fournissent des productions moyennes de l'ordre de 0,6 t/ha de grains de sorgho local 
La demi-lune seule sans aucune fumure donne une production inférieure à 0,1 t/ha de grains. Le simple fait 
de casser la croûte superficielle du sol afin d'améliorer l'alimentation hydrique du sol n'a pas suffit à 
augmenter le rendement du sorgho 
En cas de pluviométrie excédentaire comme ce fut le cas en 1999 (747 mm), les rendements baissent en 
raison des inondations temporaires qui influencent négativement le développement des cultures
"""
]

evaluation_data = {
    "question": questions_test,
    "answer": answers,
    "contexts": placeholder_contexts,
    "ground_truth": ground_truths # Assurez-vous que cette clé correspond à ce que Ragas attend (parfois 'reference' ou autre)
}


# Convertir en Dataset de Hugging Face
evaluation_dataset = Dataset.from_dict(evaluation_data)
print("Dataset créé.")

try:
    # 1. Instancier le LLM et les Embeddings via Langchain (SIMPLE)
    print("Initialisation du LLM ChatMistralAI...")
    mistral_llm = ChatMistralAI(
        mistral_api_key=MISTRAL_API_KEY,
        model="mistral-large-latest", # Ou un autre modèle chat supporté
        temperature=0.1
    )
    print("LLM initialisé.")

    print("\nInitialisation des embeddings MistralAIEmbeddings...")
    mistral_embeddings = MistralAIEmbeddings(
        mistral_api_key=MISTRAL_API_KEY
        # model="mistral-embed" # Le modèle par défaut est généralement correct
    )
    print("Embeddings initialisés.")

    # 2. Définir les métriques (les noms sont généralement les mêmes)
    metrics_to_evaluate = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ]
    print(f"\nMétriques sélectionnées: {[m.name for m in metrics_to_evaluate]}")

    # 3. Lancer l'évaluation Ragas

    print("\nLancement de l'évaluation Ragas ...")
    results = evaluate(
        dataset=evaluation_dataset,
        metrics=metrics_to_evaluate,
        llm=mistral_llm,              # Instance Langchain standard
        embeddings=mistral_embeddings # Instance Langchain standard
        # Ragas gère les appels async/sync en interne avec les objets Langchain
    )
    print("\n--- Évaluation Ragas terminée ---")

    # 4. Afficher les résultats
    print("\n--- Résultats ---")
    print(results) # Le format de sortie peut varier légèrement avec les versions

    # Optionnel : Affichage DataFrame si la structure le permet
    if isinstance(results, dict) and 'ragas_score' in results:
            print(f"\nScore RAGAS global : {results['ragas_score']:.4f}")
            # Afficher les scores par métrique s'ils sont disponibles directement
            for metric in metrics_to_evaluate:
                if metric.name in results:
                    print(f"Score {metric.name}: {results[metric.name]:.4f}")
    else:
        try:
                # Essayer de convertir en DataFrame si c'est un Dataset ou similaire
                results_df = results.to_pandas()
                print("\n--- Résultats (DataFrame) ---")
                pd.set_option('display.max_columns', None)
                print(results_df.head(len(results_df)))
        except AttributeError:
                print("\nFormat de résultat non convertible directement en DataFrame Pandas.")


except Exception as e:
    print(f"\nUne erreur est survenue lors de l'initialisation ou l'évaluation : {e}")
    import traceback
    print("\nTraceback:")
    traceback.print_exc()