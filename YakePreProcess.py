import os
import json
import yake
import requests

# Function to extract keywords using YAKE
def extract_keywords(text, num_terms=10):
    keyword_extractor = yake.KeywordExtractor(n=2, top=num_terms)  # Bigram (n=2)
    keywords = keyword_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]  # Only return the terms

# Function to search DBPedia for explanations
def search_dbpedia(term):
    url = f"http://lookup.dbpedia.org/api/search/KeywordSearch?QueryString={term}"
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "docs" in data and len(data["docs"]) > 0:
            return data["docs"][0].get("abstract", None)  # Return first result abstract
    return None  # No result found

# Function to process each eLife JSON file
def process_elife_files(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):  # Process only JSON files
            file_path = os.path.join(input_folder, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)  # Load JSON file

            # Assuming article content is stored under "content" key
            if "content" in data:
                content = data["content"]

                # Extract keywords
                keywords = extract_keywords(content)

                # Search DBPedia and create output JSON
                output_data = {"eLife": content}
                for term in keywords:
                    explanation = search_dbpedia(term)
                    if explanation:
                        output_data[term] = explanation

                # Save JSON output
                output_filename = os.path.join(output_folder, f"processed_{filename}")
                with open(output_filename, "w", encoding="utf-8") as json_file:
                    json.dump(output_data, json_file, ensure_ascii=False, indent=4)

                print(f"Processed: {filename}")

# Run script
input_folder = "home/dock/elife"  # Folder containing eLife JSON files
output_folder = "home/dock/YakePreProcess"  # Folder to save processed JSON files

os.makedirs(output_folder, exist_ok=True)
process_elife_files(input_folder, output_folder)
