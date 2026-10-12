import os
import requests
from dotenv import load_dotenv

#ON CHARGE LES CLES API. 
load_dotenv()
api_key =os.getenv("GEMINI_API_KEY")

#ICI, C'EST LA LOGIQUE POUR INTERROGER GOOGLE ET CONNAITRE LE NOM DES MODELES
if not api_key:
    print("❌ Erreur : Clé API introuvable dans le .env")#SI LA CLÉ N'EST PAS ENCORE DANS LE FICHIER .ENV
else:
    #Si la clé est bien là, on interroge les serveurs de Google.
    print("🔍 Interrogation des serveurs de Google...\n")
    url=f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    #L'UTILISATION DE L'OUTIL REQUESTS
    try:
        reponse = requests.get(url)
        donnees = reponse.json()

        print("Voici les noms exacts pouvant être utilisés dans le code :")
        print("-"*50)

        #LA BOUCLE POUR AFFICHER LES NOMS DES MODÈLES ET CE QU'ILS PEUVENT FAIRE
        for modele in donnees.get("models", []):
                #On nettoie pour afficher sans le préfixe "models/"
                nom=modele['name'].replace('models/', '')
                #On récupère la liste des capacités du modèle
                methodes = modele.get("supportedGenerationMethods", [])
                #On affiche maintenant le nom et ses capacités
                print(f"✅ {nom}")
                print(f"    -> Capacités : {', '.join(methodes)}\n")

    except Exception as e:
        print(f"Erreur réseau : {e}")