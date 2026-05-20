import textwrap
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.chroma_services import vectorstore

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

BATCH_SIZE = 100

def process_and_store_articles(articles):
    documents = []
    metadatas = []
    seen_urls = set()

    for article in articles:
        title = article.get("title") or ""
        description = article.get("description") or ""
        url = article.get("url", "")

        #Deduplicate by URL
        if url in seen_urls:
            continue
        seen_urls.add(url)

        content = textwrap.dedent(f"""
            Title: {title}

            Description:
            {description}
        """).strip()

        chunks = text_splitter.split_text(content)

        for chunk in chunks:
            if not chunk.strip():  #skip empty chunks
                continue
            documents.append(chunk)
            metadatas.append({"title": title, "url": url})

    if documents:
        print(f"\n====CHUNKS===== ({len(documents)} total)\n")
        for i, chunk in enumerate(documents):
            print("Chunk ",i+1,":\n", chunk)
            print("\n" + "=" * 50)

        try:
            for i in range(0, len(documents), BATCH_SIZE):
                vectorstore.add_texts(
                    texts=documents[i:i+BATCH_SIZE],
                    metadatas=metadatas[i:i+BATCH_SIZE]
                )
        except Exception as e:
            print(f"[ERROR] Failed to store chunks: {e}")
            raise

    return len(documents)