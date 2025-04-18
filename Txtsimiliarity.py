import json
from sentence_transformers import SentenceTransformer
import torch

# Step 1: Load files
file_paths = [
    "YakePreProcess/File_pre_processed/processed_val_bigrams.json",
    "YakePreProcess/File_pre_processed/processed_test_bigrams.json"
]

descriptions = []
concept_ids = []

for file_path in file_paths:
    with open(file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    for article in articles:
        for concept, info in article["dbpedia"].items():
            desc = info.get("description", "")
            if desc and "No abstract available" not in desc:
                descriptions.append(desc)
                concept_ids.append(f'{article["id"]}:{concept}')

print(f"Loaded {len(descriptions)} descriptions.")

# Step 2: Load model & encode
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(descriptions, convert_to_tensor=True)

print(f"Generated embeddings shape: {embeddings.shape}")  # Should be (N, 384)

# Step 3: Quick sanity check
print("\nExample:")
print("Description:", descriptions[0][:200] + "...")
print("Embedding (first 5 dims):", embeddings[0][:5])
