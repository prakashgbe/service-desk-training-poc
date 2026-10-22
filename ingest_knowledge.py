import os
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent
SOP_PATH = (
    PROJECT_DIR
    / "data"
    / "knowledge"
    / "wifi_troubleshooting_sop.md"
)
CHROMA_PATH = PROJECT_DIR / "data" / "chroma_db"

DOCUMENT_ID = "SOP-NET-001"
DOCUMENT_VERSION = "1.0"
COLLECTION_NAME = "service_desk_knowledge"
EMBEDDING_MODEL = "gemini-embedding-001"


def split_by_headings(text):
    """Split Markdown text into sections using heading boundaries."""

    sections = re.split(r"(?m)(?=^#{1,6}\s+)", text.strip())
    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        heading_match = re.match(r"(?m)^#{1,6}\s+(.+)$", section)
        heading = heading_match.group(1).strip() if heading_match else "Introduction"

        chunks.append(
            {
                "heading": heading,
                "text": section,
            }
        )

    return chunks


def main():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found in .env")

    if not SOP_PATH.exists():
        raise FileNotFoundError(f"SOP file not found: {SOP_PATH}")

    document_text = SOP_PATH.read_text(encoding="utf-8")

    if not document_text.strip():
        raise ValueError("The SOP file is empty.")

    chunks = split_by_headings(document_text)

    if not chunks:
        raise ValueError("No sections were extracted from the SOP.")

    genai_client = genai.Client(api_key=api_key)

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Service Desk training knowledge"},
    )

    existing = collection.get()

    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    for index, chunk in enumerate(chunks):
        response = genai_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=chunk["text"],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            ),
        )

        embedding = response.embeddings[0].values

        collection.add(
            ids=[
                f"{DOCUMENT_ID}-v{DOCUMENT_VERSION}-chunk-{index}"
            ],
            documents=[chunk["text"]],
            embeddings=[embedding],
            metadatas=[
                {
                    "document_id": DOCUMENT_ID,
                    "document_version": DOCUMENT_VERSION,
                    "source_file": SOP_PATH.name,
                    "section_heading": chunk["heading"],
                    "chunk_index": index,
                }
            ],
        )

        print(
            f"Indexed section {index + 1}/{len(chunks)}: "
            f"{chunk['heading']}"
        )

    print("\nKnowledge ingestion completed successfully.")
    print(f"Document: {SOP_PATH.name}")
    print(f"Sections indexed: {len(chunks)}")
    print(f"Vector database: {CHROMA_PATH}")


if __name__ == "__main__":
    main()