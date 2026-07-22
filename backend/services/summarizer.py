from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.chroma_services import get_vectorstore

LLM_MODEL = "llama3.2"
CHUNKS_PER_INTEREST = 5  # how many relevant chunks to pull per topic

llm = ChatOllama(model=LLM_MODEL, temperature=0.2)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a news summarizer. "
     "Summarize the news articles below for the topic: {topic}. "
     "Format your response like this:\n\n"
     "## {topic}\n"
     "- Key point 1\n"
     "- Key point 2\n\n"
     "Keep each point to one sentence. Be factual. "
     "If there is not enough information, say so briefly instead of making things up.\n\n"
     "Articles:\n{context}"),
    ("human", "Summarize the articles above."),
])

chain = prompt | llm | StrOutputParser()


def summarize_topic(topic: str) -> str:
    """Retrieve relevant chunks for one topic/interest and summarize them."""
    vs = get_vectorstore()

    if vs is None:
        return f"## {topic}\nNo articles have been stored yet."

    docs = vs.similarity_search(topic, k=CHUNKS_PER_INTEREST)

    if not docs:
        return f"## {topic}\nNo relevant articles found."

    context = "\n\n---\n\n".join(d.page_content for d in docs)

    return chain.invoke({"topic": topic, "context": context})


def summarize_interests(interests: list[str]) -> str:
    """Summarize news for a list of interests, one section each."""
    sections = [summarize_topic(topic) for topic in interests]
    return "\n\n".join(sections)