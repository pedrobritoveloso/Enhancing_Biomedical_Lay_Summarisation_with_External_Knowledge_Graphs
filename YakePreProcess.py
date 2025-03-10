import os
import json
import yake
import requests

# Function to extract keywords using YAKE
def extract_keywords(text, num_terms=10, isTrigram=False):
    n = 3 if isTrigram else 2  # Use trigrams or bigrams
    keyword_extractor = yake.KeywordExtractor(top=num_terms, n=n)
    keywords = [kw[0] for kw in keyword_extractor.extract_keywords(text)]
    return keywords

def search_keywords_dbpedia(keyword):
    # Define a set of relevant biomedical types (classes) for filtering
    biomedical_types = [
        "BiologicalProcess",
        "Disease",  # For diseases like cancer, diabetes, etc.
        "Gene",  # For gene-related keywords
        "ChemicalSubstance",  # For drug or chemical substance keywords
        "PharmaceuticalDrug"  # For pharmaceutical drug-related keywords
    ]

    # Construct the URL with query and filter by biomedical types
    url = f"http://lookup.dbpedia.org/api/search?query={keyword}&format=JSON&" + \
          f"type={','.join(biomedical_types)}&maxResults=5"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        
        # Check if response is successful
        if response.status_code == 200:
            results = response.json().get("docs", [])  # Extract results safely
            if results:
                for result in results:
                    # Ensure the 'title' key exists and is not empty
                    title = result.get('title', '')
                    if title:
                        dbpedia_url = f"http://dbpedia.org/resource/{title}"
                        print(f"'{keyword}' was found in DBpedia: {dbpedia_url}")
                    else:
                        print(f"No valid title for keyword '{keyword}' in DBpedia result.")
            else:
                print(f"'{keyword}' was not found in DBpedia")
        else:
            print(f"DBpedia search failed for {keyword}: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request error for {keyword}: {e}")


# Function to process eLife JSON files
def process_elife_file(file_path, output_folder, isTrigram):
    print(f"Processing file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        print(f"Skipping {file_path}: JSON structure is not a list of articles.")
        return

    processed_articles = []

    for article in data:
        if not isinstance(article, dict):
            print(f"Skipping an entry in {file_path}: Not a valid dictionary")
            continue

        if "sections" in article and isinstance(article["sections"], list):
            content = " ".join([" ".join(section) for section in article["sections"] if isinstance(section, list)])
        else:
            print(f"Skipping an entry in {file_path}: Invalid 'sections' structure.")
            continue

        if not content.strip():
            print(f"Skipping an entry in {file_path}: Extracted text is empty")
            continue

        print(f"Extracting keywords from an article in {file_path}")

        keywords = extract_keywords(content, isTrigram=isTrigram)
        print(f"Extracted keywords: {keywords}")

        # Query DBPedia for explanations
        dbpedia_explanations = {kw: search_dbpedia(kw) for kw in keywords}
        
        # Structure output JSON
        processed_entry = {
            "id": article.get("id", "unknown"),
            "title": article.get("title", "Untitled"),
            "eLife": content,
            "DBpedia links": dbpedia_explanations 
        }

        # Add explanations only if found
        for term, explanation in dbpedia_explanations.items():
            if explanation:
                processed_entry[term] = explanation
        
        processed_articles.append(processed_entry)

    if not processed_articles:
        print(f"No valid articles processed in {file_path}, skipping output.")
        return

    base_filename = os.path.basename(file_path).replace('.json', '')
    output_filename = os.path.join(output_folder, f"processed_{base_filename}_{'trigrams' if isTrigram else 'bigrams'}.json")

    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(processed_articles, json_file, ensure_ascii=False, indent=4)

    print(f"Processed: {file_path} -> Saved to {output_filename}")

# Function to list and choose eLife files
def choose_file(input_folder):
    files = [f for f in os.listdir(input_folder) if f.endswith(".json")]

    if not files:
        print("No JSON files found in the input directory.")
        return None

    print("Available files:")
    for idx, filename in enumerate(files, start=1):
        print(f"{idx}. {filename}")

    file_choice = input(f"Choose a file by entering its number (1-{len(files)}): ")

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

# Function to choose between trigrams and bigrams
def choose_keyword_type():
    while True:
        choice = input("Extract trigrams (True) or bigrams (False)? Enter True or False: ")
        if choice.lower() == "true":
            return True
        elif choice.lower() == "false":
            return False
        else:
            print("Invalid input. Enter True or False.")

# Run script
input_folder = "/home/dock/elife"
output_folder = "/home/dock/Enhancing_Biomedical_Lay_Summarisation_with_External_Knowledge_Graphs/YakePreProcess"
os.makedirs(output_folder, exist_ok=True)

file_to_process = choose_file(input_folder)

if file_to_process:
    isTrigram = choose_keyword_type()
    process_elife_file(file_to_process, output_folder, isTrigram)
