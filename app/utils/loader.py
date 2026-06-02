from pathlib import Path
import re
import pandas as pd


def _clean_text(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def _normalize_header(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(header).strip().lower())


def _row_get(row, aliases, default=""):
    normalized = {_normalize_header(k): v for k, v in row.items()}
    for alias in aliases:
        key = _normalize_header(alias)
        if key in normalized:
            return _clean_text(normalized[key])
    return default


def load_kaggle_products(path: str | Path):
    df = pd.read_csv(path)
    rows = []

    for _, row in df.fillna("").iterrows():
        row_dict = row.to_dict()

        product_name = _row_get(row_dict, ["product_name", "productname", "name"])
        category = _row_get(row_dict, ["product_type", "producttype", "category"])
        ingredients = _row_get(row_dict, ["clean_ingreds", "ingredients", "ingredient_list", "ingredientlist"])
        price = _row_get(row_dict, ["price", "cost"])
        url = _row_get(row_dict, ["product_url", "url", "producturl"])
        brand = _row_get(row_dict, ["brand", "brand_name", "brandname"])
        raw_skin_type = _row_get(row_dict, ["skin_type", "skintype", "skin_type_suitable", "suitable_for"])
        raw_concerns = _row_get(row_dict, ["concerns", "concern", "skin_concerns", "problem"])

        rows.append({
            "source_dataset": "kaggle_products",
            "entity_type": "product",
            "product_name": product_name,
            "category": category,
            "ingredients": ingredients,
            "price": price,
            "url": url,
            "brand": brand,
            "skin_type": raw_skin_type,
            "concerns": raw_concerns,
            "is_natural": "mixed",
        })

    return rows


def load_organic_ingredients(path: str | Path):
    df = pd.read_csv(path)
    rows = []

    for _, row in df.fillna("").iterrows():
        row_dict = row.to_dict()

        ingredient_name = _row_get(row_dict, ["Ingredients", "ingredient_name", "ingredient"])
        category = _row_get(row_dict, ["Category", "category"])
        problem = _row_get(row_dict, ["Problem", "problem", "concerns"])
        skin_type = _row_get(row_dict, ["Skin_or_Hair_Type", "skin_type", "skintype"])
        symptoms = _row_get(row_dict, ["Symptoms", "symptoms"])
        benefits = _row_get(row_dict, ["Benefits", "benefits"])
        usage = _row_get(row_dict, ["How_to_Use", "usage", "how_to_use"])
        notes = _row_get(row_dict, ["Notes", "notes"])

        rows.append({
            "source_dataset": "organic_ingredients",
            "entity_type": "ingredient",
            "ingredient_name": ingredient_name,
            "category": category,
            "problem": problem,
            "skin_type": skin_type,
            "symptoms": symptoms,
            "benefits": benefits,
            "usage": usage,
            "notes": notes,
            "concerns": problem,
            "is_natural": "yes",
        })

    return rows