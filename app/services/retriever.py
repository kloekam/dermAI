import os
import json
from pathlib import Path

import faiss
import numpy as np

from app.services.embedder import embed_query


BASE = Path(__file__).resolve().parents[2]
FAISS_INDEX_PATH = BASE / "output" / "index.faiss"
METADATA_PATH = BASE / "output" / "metadata.json"
TOP_K = 5

index = faiss.read_index(str(FAISS_INDEX_PATH))
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)


def normalize_skin_type(value):
    if not value:
        return None
    value = str(value).strip().lower()
    allowed = {"oily", "dry", "normal", "combination", "sensitive", "all"}
    return value if value in allowed else None


def classify_query(query: str) -> str:
    q = (query or "").lower()

    guideline_terms = {
        "psoriasis", "guideline", "plaque", "topical steroid",
        "nhs", "nice", "clinical", "scalp psoriasis"
    }
    ingredient_terms = {
        "ingredient", "organic", "natural", "aloe", "tea tree",
        "jojoba", "niacinamide", "salicylic acid", "hyaluronic acid"
    }
    product_terms = {
        "product", "cleanser", "serum", "moisturizer", "moisturiser",
        "sunscreen", "toner", "mask", "face wash", "best products"
    }

    if any(term in q for term in guideline_terms):
        return "guideline"
    if any(term in q for term in ingredient_terms):
        return "ingredient"
    if any(term in q for term in product_terms):
        return "product"
    return "product"


def _matches_entity(item, entity_type):
    if not entity_type or entity_type == "all":
        return True
    return item.get("entity_type") == entity_type


def _matches_skin_type(item, selected_skin_type):
    if not selected_skin_type:
        return True

    item_skin_type = (item.get("skin_type") or "").lower()
    if not item_skin_type:
        return True

    parts = {p.strip() for p in item_skin_type.split(",") if p.strip()}
    return selected_skin_type in parts or "all" in parts


def _boost_score(item, query, score):
    q = query.lower()
    boosted = float(score)

    category = (item.get("category") or "").lower()
    product_name = (item.get("product_name") or "").lower()
    concerns = (item.get("concerns") or "").lower()
    text = (item.get("text") or "").lower()

    if "cleanser" in q and "cleanser" in category:
        boosted += 0.15
    if "oily" in q and "oily" in (item.get("skin_type") or "").lower():
        boosted += 0.10
    if "dry" in q and "dry" in (item.get("skin_type") or "").lower():
        boosted += 0.10
    if "dryness" in q and "dryness" in concerns:
        boosted += 0.10
    if any(word in q for word in ["oily", "acne", "blemish"]) and any(word in text for word in ["salicylic", "niacinamide", "foaming"]):
        boosted += 0.05
    if any(word in q for word in ["dry", "dryness", "hydrating"]) and any(word in text for word in ["ceramide", "hyaluronic", "glycerin", "squalane"]):
        boosted += 0.05
    if product_name and any(token in product_name for token in q.split()):
        boosted += 0.03

    return boosted


def _dedupe_key(item):
    entity_type = item.get("entity_type")

    if entity_type == "product":
        return (
            entity_type,
            item.get("product_name", ""),
            item.get("category", ""),
            item.get("url", ""),
        )
    if entity_type == "ingredient":
        return (
            entity_type,
            item.get("ingredient_name", ""),
            item.get("problem", ""),
            item.get("skin_type", ""),
        )
    return (
        entity_type,
        item.get("chunk_id", ""),
        item.get("page_number", ""),
    )


def retrieve(query, filters=None, top_k=TOP_K):
    filters = filters or {}
    selected_skin_type = normalize_skin_type(filters.get("skin_type"))
    entity_type = filters.get("entity_type")

    query_vec = embed_query(query)
    if len(query_vec.shape) == 1:
        query_vec = np.array([query_vec], dtype="float32")

    scores, indices = index.search(query_vec.astype("float32"), top_k * 8)

    candidates = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        item = metadata[idx].copy()

        if not _matches_entity(item, entity_type):
            continue
        if not _matches_skin_type(item, selected_skin_type):
            continue

        item["score"] = _boost_score(item, query, score)
        candidates.append(item)

    if not candidates:
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            item = metadata[idx].copy()
            if _matches_entity(item, entity_type):
                item["score"] = float(score)
                candidates.append(item)

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

    deduped = []
    seen = set()
    for item in candidates:
        key = _dedupe_key(item)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= top_k:
            break

    return deduped