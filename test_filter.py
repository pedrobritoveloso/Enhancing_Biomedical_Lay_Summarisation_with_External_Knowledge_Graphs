from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "microsoft/Phi-4-mini-instruct"

# Force re-download
tokenizer = AutoTokenizer.from_pretrained(model_name, force_download=True)
model = AutoModelForCausalLM.from_pretrained(model_name, force_download=True)

def is_biomedical(description):
    """Checks if the given description is related to biomedical/biological topics."""
    prompt = f"""You are a helpful assistant. Consider the following abstract:\n\n{description}\n\nDo you think it is a biological or biomedical related concept? Answer only yes or no."""
    
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model.generate(**inputs, max_length=50)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return "yes" in response.lower()

# Example Usage
dbpedia_descriptions = {
    "RNA-binding proteins": "RNA-binding proteins (often abbreviated as RBPs) are proteins that bind to the double or single-stranded RNA...",
    "Play key": "The piano is a stringed keyboard instrument...",
}

filtered_keywords = {k: v for k, v in dbpedia_descriptions.items() if is_biomedical(v)}

print(filtered_keywords)  # Should remove "Play key" but keep "RNA-binding proteins"
