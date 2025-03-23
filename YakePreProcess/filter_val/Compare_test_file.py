import json

# Load filtered_val_keywords
with open('YakePreProcess/filter_val/filtered_val_keywords.json', 'r') as f:
    filtered_val_keywords = json.load(f)

# Load filtered_val_bigrams
with open('YakePreProcess/File_pre_processed/processed_val_bigrams.json', 'r') as f:
    filtered_val_bigrams = json.load(f)

# Compare the two datasets
for keyword_entry in filtered_val_keywords:
    article_id = keyword_entry['id']
    keywords = set(keyword_entry['keywords'])

    # Find the corresponding entry in filtered_val_bigrams
    bigram_entry = next((entry for entry in filtered_val_bigrams if entry['id'] == article_id), None)
    if bigram_entry:
        bigrams = set(bigram_entry['keywords'])
        missing_keywords = keywords - bigrams

        print(f"Article ID: {article_id}")
        print(f"Missing Keywords: {missing_keywords}")
        print(f"Number of Missing Keywords: {len(missing_keywords)}\n")
    else:
        print(f"Article ID: {article_id} not found in filtered_val_bigrams.\n")