from google.adk.agents import Agent

from app.services.knowledge_retrieval import (
    KnowledgeRetrievalService,
)


retrieval_service = KnowledgeRetrievalService()


def search_approved_knowledge(question: str) -> dict:
    """
    Search approved knowledge documents for relevant information.

    Args:
        question: The learner's troubleshooting question.

    Returns:
        Relevant document sections and their source metadata.
    """
    results = retrieval_service.retrieve(
        question=question,
        top_k=3,
    )

    if not results:
        return {
            "found": False,
            "message": "No relevant knowledge sections were retrieved.",
            "sources": [],
        }

    sources = []

    for item in results:
        sources.append(
            {
                "document_id": item["document_id"],
                "document_version": item["document_version"],
                "source_file": item["source_file"],
                "section_heading": item["section_heading"],
                "content": item["content"],
            }
        )

    return {
        "found": True,
        "sources": sources,
    }


knowledge_agent = Agent(
    name="knowledge_agent",
    model="gemini-3.5-flash-lite",
    description=(
        "Helps Service Desk learners troubleshoot issues "
        "using approved knowledge documents."
    ),
    instruction="""
You are the Knowledge Agent in a Service Desk engineer training platform.

For every troubleshooting question:

1. Call the search_approved_knowledge tool before answering.
2. Base company-specific troubleshooting instructions on the retrieved content.
3. Explain the relevant steps clearly to a junior Service Desk engineer.
4. Preserve the intended sequence of troubleshooting steps described in the SOP.
5. Cite the source document ID, version, and section heading.
6. Do not invent company-specific procedures or claim that a procedure is
   approved unless the retrieved source supports that claim.
7. If the retrieved content does not adequately answer the question,
   clearly state that the available knowledge is insufficient.
8. You may explain general technical concepts when helpful, but distinguish
   them from instructions contained in the approved knowledge documents.

You retrieve information and explain procedures. You do not execute
troubleshooting actions, modify systems, or certify learner competency.
""",
    tools=[search_approved_knowledge],
)