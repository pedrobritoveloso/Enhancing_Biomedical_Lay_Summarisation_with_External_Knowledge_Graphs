import os
import json
import sys
import yake
import requests

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

# Function to extract keywords using YAKE


def extract_keywords(text, num_terms=10, dedupLim=0.5):
    keyword_extractor = yake.KeywordExtractor(
        top=num_terms, n=2, dedupLim=dedupLim)
    keywords = [kw[0] for kw in keyword_extractor.extract_keywords(text)]
    return keywords

# Function to search keywords in DBPedia and return only biomedical links


def search_dbpedia(keyword):
    lookup_url = f"http://lookup.dbpedia.org/api/search?query={keyword}&format=JSON"
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(lookup_url, headers=headers)
        if response.status_code == 200:
            results = response.json().get("docs", [])
            if not results:
                print("No results found in DBPedia.")
                return None, None
            # Extract only the first result
            first_result = results[0]
            main_url = first_result.get("resource", [None])[0]
            if not main_url:
                print("No valid DBpedia resource found.")
                return None, None
            print(f"First result URL: {main_url}")
            # Extract full description from DBPedia resource
            full_description = fetch_dbpedia_description(main_url)
            return main_url, full_description
        print("No relevant DBPedia link found.")
        return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error querying DBPedia for '{keyword}': {e}")
        return None, None


def fetch_dbpedia_description(resource_url):
    # Convert resource URL to API format
    resource_name = resource_url.split("/")[-1]
    dbpedia_api_url = f"http://dbpedia.org/data/{resource_name}.json"
    try:
        response = requests.get(dbpedia_api_url)
        if response.status_code == 200:
            data = response.json()
            # Locate the correct entity data
            entity_data = data.get(
                f"http://dbpedia.org/resource/{resource_name}", {})
            # Extract full English abstract
            abstracts = entity_data.get(
                "http://dbpedia.org/ontology/abstract", [])
            for abstract in abstracts:
                if abstract.get("lang") == "en":  # Select English abstract
                    return abstract.get("value", "No abstract available")
        return "No abstract available"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching description for '{resource_url}': {e}")
        return "No abstract available"


def query_ollama(keyword):
    try:
        response = requests.post(
            OLLAMA_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": "deepseek-r1",  # Ensure the model name is correct
                "prompt": f"Classify if the following term is related to biomedical/biological domain: {keyword}. Answer yes if it's related to biomedical/biological, no if not."
            },
            stream=True  # Use stream mode to handle the chunks of response
        )

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return None

        # Print raw response text for debugging
        print("\n" + "=" * 50)
        full_response = ""
        # Iterate over the chunks in the stream
        for chunk in response.iter_lines():
            if chunk:
                # Decode the chunk to a string and parse it as JSON
                try:
                    json_chunk = json.loads(chunk.decode("utf-8"))
                    # Add the response text to the full response
                    # Concatenate the parts
                    full_response += json_chunk.get("response", "")
                except json.JSONDecodeError:
                    print("Error decoding chunk")

        # Print the full concatenated response
        print("Full Response: ")
        print(full_response)
        print("=" * 50 + "\n")
        return full_response.strip()  # Return the complete response

    except requests.exceptions.RequestException as e:
        print(f"\nError querying Ollama: {e}")
        print("=" * 50 + "\n")
        return None


def is_biomedical_keyword(keyword):
    """
    Uses Ollama to classify whether a given keyword is related to the biomedical/biological domain.
    Returns True if the keyword is related, False otherwise.
    """
    result = query_ollama(
        keyword)  # Assuming query_ollama is the function we created earlier to interact with Ollama
    if result:
        # Assuming Ollama responds with 'yes' or similar for biomedical terms
        return "yes" in result.lower()
    return False

def process_elife_file(file_path, output_folder, start_id, end_id):
    print(f"Processing file: {file_path} (Articles {start_id} to {end_id})")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        print(f"Skipping {file_path}: JSON structure is not a list of articles.")
        return
    total_articles = len(data)
    start_id = max(1, start_id)  # Ensure valid range
    end_id = min(end_id, total_articles)
    contador = 0

    # Open the output files for appending
    base_filename = os.path.basename(file_path).replace('.json', '')
    output_filename = os.path.join(output_folder, f"processed_{base_filename}_bigrams.json")
    output_filename_keywords = os.path.join(output_folder, f"processed_{base_filename}_keywords.json")

    # Open files in append mode
    with open(output_filename, "a", encoding="utf-8") as json_file, \
         open(output_filename_keywords, "a", encoding="utf-8") as json_file_keywords:
        
        for index, article in enumerate(data[start_id - 1:end_id], start=start_id):
            if not isinstance(article, dict) or "sections" not in article:
                continue

            # Extract article text
            content = " ".join(
                " ".join(section) for section in article["sections"] if isinstance(section, list)).strip()
            if not content:
                continue

            print(f"Extracting keywords from an article in {file_path}")
            keywords = extract_keywords(content)
            print(f"Extracted keywords: {keywords}")

            # Store all original extracted keywords (unfiltered)
            processed_keywords_entry = {
                "id": article.get("id", "unknown"),
                "title": article.get("title", "Untitled"),
                "keywords": keywords  # Store the raw (unfiltered) keyword list
            }

            # Append the unfiltered keywords to the keywords file
            if keywords:
                json.dump([processed_keywords_entry], json_file_keywords, ensure_ascii=False, indent=4)
                json_file_keywords.write("\n")  # Ensure each entry is on a new line

            # Filter keywords with Ollama
            relevant_keywords = [kw for kw in keywords if is_biomedical_keyword(kw)]

            print(f"Filtered relevant keywords: {relevant_keywords}")

            # Query DBPedia for each relevant keyword
            dbpedia_results = {}
            contador += 1
            print(f"Contador de artigos ja processsadoss: {contador}")
            for kw in relevant_keywords:
                link, description = search_dbpedia(kw)
                if link:
                    dbpedia_results[kw] = {
                        "link": link,
                        "description": description
                    }
            print("No more DBPedia links related to this article")

            # Structure output JSON for article data
            processed_entry = {
                "id": article.get("id", "unknown"),
                "title": article.get("title", "Untitled"),
                "dbpedia": dbpedia_results  # Store all DBpedia results
            }

            # If there are relevant DBpedia results, append to the processed_bigrams file
            if dbpedia_results:
                json.dump([processed_entry], json_file, ensure_ascii=False, indent=4)
                json_file.write("\n")  # Ensure each entry is on a new line

    print(f"Processed: {file_path} -> Saved to {output_filename}")
    print(f"Processed: {file_path} -> Saved to {output_filename_keywords}")

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


# Run script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python YakePreprocess.py <start_id> <end_id>")
        sys.exit(1)

    start_id = int(sys.argv[1])
    end_id = int(sys.argv[2])

    input_folder = "/home/dock/elife"
    output_folder = "/home/dock/Enhancing_Biomedical_Lay_Summarisation_with_External_Knowledge_Graphs/YakePreProcess"
    os.makedirs(output_folder, exist_ok=True)

    file_to_process = choose_file(input_folder)

    if file_to_process:
        process_elife_file(file_to_process, output_folder, start_id, end_id)
