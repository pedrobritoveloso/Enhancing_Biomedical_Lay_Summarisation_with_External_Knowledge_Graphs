import json

# Load the 50 selected articles from filtered_val_keywords.json
with open("filtered_val_keywords.json", "r") as file:
    selected_articles = json.load(file)

# Extract the list of IDs from the selected articles
selected_ids = {article["id"] for article in selected_articles}

# Load the processed_val_bigrams.json file
with open("processed_val_bigrams.json", "r") as file:
    bigrams_data = json.load(file)

# Create a dictionary for fast lookup of bigram articles by ID
bigrams_dict = {article["id"]: article for article in bigrams_data}

# Extract the bigrams for the selected articles while maintaining the order from filtered_val_keywords
filtered_bigrams = [bigrams_dict[article["id"]] for article in selected_articles if article["id"] in bigrams_dict]

# Save the filtered bigrams into a new file
with open("filter_val/filtered_val_bigrams.json", "w") as file:
    json.dump(filtered_bigrams, file, indent=4)

print("Filtered bigrams saved to filtered_val_bigrams.json")
