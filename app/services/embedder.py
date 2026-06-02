import os
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_documents(texts):
    model = get_model()
    emb = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return np.array(emb, dtype='float32')


def embed_query(text):
    model = get_model()
    emb = model.encode([text], normalize_embeddings=True, show_progress_bar=False)
    return np.array(emb, dtype='float32')
