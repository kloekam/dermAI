import re


SKIN_TYPE_KEYWORDS = {
    "oily": ["oily", "oil control", "oil-control", "shine", "blemish", "acne"],
    "dry": ["dry", "dehydrated", "hydrating", "moisturizing", "moisturising", "comfort"],
    "sensitive": ["sensitive", "calming", "soothing", "gentle", "redness"],
    "combination": ["combination", "combo"],
    "normal": ["normal"],
}

CONCERN_KEYWORDS = {
    "acne": ["acne", "blemish", "breakout", "salicylic"],
    "dryness": ["dry", "dehydrated", "hydrating", "moisturizing", "moisturising"],
    "sensitivity": ["sensitive", "redness", "soothing", "calming"],
    "aging": ["wrinkle", "firming", "anti-aging", "ageing", "fine line"],
    "pores": ["pores", "pore", "charcoal", "clay"],
}


def _norm(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _infer_skin_type(*parts):
    blob = " ".join(_norm(p).lower() for p in parts if p)
    hits = [skin for skin, words in SKIN_TYPE_KEYWORDS.items() if any(w in blob for w in words)]
    return ", ".join(hits) if hits else ""


def _infer_concerns(*parts):
    blob = " ".join(_norm(p).lower() for p in parts if p)
    hits = [concern for concern, words in CONCERN_KEYWORDS.items() if any(w in blob for w in words)]
    return ", ".join(hits) if hits else ""


def product_chunks(records):
    chunks = []
    for i, r in enumerate(records):
        product_name = _norm(r.get("product_name")) or "Unknown"
        category = _norm(r.get("category")) or "Unknown"
        ingredients = _norm(r.get("ingredients")) or "Not provided"
        brand = _norm(r.get("brand"))
        price = _norm(r.get("price")) or "Unknown"
        url = _norm(r.get("url"))

        skin_type = _norm(r.get("skin_type"))
        concerns = _norm(r.get("concerns"))

        inferred_skin_type = skin_type or _infer_skin_type(product_name, category, ingredients)
        inferred_concerns = concerns or _infer_concerns(product_name, category, ingredients)

        text_parts = [
            f"Product: {product_name}.",
            f"Category: {category}.",
        ]
        if brand:
            text_parts.append(f"Brand: {brand}.")
        text_parts.append(f"Ingredients: {ingredients}.")
        if inferred_skin_type:
            text_parts.append(f"Best for skin types: {inferred_skin_type}.")
        if inferred_concerns:
            text_parts.append(f"Relevant concerns: {inferred_concerns}.")
        text_parts.append(f"Price: {price}.")
        if url:
            text_parts.append(f"URL: {url}.")

        meta = dict(r)
        meta["chunk_id"] = f"product_{i}"
        meta["skin_type"] = inferred_skin_type
        meta["concerns"] = inferred_concerns
        meta["text"] = " ".join(text_parts)
        chunks.append(meta)

    return chunks


def organic_chunks(records):
    chunks = []
    for i, r in enumerate(records):
        ingredient_name = _norm(r.get("ingredient_name")) or "Unknown"
        category = _norm(r.get("category")) or "Unknown"
        skin_type = _norm(r.get("skin_type")) or "Unknown"
        problem = _norm(r.get("problem")) or "Unknown"
        symptoms = _norm(r.get("symptoms")) or "Unknown"
        benefits = _norm(r.get("benefits")) or "Unknown"
        usage = _norm(r.get("usage")) or "Unknown"
        notes = _norm(r.get("notes")) or "Unknown"

        text = (
            f"Natural ingredient: {ingredient_name}. "
            f"Category: {category}. "
            f"Best for: {skin_type}. "
            f"Problem addressed: {problem}. "
            f"Symptoms: {symptoms}. "
            f"Benefits: {benefits}. "
            f"How to use: {usage}. "
            f"Notes: {notes}."
        )

        meta = dict(r)
        meta["chunk_id"] = f"ingredient_{i}"
        meta["text"] = text
        chunks.append(meta)

    return chunks


def pdf_chunks(pages, max_chars=1100, overlap=180):
    chunks = []
    for page in pages:
        paras = [p.strip() for p in re.split(r"\n\s*\n|\n", page["text"]) if p.strip()]
        buffer = ""
        idx = 0

        for para in paras:
            if len(buffer) + len(para) + 1 <= max_chars:
                buffer = (buffer + " " + para).strip()
            else:
                if buffer:
                    chunks.append({
                        "chunk_id": f"guideline_p{page['page_number']}_{idx}",
                        "source_dataset": "nice_psoriasis_guideline",
                        "entity_type": "guideline",
                        "page_number": page["page_number"],
                        "category": "clinical_guideline",
                        "skin_type": "",
                        "concerns": "psoriasis",
                        "is_natural": "n/a",
                        "text": buffer,
                    })
                    idx += 1
                buffer = (buffer[-overlap:] + " " + para).strip() if overlap < len(buffer) else para

        if buffer:
            chunks.append({
                "chunk_id": f"guideline_p{page['page_number']}_{idx}",
                "source_dataset": "nice_psoriasis_guideline",
                "entity_type": "guideline",
                "page_number": page["page_number"],
                "category": "clinical_guideline",
                "skin_type": "",
                "concerns": "psoriasis",
                "is_natural": "n/a",
                "text": buffer,
            })

    return chunks