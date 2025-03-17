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
    prompt = "Is Lisbon the capital of Portugal? Answer only with yes or no"
    result = query_ollama(prompt)
    print("Ollama Response:", result)
