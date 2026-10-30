import json
from pathlib import Path

from minimal_rag.rag import ask_rag


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_PATH = PROJECT_ROOT / "data" / "evaluation.json"


def load_evaluation_questions() -> list[dict]:
    return json.loads(
        EVALUATION_PATH.read_text(encoding="utf-8")
    )
    
def evidence_hit_at_k(
    retrieved_documents: list,
    relevant_chunk_ids: list[str],
) -> bool:
    retrieved_ids = {
        doc.metadata["chunk_id"]
        for doc in retrieved_documents
    }

    return bool(
        retrieved_ids.intersection(relevant_chunk_ids)
    )


def main():
    questions = load_evaluation_questions()

    hits = 0
    answerable_count = 0

    for item in questions:
        result = ask_rag(
            question=item["question"]
        )
        
        if not item["answerable"]:
            continue

        answerable_count += 1

        hit = evidence_hit_at_k(
            retrieved_documents=result["retrieved_documents"],
            relevant_chunk_ids=item["relevant_chunk_ids"],
        )

        hits += int(hit)

        print(
            f"{item['id']} - Evidence Hit@3: {hit}"
        )
        
    print(
        f"\nEvidence Hit@3: {hits / answerable_count:.2%}"
    )



if __name__ == "__main__":
    main()