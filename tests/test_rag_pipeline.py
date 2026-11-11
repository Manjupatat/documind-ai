# from .app.services.rag_pipeline import rag_pipeline
from app.services.rag_pipeline import rag_pipeline


question = "Who can apply for the Sampurna challenge?"

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