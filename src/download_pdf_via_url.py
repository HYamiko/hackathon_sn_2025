#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
from urllib.parse import urlparse, unquote
from pathlib import Path
import time

def extraire_nom_fichier(url):
    """Extrait un nom de fichier valide depuis l'URL."""
    parsed = urlparse(url)
    nom = os.path.basename(unquote(parsed.path))
    
    # Si pas d'extension .pdf, l'ajouter
    if not nom.lower().endswith('.pdf'):
        nom += '.pdf'
    
    # Si nom vide, générer un nom
    if not nom or nom == '.pdf':
        nom = f"document_{hash(url) % 100000}.pdf"
    
    return nom

def telecharger_pdfs(fichier_urls, repertoire_sortie='pdfs_telecharges'):
    """
    Télécharge tous les PDFs listés dans un fichier.
    
    Args:
        fichier_urls: Fichier contenant les URLs (une par ligne)
        repertoire_sortie: Dossier où sauvegarder les PDFs
    """
    # Créer le répertoire de sortie s'il n'existe pas
    Path(repertoire_sortie).mkdir(parents=True, exist_ok=True)
    
    stats = {
        'total': 0,
        'succes': 0,
        'echecs': 0,
        'ignores': 0
    }
    
    try:
        with open(fichier_urls, 'r', encoding='utf-8') as f:
            urls = [ligne.strip() for ligne in f if ligne.strip()]
        
        stats['total'] = len(urls)
        print(f"📄 {stats['total']} URL(s) trouvée(s)\n")
        
        for i, url in enumerate(urls, 1):
            # Ignorer les lignes qui ne sont pas des URLs
            if not url.startswith(('http://', 'https://')):
                print(f"[{i}/{stats['total']}] ⊘ Ignoré (pas une URL): {url[:60]}...")
                stats['ignores'] += 1
                continue
            
            try:
                print(f"[{i}/{stats['total']}] ⬇ Téléchargement: {url[:60]}...")
                
                # Télécharger avec timeout
                response = requests.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Vérifier le type de contenu
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                    print(f"    ⚠ Attention: Le contenu ne semble pas être un PDF ({content_type})")
                
                # Extraire le nom du fichier
                nom_fichier = extraire_nom_fichier(url)
                chemin_complet = os.path.join(repertoire_sortie, nom_fichier)
                
                # Éviter d'écraser des fichiers existants
                compteur = 1
                nom_base, ext = os.path.splitext(nom_fichier)
                while os.path.exists(chemin_complet):
                    nom_fichier = f"{nom_base}_{compteur}{ext}"
                    chemin_complet = os.path.join(repertoire_sortie, nom_fichier)
                    compteur += 1
                
                # Sauvegarder le fichier
                with open(chemin_complet, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                taille = os.path.getsize(chemin_complet) / 1024  # en Ko
                print(f"    ✓ Sauvegardé: {nom_fichier} ({taille:.1f} Ko)")
                stats['succes'] += 1
                
                # Petite pause pour éviter de surcharger le serveur
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"    ✗ Erreur de téléchargement: {e}")
                stats['echecs'] += 1
            except Exception as e:
                print(f"    ✗ Erreur: {e}")
                stats['echecs'] += 1
        
        # Afficher le résumé
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DU TÉLÉCHARGEMENT")
        print("="*60)
        print(f"Total d'URLs:        {stats['total']}")
        print(f"✓ Téléchargés:       {stats['succes']}")
        print(f"✗ Échecs:            {stats['echecs']}")
        print(f"⊘ Ignorés:           {stats['ignores']}")
        print(f"\n📁 Répertoire: {os.path.abspath(repertoire_sortie)}")
        
    except FileNotFoundError:
        print(f"✗ Erreur: Le fichier '{fichier_urls}' n'existe pas.")
    except Exception as e:
        print(f"✗ Erreur lors du traitement: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <fichier_urls> [repertoire_sortie]")
        print("\nExemple:")
        print("  python script.py urls.txt")
        print("  python script.py urls.txt mes_pdfs")
        print("\nLe fichier doit contenir une URL par ligne.")
    else:
        fichier = sys.argv[1]
        repertoire = sys.argv[2] if len(sys.argv) > 2 else 'pdfs_telecharges'
        telecharger_pdfs(fichier, repertoire)