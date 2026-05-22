import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings 

embedding_model = OllamaEmbeddings(model="nomic-embed-text")

FAISS_PATH = "./faiss_db"

# Don't create it here — just declare it
vectorstore = None

def get_vectorstore():
    global vectorstore

    if vectorstore is not None:
        return vectorstore

    if os.path.exists(FAISS_PATH):
        # Load existing DB from disk
        vectorstore = FAISS.load_local(
            FAISS_PATH,
            embedding_model,
            allow_dangerous_deserialization=True
        )
    else:
        # DB doesn't exist yet — will be created when first articles are stored
        vectorstore = None

    return vectorstore


def save_vectorstore(vs):
    global vectorstore
    vectorstore = vs
    vs.save_local(FAISS_PATH)