import os
import json
import yake
import requests

# Function to extract keywords using YAKE
def extract_keywords(text, num_terms=10, isTrigram=False):
    n = 3 if isTrigram else 2  # Set n=3 for trigrams, otherwise n=2 for bigrams
    keyword_extractor = yake.KeywordExtractor(top=num_terms, n=n)  
    keywords = keyword_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]  # Only return the terms

# Function to search keywords in DBpedia
def search_keywords_dbpedia(keyword):
    url = f"http://lookup.dbpedia.org/api/search?query={keyword}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json().get("docs",[])
        return results
    else:
        print(f"DBpedia search failed {keyword}: {response.status_code}")
        return None


# Function to process the selected eLife JSON file
def process_elife_file(file_path, output_folder, isTrigram):
    print(f"Processing file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Ensure data is a list
    if not isinstance(data, list):
        print(f"Skipping {file_path}: JSON structure is not a list of articles.")
        return

    processed_articles = []

    for article in data:
        if not isinstance(article, dict):
            print(f"Skipping an entry in {file_path}: Not a valid dictionary")
            continue

        # Extract relevant text from "sections"
        if "sections" in article and isinstance(article["sections"], list):
            if all(isinstance(section, list) for section in article["sections"]):
                content = " ".join([" ".join(section)
                                   for section in article["sections"] if section])
            else:
                print(f"Skipping an entry in {file_path}: 'sections' is not a list of lists.")
                continue
        else:
            print(f"Skipping an entry in {file_path}: No valid 'sections' key found")
            continue

        if not content.strip():
            print(f"Skipping an entry in {file_path}: Extracted text is empty")
            continue

        print(f"Extracting keywords from an article in {file_path}")

        # Extract keywords
        keywords = extract_keywords(content, isTrigram=isTrigram)
        print(f"Extracted keywords: {keywords}")

        dbpedia_results = {kw: search_keywords_dbpedia(kw) for kw in keywords}  # Search DBpedia
        print(f"DBpedia results: {dbpedia_results}")

        # Create processed article JSON
        processed_articles.append({
            "id": article.get("id", "unknown"),
            "title": article.get("title", "Untitled"),
            "keywords": keywords,
            "dbpedia_links": dbpedia_results
        })

    if not processed_articles:
        print(f"No valid articles processed in {file_path}, skipping output.")
        return

	 # Save JSON output (separate file for trigrams or bigrams)
    base_filename = os.path.basename(file_path).replace('.json', '')  # Remove '.json' part from file name
    output_filename = os.path.join(
        output_folder, f"processed_{base_filename}_{'trigrams' if isTrigram else 'bigrams'}.json")
    
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(processed_articles, json_file, ensure_ascii=False, indent=4)

    print(f"Processed: {file_path} -> Saved to {output_filename}")

# Function to list files and let the user choose which one to process
def choose_file(input_folder):
    files = [f for f in os.listdir(input_folder) if f.endswith(".json")]

    if not files:
        print("No JSON files found in the input directory.")
        return None

    print("Available files:")
    for idx, filename in enumerate(files, start=1):
        print(f"{idx}. {filename}")

    file_choice = input(
        f"Please choose a file by entering its number (1-{len(files)}): ")
    
    try:
        file_choice = int(file_choice)
        if 1 <= file_choice <= len(files):
            return os.path.join(input_folder, files[file_choice - 1])
        else:
            print("Invalid choice, please select a valid file number.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

# Function to ask if the user wants trigrams or bigrams
def choose_keyword_type():
    while True:
        choice = input("Do you want to extract trigrams (True) or bigrams (False)? Please enter True or False: ")
        if choice.lower() == "true":
            return True  
        elif choice.lower() == "false":
            return False  
        else:
            print("Invalid input. Please enter True or False.")

# Run script
input_folder = "/home/dock/elife"
output_folder = "/home/dock/Enhancing_Biomedical_Lay_Summarisation_with_External_Knowledge_Graphs/YakePreProcess"

os.makedirs(output_folder, exist_ok=True)

# Let the user choose which file to process
file_to_process = choose_file(input_folder)

if file_to_process:
    # Ask if the user wants trigrams or bigrams
    isTrigram = choose_keyword_type()

    # Process the file with the selected keyword type (trigram or bigram)
    process_elife_file(file_to_process, output_folder, isTrigram)
