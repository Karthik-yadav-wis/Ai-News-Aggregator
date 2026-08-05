import textwrap
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from services.faiss_services import embedding_model, get_vectorstore, save_vectorstore
from models import Article

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

BATCH_SIZE = 100

def process_and_store_articles(articles, db, interest_name):
    """
    Chunks + embeds a batch of articles into FAISS, skipping any article
    whose URL has already been ingested in a previous run (tracked via
    the Article table).

    `db` is a SQLAlchemy session — used to check/record ingested URLs.
    `interest_name` is the exact keyword these articles were fetched
    under — stored in each chunk's metadata so retrieval can filter to
    only chunks that genuinely belong to a given interest, rather than
    relying purely on vector similarity (which can't tell "Louis
    Partridge" and "JR NTR" apart if their chunks happen to be close
    in vector space).
    """
    documents = []
    metadatas = []
    seen_urls = set()
    new_article_rows = []
    source_key = interest_name.strip().lower()

    for article in articles:
        title = article.get("title") or ""
        description = article.get("description") or ""
        url = article.get("url", "")

        if not url:
            continue

        # Skip duplicates within this same batch
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # Skip articles already ingested in a previous run
        already_ingested = db.query(Article).filter(Article.url == url).first()
        if already_ingested:
            continue

        content = textwrap.dedent(f"""
            Title: {title}
            Description:
            {description}
        """).strip()

        chunks = text_splitter.split_text(content)
        added_any_chunk = False
        for chunk in chunks:
            if not chunk.strip():  # skip empty chunks
                continue
            documents.append(chunk)
            metadatas.append({
                "title": title,
                "url": url,
                "source_interest": source_key,
            })
            added_any_chunk = True

        if added_any_chunk:
            new_article_rows.append(Article(url=url, title=title))

    if documents:
        print(f"\n====CHUNKS===== ({len(documents)} total, {len(new_article_rows)} new articles)\n")
        try:
            vs = get_vectorstore()
            if vs is None:
                vs = FAISS.from_texts(
                    texts=documents[:BATCH_SIZE],
                    embedding=embedding_model,
                    metadatas=metadatas[:BATCH_SIZE]
                )
                for i in range(BATCH_SIZE, len(documents), BATCH_SIZE):
                    vs.add_texts(
                        texts=documents[i:i + BATCH_SIZE],
                        metadatas=metadatas[i:i + BATCH_SIZE]
                    )
            else:
                for i in range(0, len(documents), BATCH_SIZE):
                    vs.add_texts(
                        texts=documents[i:i + BATCH_SIZE],
                        metadatas=metadatas[i:i + BATCH_SIZE]
                    )
            save_vectorstore(vs)

            # Only record articles as "ingested" after FAISS storage succeeds,
            # so a failed embedding run can be retried on the next call.
            db.add_all(new_article_rows)
            db.commit()

        except Exception as e:
            print(f"[ERROR] Failed to store chunks: {e}")
            db.rollback()
            raise
    else:
        print("[process_and_store_articles] Nothing new to store — all articles already ingested.")

    return len(documents)