from app.services.knowledge_retrieval import (
    KnowledgeRetrievalService,
)


def main():
    service = KnowledgeRetrievalService()

    question = (
        "My laptop cannot connect to the wireless network. "
        "What should I check first?"
    )

    results = service.retrieve(question, top_k=3)

    print(f"\nQuestion: {question}\n")

    for index, item in enumerate(results, start=1):
        print(f"--- Result {index} ---")
        print(f"Section: {item['section_heading']}")
        print(f"Source: {item['source_file']}")
        print(f"Document ID: {item['document_id']}")
        print(f"Version: {item['document_version']}")
        print(f"Distance: {item['distance']:.4f}")
        print(f"\n{item['content']}\n")


if __name__ == "__main__":
    main()