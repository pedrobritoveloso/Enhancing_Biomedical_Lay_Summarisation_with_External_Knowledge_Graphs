import requests
import json

# Define the Ollama API URL
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

# Function to send a request to Ollama
def query_ollama(prompt, model="deepseek-r1"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  # Set to True if you want streaming responses
    }
    
    response = requests.post(OLLAMA_API_URL, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result.get("response", "No response")
    else:
        return f"Error: {response.status_code}, {response.text}"

# Example usage
if __name__ == "__main__":
    prompt = "You are a helpful assistant. Consider the following Politician abstract about. A politician is a person active in party politics, or a person holding or seeking an elected office in government. Politicians propose, support, reject and create laws that govern the land and by extension its people. Broadly speaking, a politician can be anyone who seeks to achieve political power in a government. Do you think it is a biological or biomedical related concept? Answer only yes or no."
    result = query_ollama(prompt)
    print("Ollama Response:", result)
