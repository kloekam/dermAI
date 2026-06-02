import os, json
from pathlib import Path
import numpy as np
import faiss
from dotenv import load_dotenv
from app.utils.loader import load_kaggle_products, load_organic_ingredients
from app.utils.pdf_loader import load_pdf_pages
from app.utils.chunker import product_chunks, organic_chunks, pdf_chunks
from app.services.embedder import embed_documents

load_dotenv()
BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'data'
OUT = BASE / 'output'
OUT.mkdir(exist_ok=True)


def run_ingestion():
    print('=' * 60)
    print('dermAI — Full Multi-Source Ingestion')
    print('=' * 60)
    kaggle = load_kaggle_products(DATA / 'kaggle_skincare.csv')
    organic = load_organic_ingredients(DATA / 'organic_skincare_cleaned.csv')
    pdf_pages = load_pdf_pages(DATA / 'NICE_psoriasis_guideline.pdf')
    chunks = product_chunks(kaggle) + organic_chunks(organic) + pdf_chunks(pdf_pages)
    print(f'[ingest] kaggle products: {len(kaggle)}')
    print(f'[ingest] organic ingredients: {len(organic)}')
    print(f'[ingest] pdf pages: {len(pdf_pages)}')
    print(f'[ingest] total chunks: {len(chunks)}')
    texts = [c['text'] for c in chunks]
    embeddings = np.array(embed_documents(texts), dtype='float32')
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, str(OUT / 'index.faiss'))
    with open(OUT / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f'[ingest] saved {OUT / "index.faiss"}')
    print(f'[ingest] saved {OUT / "metadata.json"}')

if __name__ == '__main__':
    run_ingestion()
