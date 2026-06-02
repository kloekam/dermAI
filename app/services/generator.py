import re


def generate_answer(question, chunks):
    if not chunks:
        return (
            "I could not find a clear answer in the current dermAI knowledge base. "
            "Try rephrasing your question or ask about a product, ingredient, or psoriasis guidance."
        )

    if any(c.get("entity_type") == "guideline" for c in chunks):
        intro = "I found relevant clinical guidance and skincare knowledge."
    elif any(c.get("entity_type") == "ingredient" for c in chunks):
        intro = "I found relevant organic ingredient guidance."
    else:
        intro = "I found relevant skincare products from the product catalog."

    bullets = []
    for c in chunks[:4]:
        label = c.get("product_name") or c.get("ingredient_name") or c.get("source_dataset") or "Result"
        txt = re.sub(r"\s+", " ", c.get("text", "")).strip()
        bullets.append(f"- {label}: {txt[:220]}{'...' if len(txt) > 220 else ''}")

    safety = (
        "This information is educational and not a substitute for personalized medical care, "
        "especially for persistent, severe, or worsening skin conditions."
    )

    return intro + "\n\n" + "\n".join(bullets) + "\n\n" + safety