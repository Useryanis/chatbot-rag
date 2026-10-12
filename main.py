#ON IMPORTE LES OUTILS NECESSAIRES
import os
from dotenv import load_dotenv
from google import genai
from groq import Groq
import time
from gtts import gTTS
import pygame
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory 
from langchain_core.prompts import PromptTemplate
#ON CHARGE LES CLÉS API
load_dotenv()

#ON INITIALISE LA MÉMOIRE CENTRALE PARTAGÉE PAR LES DEUX CERVEAUX
memoire=ConversationBufferMemory()
print("--- 🚀Mémoire opérationnelle ---\n")

#ON INITIALISE PROPREMENT LES CERVEAUX DE GROQ ET GEMINI
llm1=ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-2.5-flash"
)
llm2=ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-2.5-flash"
)
print("--- 🤖 Système initialisé ---\n")

#ON RELIE ICI CHAQUE CERVEAU À LA MÉMOIRE CENTRALE.
chaine1= ConversationChain(llm=llm1, memory=memoire)
chaine2= ConversationChain(llm=llm2, memory=memoire)

#INITIALISATION SÉCURISÉE DE L'AUDIO
audio = False
try:
    pygame.mixer.init()
    audio = True
except pygame.error:
    print("🛑 Attention : Carte son introuvable (Mode silencieux activé).")

#ON DEFINIT MAINTENANT LA FONCTION QUI VA PERMETTRE À L'ASSISTANT DE BASCULER DE MANIÈRE INTELLIGENTE ENTRE LES MODES FLASH ET PRO EN FONCTION DE LA REQUETE.
def choisir(texte):
    mots=["physique", "maths", "python", "django", "algorithme", "matrice", "vectoriel", "algèbre", "exercice", "td", "optique", "analyse"]
    if any( mot in texte.lower() for mot in mots):
        return "gemini"
    else:
        return "groq"

#ICI, C'EST LA FONCTION QUI VA NOUS PERMETTRE DE PARLER À L'UTILISATEUR
def parler(texte):
    if not audio:
        return #On annule si l'audio ne marche pas
    
    phrase = texte.split(". ")[0]
    tts = gTTS(text=phrase, lang='fr')
    tts.save("voix.mp3")
    pygame.mixer.music.load("voix.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

#LA BOUCLE PRINCIPALE DEFINISSANT LE SCHEMA DE LA DISCUSSION
while True:
    requete = input("Entrez votre message ou tapez 'quitter' pour arrêter la discussion:\n>>  ")
    if requete.lower() == "quitter":
        print("Au revoir✨👋")
        break
    fournisseur = choisir(requete)
    try:
        print(f"--- Modèle activé : {fournisseur.upper()} ---")
        #ON AJUSTE MAINTENANT LE CHOIX DU MODELE EN FONCTION DE LA REQUETE
        if fournisseur == "gemini":
            print("--- 🧠 Mode Réflexion ---")
            texte_final=chaine2.predict(input=requete)

        else:
            print("--- ⚡ Mode Rapide ---")
            texte_final=chaine1.predict(input=requete)

        print(f"\nAssistant: {texte_final}")
        parler(texte_final)

    except Exception as e:
        print(f"\nErreur de Connexion: {e}")