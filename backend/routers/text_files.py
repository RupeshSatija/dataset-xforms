import random
import string

import nltk
from fastapi import APIRouter, File, HTTPException, UploadFile
from transformers import AutoTokenizer

# Download required NLTK data
nltk.download("wordnet")
nltk.download("omw-1.4")  # Open Multilingual WordNet

router = APIRouter()
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode()
    # Use the BERT tokenizer instead of NLTK
    tokens = tokenizer.tokenize(text)
    return {"content": text, "tokens": tokens}


@router.post("/transform")
async def transform_text(request: dict):
    text = request.get("text", "")
    transformation = request.get("transformation", "")

    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    # Split text into words
    words = text.split()

    if transformation == "synonyms":
        result = simple_synonyms(words)
        return {
            "tokens": result["tokens"],
            "modifications": result["modifications"],
            "type": "synonym",
            "colors": {
                "synonym": "#98FB98"  # Light green for synonyms
            },
        }
    else:
        # For other transformations, process in chunks
        chunk_size = 500  # Slightly less than max to be safe
        tokens = []
        modifications = []

        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size]
            chunk_tokens = tokenizer.tokenize(chunk)

            if transformation == "add_spaces":
                chunk_result = add_spaces(chunk_tokens)
            elif transformation == "add_punctuation":
                chunk_result = add_punctuation(chunk_tokens)
            elif transformation == "noise":
                chunk_result = add_noise(chunk_tokens)

            tokens.extend(chunk_result["tokens"])
            modifications.extend(chunk_result["modifications"])

        return {
            "tokens": tokens,
            "modifications": modifications,
            "type": transformation,
            "colors": {
                "spaces": "#87CEEB",  # Light blue
                "punctuation": "#FFB6C1",  # Light pink
                "noise": "#DDA0DD",  # Light purple
            },
        }


def add_spaces(tokens):
    """Add random spaces between tokens"""
    result = []
    modifications = []
    for token in tokens:
        result.append(token)
        modifications.append(False)
        if random.random() < 0.3:  # 30% chance to add extra space
            result.append(" ")
            modifications.append(True)
    return {"tokens": result, "modifications": modifications}


def add_punctuation(tokens):
    """Add random punctuation marks"""
    punctuation = ",.!?;"
    result = []
    modifications = []
    for token in tokens:
        result.append(token)
        modifications.append(False)
        if random.random() < 0.2:  # 20% chance to add punctuation
            result.append(random.choice(punctuation))
            modifications.append(True)
    return {"tokens": result, "modifications": modifications}


def simple_synonyms(words):
    """Simple synonym replacement using a dictionary"""
    synonyms = {
        # Documentation terms
        "documentation": ["guide", "manual", "reference", "handbook"],
        "tool": ["program", "utility", "software", "application"],
        "instructions": ["procedures", "directions", "guidelines", "steps"],
        # Technical terms
        "encryption": ["ciphering", "encoding", "scrambling", "protection"],
        "decryption": ["decoding", "deciphering", "unscrambling", "recovery"],
        "options": ["parameters", "settings", "configurations", "preferences"],
        "server": ["system", "host", "platform", "machine"],
        # File terms
        "file": ["resource", "document", "data", "content"],
        "content": ["information", "material", "data", "substance"],
    }

    result = []
    modifications = []

    for word in words:
        # Clean word for matching
        clean_word = "".join(c.lower() for c in word if c.isalnum())

        if clean_word in synonyms and random.random() < 0.5:  # 50% chance
            new_word = random.choice(synonyms[clean_word])
            # Preserve original formatting
            result.append(word.replace(clean_word, new_word))
            modifications.append(True)
        else:
            result.append(word)
            modifications.append(False)

    return {"tokens": result, "modifications": modifications}


def add_noise(tokens):
    """Add random character noise to tokens"""
    result = []
    modifications = []
    for token in tokens:
        if random.random() < 0.2:  # 20% chance to add noise
            pos = random.randint(0, len(token))
            noise_char = random.choice(string.ascii_letters)
            token = token[:pos] + noise_char + token[pos:]
            modifications.append(True)
        result.append(token)
        modifications.append(False)
    return {"tokens": result, "modifications": modifications}
