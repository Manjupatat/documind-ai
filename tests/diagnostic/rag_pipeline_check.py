from app.services.rag_pipeline import rag_pipeline


questions = ["Who can apply for the Sampurna challenge?", 
            "What are the eligibility criteria?",
            "What is the personal mobile number of the challenge director?",
            "Explain the history of the Indian railway system."]

for question in questions:
    result = rag_pipeline.ask(
        question=question,
        top_k=3
    )

    print("\nQUESTION:")
    print(result["question"])

    print("\nAI ANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(
            f'{source["source"]} - Page {source["page"]}'
        )