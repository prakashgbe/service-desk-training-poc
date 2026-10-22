import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent
CHROMA_PATH = PROJECT_DIR / "data" / "chroma_db"

COLLECTION_NAME = "service_desk_knowledge"
EMBEDDING_MODEL = "gemini-embedding-001"


def main():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found in the .env file."
        )

    client = genai.Client(api_key=api_key)

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    question = (
        "My laptop cannot connect to the wireless network. "
        "What should I check first?"
    )

    print(f"\nLearner question:\n{question}\n")
    print("Generating question embedding...")

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        ),
    )

    query_embedding = response.embeddings[0].values

    print("Searching the knowledge base...\n")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for index, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):
        print(f"--- Retrieved chunk {index} ---")
        print(f"Source: {metadata['source_file']}")
        print(f"Document ID: {metadata['document_id']}")
        print(f"Version: {metadata['document_version']}")
        print(f"Chunk index: {metadata['chunk_index']}")
        print(f"Distance: {distance:.4f}")
        print(f"\nContent:\n{document}\n")

    print("Retrieval test completed.")


if __name__ == "__main__":
    main()