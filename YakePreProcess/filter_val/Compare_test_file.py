import json

# Load filtered_val_keywords
with open('filtered_val_keywords.json', 'r') as f:
    filtered_val_keywords = json.load(f)

# Load filtered_val_bigrams
with open('filtered_val_bigrams.json', 'r') as f:
    filtered_val_bigrams = json.load(f)

# Open the output file for writing
with open('keywords_missing_from_each_article.txt', 'w') as output_file:
    # Compare the two datasets
    for keyword_entry in filtered_val_keywords:
        article_id = keyword_entry['id']
        keywords = set(keyword_entry['keywords'])

        # Find the corresponding entry in filtered_val_bigrams
        bigram_entry = next((entry for entry in filtered_val_bigrams if entry['id'] == article_id), None)
        if bigram_entry:
            # Extract keywords from the dbpedia field
            bigrams = set(bigram_entry['dbpedia'].keys())
            missing_keywords = keywords - bigrams

            # Write the results to the file
            output_file.write(f"Article ID: {article_id}\n")
            output_file.write(f"Missing Keywords: {missing_keywords}\n")
            output_file.write(f"Number of Missing Keywords: {len(missing_keywords)}\n\n")

            # Print the results to the console
            print(f"Article ID: {article_id}")
            print(f"Missing Keywords: {missing_keywords}")
            print(f"Number of Missing Keywords: {len(missing_keywords)}\n")
        else:
            # Write the results to the file
            output_file.write(f"Article ID: {article_id} not found in filtered_val_bigrams.\n\n")

            # Print the results to the console
            print(f"Article ID: {article_id} not found in filtered_val_bigrams.\n")
