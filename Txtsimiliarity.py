import json
from sentence_transformers import SentenceTransformer
import torch

# Step 1: Prompt user for model selection
print("Select the model to encode the descriptions:")
print("1. all-MiniLM-L6-v2 (default, lightweight and fast)")
print("2. paraphrase-MiniLM-L6-v2 (optimized for paraphrase detection)")
print("3. all-mpnet-base-v2 (more accurate but slower)")
print("4. paraphrase-mpnet-base-v2 (optimized for paraphrase detection)")
print("5. distiluse-base-multilingual-cased-v2 (multilingual support)")
model_choice = input("Enter the number corresponding to your choice: ")

# Map user input to model names
model_map = {
    "1": "all-MiniLM-L6-v2",
    "2": "paraphrase-MiniLM-L6-v2",
    "3": "all-mpnet-base-v2",
    "4": "paraphrase-mpnet-base-v2",
    "5": "distiluse-base-multilingual-cased-v2"
}

# Get the selected model or default to 'all-MiniLM-L6-v2'
model_name = model_map.get(model_choice, "all-MiniLM-L6-v2")
print(f"Using model: {model_name}")

# Step 2: Load files
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

# Step 3: Load the selected model and encode descriptions
model = SentenceTransformer(model_name)
embeddings = model.encode(descriptions, convert_to_tensor=True)

print(f"Generated embeddings shape: {embeddings.shape}")  # Should be (N, 384)

# Step 4: Quick sanity check
print("\nExample:")
print("Description:", descriptions[0][:200] + "...")
print("Embedding (first 5 dims):", embeddings[0][:5])
