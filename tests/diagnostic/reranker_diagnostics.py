
from app.services.vector_store import vector_store
from app.services.reranker_service import reranker_service


def run_reranker_diagnostics():

    tests = [
        {
            "name": "KSP — Relevant",
            "question": "What did the user ask the assistant to investigate?",
            "document_id": "80e2e5b7-c453-41ce-b4f3-f0ede5efde00"
        },
        {
            "name": "KSP — Unrelated",
            "question": "What are the eligibility criteria for agricultural startups?",
            "document_id": "80e2e5b7-c453-41ce-b4f3-f0ede5efde00"
        },
        {
            "name": "Grand Challenge — Clearly unrelated",
            "question": "What is the capital city of Japan?",
            "document_id": "9b056381-7716-4279-9262-49b78bd687ac"
        },
        {
            "name": "Grand Challenge — Relevant",
            "question": "Which seven crops are given special emphasis in the programme?",
            "document_id": "9b056381-7716-4279-9262-49b78bd687ac"
        }
    ]

    print("\n" + "=" * 80)
    print("DOCUMIND AI — RERANKER DIAGNOSTICS")
    print("=" * 80)

    for test in tests:

        print("\n" + "-" * 80)
        print(f"TEST: {test['name']}")
        print(f"QUESTION: {test['question']}")
        print(f"DOCUMENT ID: {test['document_id']}")
        print("-" * 80)

        # Step 1: Retrieve candidate chunks.
        candidates = vector_store.search(
            query=test["question"],
            k=10,
            document_id=test["document_id"]
        )

        print(f"\nRetrieved candidates: {len(candidates)}")

        if not candidates:
            print("No documents retrieved.")
            continue

        # Step 2: Rerank candidates.
        results = reranker_service.rerank(
            query=test["question"],
            documents=candidates,
            top_n=3
        )

        if not results:
            print("No reranked results.")
            continue

        # Step 3: Display ranking scores and content.
        for rank, (doc, score) in enumerate(results, start=1):

            print(f"\nRank       : {rank}")
            print(f"Score      : {float(score):.4f}")
            print(f"Source     : {doc.metadata.get('source')}")
            print(f"Page       : {doc.metadata.get('page')}")
            print(f"Document ID: {doc.metadata.get('document_id')}")

            content = doc.page_content.replace("\n", " ")

            print(f"Content    : {content[:300]}...")

    print("\n" + "=" * 80)
    print("DIAGNOSTICS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_reranker_diagnostics()
