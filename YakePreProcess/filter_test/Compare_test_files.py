import json

# Load filtered_test_keywords
with open('YakePreProcess/filter_test/filtered_test_keywords.json', 'r') as f:
    filtered_keywords = json.load(f)

# Load filtered_test_bigrams
with open('YakePreProcess/File_pre_processed/processed_test_bigrams.json', 'r') as f:
    filtered_bigrams = json.load(f)

# Compare the two datasets
for keyword_entry in filtered_keywords:
    article_id = keyword_entry['id']
    keywords = set(keyword_entry['keywords'])

    # Find the corresponding entry in filtered_test_bigrams
    bigram_entry = next((entry for entry in filtered_bigrams if entry['id'] == article_id), None)
    if bigram_entry:
        bigrams = set(bigram_entry['keywords'])
        missing_keywords = keywords - bigrams

        print(f"Article ID: {article_id}")
        print(f"Missing Keywords: {missing_keywords}")
        print(f"Number of Missing Keywords: {len(missing_keywords)}\n")
    else:
        print(f"Article ID: {article_id} not found in filtered_test_bigrams.\n")