# dermAI

A complete multi-source skincare RAG app with:
- Kaggle skincare product dataset
- Organic skincare ingredient dataset
- NICE psoriasis guideline PDF
- Flask homepage + popup chatbot
- Local SentenceTransformer embeddings + FAISS retrieval

## Setup

1. Create and activate a virtual environment.
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy env file:
   ```bash
   copy .env.example .env
   ```
   or on macOS/Linux:
   ```bash
   cp .env.example .env
   ```
4. Build the index:
   ```bash
   python -m scripts.ingest
   ```
5. Run the app:
   ```bash
   python run.py
   ```
6. Open http://127.0.0.1:5000

## Notes
- Embeddings are local by default for reliability.
- The answer layer is extractive and grounded in retrieved chunks.
- The popup chatbot works best after ingestion creates `output/index.faiss` and `output/metadata.json`.
