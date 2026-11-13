
from app.services.vector_store import vector_store
from app.services.reranker_service import reranker_service


document_id = "49b5712b-8e82-43bf-9592-2064a2bfc548"

questions = [
    "Who can apply for the Sampurna challenge?",
    "What are the eligibility criteria?",
    "What is the personal mobile number of the challenge director?",
    "Explain the history of the Indian railway system."
]

for question in questions:

    print("\n" + "=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    # Step 1: Retrieve 10 candidate chunks
    documents = vector_store.search(
        query=question,
        k=10,
        document_id=document_id
    )

    print("\nRetrieved candidates:", len(documents))

    # Step 2: Rerank candidates
    results = reranker_service.rerank(
        query=question,
        documents=documents,
        top_n=3
    )

    # Step 3: Display reranked results
    for index, (doc, score) in enumerate(results, start=1):

        print(f"\nReranked Result {index}")
        print(f"Reranker Score: {float(score):.4f}")
        print(f"Page: {doc.metadata.get('page')}")
        print(f"Source: {doc.metadata.get('source')}")
        print(f"Content: {doc.page_content[:300]}...")
