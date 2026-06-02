import os, json
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health():
    faiss_path = os.getenv('FAISS_INDEX_PATH', 'output/index.faiss')
    metadata_path = os.getenv('METADATA_PATH', 'output/metadata.json')
    payload = {
        'status': 'UP',
        'faiss_index': 'loaded' if os.path.exists(faiss_path) else 'missing',
        'metadata': 'loaded' if os.path.exists(metadata_path) else 'missing',
        'vector_count': 0,
    }
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            payload['vector_count'] = len(json.load(f))
    return jsonify(payload)
