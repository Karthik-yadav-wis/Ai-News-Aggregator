import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

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