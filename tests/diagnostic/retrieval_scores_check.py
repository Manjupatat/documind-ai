
from app.services.vector_store import vector_store

document_id = "49b5712b-8e82-43bf-9592-2064a2bfc548"

questions = [
    "Who can apply for the Sampurna challenge?",
    "What are the eligibility criteria?",
    "What is the personal mobile number of the challenge director?",
    "Explain the history of the Indian railway system."
]

for question in questions:
    print("\n" + "=" * 70)
    print("QUESTION:", question)
    print("=" * 70)

    results = vector_store.search_with_scores(
        query=question,
        k=3,
        document_id=document_id
    )

    for index, (doc, distance) in enumerate(results, start=1):
        print(f"\nResult {index}")
        print(f"Raw Distance: {distance:.4f}")
        print(f"Source: {doc.metadata.get('source')}")
        print(f"Page: {doc.metadata.get('page')}")
        print(f"Content: {doc.page_content[:250]}...")
