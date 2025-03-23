import json

# Load the 50 selected articles from filtered_test_keywords.json
with open("filtered_test_keywords.json", "r") as file:
    selected_articles = json.load(file)

# Extract the list of IDs from the selected articles
selected_ids = {article["id"] for article in selected_articles}

# Debugging: Print out the selected articles' IDs to confirm correct data loading
print(f"Selected article IDs: {selected_ids}")

# Load the processed_test_bigrams.json file
with open("processed_test_bigrams.json", "r") as file:
    bigrams_data = json.load(file)

# Debugging: Check if processed_test_bigrams.json has any data
print(f"Loaded {len(bigrams_data)} bigrams articles.")

# Create a dictionary for fast lookup of bigram articles by ID
bigrams_dict = {article["id"]: article for article in bigrams_data}

# Debugging: Print out some IDs from the bigrams_dict to check if the data is correct
print(f"First few IDs in bigrams_dict: {list(bigrams_dict.keys())[:5]}")

# Extract the bigrams for the selected articles while maintaining the order from filtered_test_keywords
filtered_bigrams = [bigrams_dict[article["id"]] for article in selected_articles if article["id"] in bigrams_dict]

# Debugging: Check how many bigrams are filtered
print(f"Filtered bigrams count: {len(filtered_bigrams)}")

# Save the filtered bigrams into a new file
with open("filter_test/filtered_test_bigrams.json", "w") as file:
    json.dump(filtered_bigrams, file, indent=4)

print("Filtered bigrams saved to filtered_test_bigrams.json")
