import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.faiss_services import get_vectorstore
from langchain_google_genai  import  ChatGoogleGenerativeAI

load_dotenv()

LLM_MODEL = "gemini-flash-latest"
CHUNKS_PER_INTEREST = 8  # how many relevant chunks to pull per topic

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
     "- Key point 3\n\n"
     "Keep each point to one sentence. Be factual. "
     "Do not repeat the same point twice, even if phrased differently."
     "If there is not enough information, give brief information about the topic\n\n"
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