from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

FAISS_PATH = "Ai-News-Aggregator/backend/faiss_db"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2"

print("Loading vector store...")
embeddings = OllamaEmbeddings(model=EMBED_MODEL)
vectorstore = FAISS.load_local(
    FAISS_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

print("Retrieving all stored articles...")
all_docs = list(vectorstore.docstore._dict.values())
print(f"Found {len(all_docs)} chunks in vector store")

llm = ChatOllama(model=LLM_MODEL, temperature=0.2)
interests=["men","food","fifa","chess","ipl","modi"]
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a news summarizer. "
     "Summarize the news articles below grouped by topic. "
     "Format your response like this:\n\n"
     "## [Topic Name]\n"
     "- Key point 1\n"
     "- Key point 2\n\n"
     "Keep each point to one sentence. Be factual.\n\n"
     "{context}\ninterests:{interests}"),
    ("human", "Summarize all the news articles above."),
])

print("Sending to Ollama for summarization...\n")

chain = (
    {"context": RunnablePassthrough(), "interests": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

summary = chain.invoke({"context": all_docs, "interests": interests})

print("=== NEWS SUMMARY ===")
print(summary)