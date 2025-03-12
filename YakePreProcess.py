
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

# Function to search keywords in DBPedia and return only biomedical links
def search_dbpedia(keyword):
    """
    Search DBPedia for a given keyword and return its DBpedia link along with the full description.
    """
    lookup_url = f"http://lookup.dbpedia.org/api/search?query={keyword}&format=JSON"
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(lookup_url, headers=headers)

        if response.status_code == 200:
            results = response.json().get("docs", [])

            if not results:
                print("No results found in DBPedia.")
                return None

            # Extract only the first result
            first_result = results[0]  
            main_url = first_result.get("resource", [None])[0]  

            if not main_url:
                print("No valid DBpedia resource found.")
                return None

            print(f"First result URL: {main_url}")

            # Extract full description from DBPedia resource
            full_description = fetch_dbpedia_description(main_url)

            print(f"Full Description: {full_description}")
            return main_url

        print("No relevant DBPedia link found.")
        return None  

    except requests.exceptions.RequestException as e:
        print(f"Error querying DBPedia for '{keyword}': {e}")
        return None


def fetch_dbpedia_description(resource_url):
    """
    Fetch the full English description from DBPedia's data endpoint.
    """
    # Convert resource URL to API format
    resource_name = resource_url.split("/")[-1]  
    dbpedia_api_url = f"http://dbpedia.org/data/{resource_name}.json"

    try:
        response = requests.get(dbpedia_api_url)
        if response.status_code == 200:
            data = response.json()
            # Locate the correct entity data
            entity_data = data.get(f"http://dbpedia.org/resource/{resource_name}", {})
            # Extract full English abstract
            abstracts = entity_data.get("http://dbpedia.org/ontology/abstract", [])
            for abstract in abstracts:
                if abstract.get("lang") == "en":  # Select English abstract
                    return abstract.get("value", "No abstract available")
        return "No abstract available"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching description for '{resource_url}': {e}")
        return "No abstract available"

def process_elife_file(file_path, output_folder, isTrigram):
    print(f"Processing file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        print(
            f"Skipping {file_path}: JSON structure is not a list of articles.")
        return

    processed_articles = []

    for article in data:
        if not isinstance(article, dict):
            print(f"Skipping an entry in {file_path}: Not a valid dictionary")
            continue

        if "sections" in article and isinstance(article["sections"], list):
            content = " ".join(
                [" ".join(section) for section in article["sections"] if isinstance(section, list)])
        else:
            print(
                f"Skipping an entry in {file_path}: Invalid 'sections' structure.")
            continue

        if not content.strip():
            print(f"Skipping an entry in {file_path}: Extracted text is empty")
            continue

        print(f"Extracting keywords from an article in {file_path}")

        keywords = extract_keywords(content, isTrigram=isTrigram)
        print(f"Extracted keywords: {keywords}")

        # Query DBPedia for biomedical links only
        dbpedia_links = {kw: search_dbpedia(kw) for kw in keywords}
        print(f"No more dbpedia links related to this article")

        # Structure output JSON
        processed_entry = {
            "id": article.get("id", "unknown"),
            "title": article.get("title", "Untitled"),
            "eLife": content
        }

        # Add only valid DBpedia links
        for term, link in dbpedia_links.items():
            if link:
                processed_entry[term] = link

        if len(processed_entry) > 3:  # Ensure at least one DBpedia link is added
            processed_articles.append(processed_entry)

    if not processed_articles:
        print(f"No valid articles processed in {file_path}, skipping output.")
        return

    base_filename = os.path.basename(file_path).replace('.json', '')
    output_filename = os.path.join(
        output_folder,
        f"processed_{base_filename}_{'trigrams' if isTrigram else 'bigrams'}.json")

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

    file_choice = input(
        f"Choose a file by entering its number (1-{len(files)}): ")

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
        choice = input(
            "Extract trigrams (True) or bigrams (False)? Enter True or False: ")
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
