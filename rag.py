import os
import time 
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.globals import set_debug
from langchain_core.runnables import RunnableLambda

#Pour permettre de traquer tout le cheminement de l'IA 
#set_debug(True)

#Ici, on charge les clés API 
load_dotenv()

print("🧠 1. Initialisation du modèle d'Embeddings (Modèle Stable)....")
# Utilisation du modèle stable pour éviter les bugs de requêtes vides
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

nom_dossier_faiss = "memoire_pdf_locale"

# SYSTÈME ANTI-ERREUR 429 : On sauvegarde le PDF sur le disque pour ne pas payer la taxe Google à chaque lancement
if os.path.exists(nom_dossier_faiss):
    print("💾 2. Chargement de la base vectorielle depuis le disque dur (Rapide et gratuit !)...")
    database = FAISS.load_local(nom_dossier_faiss, embeddings, allow_dangerous_deserialization=True)
else:
    print("📜 2. Première lecture : Vectorisation du PDF en cours (Ceci ne se fera qu'une seule fois)...")
    loader = PyPDFLoader("cours.pdf")
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    morceaux = splitter.split_documents(documents)
    database = FAISS.from_documents(morceaux, embeddings)
    database.save_local(nom_dossier_faiss) # On sauvegarde pour les prochaines fois

chercheur = database.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20})

print("🤖 3. Connexion au cerveau Gemini....")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Reformulateur de question strict
recherche = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", """Question de l'utilisateur : {input}

INSTRUCTION STRICTE : En te basant sur notre historique de conversation ci-dessus, reformule cette question pour qu'elle devienne une requête de recherche complète et autonome. 
Tu dois OBLIGATOIREMENT générer une phrase. Ne donne AUCUNE réponse à la question, écris UNIQUEMENT la question reformulée pour fouiller le document.""")
])

# Le "nettoyeur" qui garantit que l'IA ne crashe pas sur du texte mal formaté
nettoyeur = RunnableLambda(lambda x: str(x).strip())

# Application du nettoyeur avant la recherche
retriever = create_history_aware_retriever(llm, nettoyeur | chercheur, recherche)

reponse = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant strict. Réponds en te basant UNIQUEMENT sur le contexte ci-dessous. \n\nContexte: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])

chaine_document = create_stuff_documents_chain(llm, reponse)
chaine_conversationnelle = create_retrieval_chain(retriever, chaine_document) 

print("\n✅ Assimilation terminée ! Tu peux poser une question pour commencer ta révision sur ton PDF ou tape 'quitter' pour terminer la discussion.\n")

historique = []

while True:
    question = input(">> ")
    
    if question.lower() == "quitter":
        print("Fin de la session de révision. À bientôt 👋✨!")
        break

    reponse_ia = chaine_conversationnelle.invoke({
        "input": question,
        "chat_history": historique
    })
    
    print(f"\nAssistant: {reponse_ia['answer']}")

    historique.append(HumanMessage(content=question))
    historique.append(AIMessage(content=reponse_ia['answer']))
    
    time.sleep(2) # Pause de sécurité