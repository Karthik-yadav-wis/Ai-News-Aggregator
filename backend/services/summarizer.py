import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.faiss_services import get_vectorstore

load_dotenv()

# Embeddings + FAISS stay on Ollama (nomic-embed-text) — only the
# generation step moves to Gemini. Don't switch the embeddings model
# without rebuilding the FAISS index from scratch; vectors from two
# different embedding models aren't compatible with each other.
LLM_MODEL = "gemini-flash-latest"
CHUNKS_PER_INTEREST = 5

# FAISS's default distance metric is L2 (Euclidean) — LOWER means MORE
# similar. There's no universal "good" cutoff since it depends on the
# embedding model's scale, so this value may need tuning: lower it if
# genuinely relevant topics are getting filtered out as "no info found";
# raise it if irrelevant topics are still slipping through to the LLM.
MAX_RELEVANT_DISTANCE = 0.9

llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a news summarizer. "
     "Summarize the news articles below for the topic: {topic}. "
     "Format your response like this:\n\n"
     "## {topic}\n"
     "- Key point 1\n"
     "- Key point 2\n\n"
     "Keep each point to one sentence. Be factual. "
     "Write only the news content itself — never mention that you are an AI, "
     "never refer to 'the provided articles' or 'the context', and never add "
     "disclaimers about missing or insufficient information. Every article "
     "given to you IS relevant, so summarize what's actually there.\n\n"
     "Articles:\n{context}"),
    ("human", "Summarize the articles above."),
])

chain = prompt | llm | StrOutputParser()

# Used when there's no relevant news for a topic. Gives general background
# on the topic itself instead of surfacing that no news was found — keeps
# every card populated with something useful rather than an empty/negative
# result. Deliberately asks for evergreen facts, not recent events, since
# there's no article content backing this up.
fallback_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Provide a brief factual overview of the topic below, in this exact format:\n\n"
     "## {topic}\n"
     "- Point 1\n"
     "- Point 2\n\n"
     "Keep each point to one sentence. Stick to well-known, evergreen background "
     "facts about who or what this is and why it's notable — do NOT invent recent "
     "news, current events, or anything time-sensitive, since none is available. "
     "Never mention news, articles, or that information is missing — just "
     "describe the topic itself factually, as a short bio or overview."),
    ("human", "Give a brief overview of {topic}."),
])

fallback_chain = fallback_prompt | llm | StrOutputParser()


def summarize_topic(topic: str) -> str:
    """Retrieve relevant chunks for one topic/interest and summarize them.
    Falls back to a general overview of the topic if no relevant articles
    were found, rather than surfacing that gap to the user."""
    vs = get_vectorstore()

    if vs is None:
        return fallback_chain.invoke({"topic": topic})

    topic_key = topic.strip().lower()

    # Widen the candidate pool since we're about to filter it down by
    # BOTH distance AND exact source-interest match — a narrow pool
    # filtered twice could come back empty even when good matches exist.
    scored_docs = vs.similarity_search_with_score(topic, k=CHUNKS_PER_INTEREST * 3)

    relevant_docs = [
        doc for doc, score in scored_docs
        if score <= MAX_RELEVANT_DISTANCE
        and doc.metadata.get("source_interest") == topic_key
    ][:CHUNKS_PER_INTEREST]

    if not relevant_docs:
        return fallback_chain.invoke({"topic": topic})

    context = "\n\n---\n\n".join(d.page_content for d in relevant_docs)

    return chain.invoke({"topic": topic, "context": context})


def summarize_interests(interests: list[str]) -> str:
    """Summarize news for a list of interests, one section each."""
    sections = [summarize_topic(topic) for topic in interests]
    return "\n\n".join(sections)