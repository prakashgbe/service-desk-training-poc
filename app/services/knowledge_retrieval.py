import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_DIR / "data" / "chroma_db"

COLLECTION_NAME = "service_desk_knowledge"
EMBEDDING_MODEL = "gemini-embedding-001"


class KnowledgeRetrievalService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY was not found in the .env file."
            )

        self.genai_client = genai.Client(api_key=api_key)

        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = self.chroma_client.get_collection(
            name=COLLECTION_NAME
        )

    def retrieve(self, question, top_k=3):
        """Retrieve relevant knowledge sections for a question."""

        response = self.genai_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=question,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            ),
        )

        query_embedding = response.embeddings[0].values

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        retrieved_items = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            retrieved_items.append(
                {
                    "content": document,
                    "document_id": metadata["document_id"],
                    "document_version": metadata["document_version"],
                    "source_file": metadata["source_file"],
                    "section_heading": metadata["section_heading"],
                    "chunk_index": metadata["chunk_index"],
                    "distance": distance,
                }
            )

        return retrieved_items