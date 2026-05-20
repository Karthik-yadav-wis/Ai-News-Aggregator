from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embedding_model=OllamaEmbeddings(model="nomic-embed-text")

vectorstore=Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model,
)
