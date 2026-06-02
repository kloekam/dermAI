from app.services.retriever import retrieve, classify_query
from app.services.generator import generate_answer


def ask_question(question, filters=None, history=None):
    filters = filters or {}

    entity_used = filters.get("entity_type") or classify_query(question)
    merged_filters = dict(filters)
    merged_filters["entity_type"] = entity_used

    chunks = retrieve(question, merged_filters)
    answer = generate_answer(question, chunks)

    sources = []
    for c in chunks:
        sources.append({
            "name": c.get("product_name") or c.get("ingredient_name") or c.get("source_dataset"),
            "entity_type": c.get("entity_type"),
            "category": c.get("category", ""),
            "score": round(c.get("score", 0) * 100, 1),
            "page_number": c.get("page_number"),
        })

    return {
        "answer": answer,
        "sources": sources,
        "entity_type_used": entity_used,
    }