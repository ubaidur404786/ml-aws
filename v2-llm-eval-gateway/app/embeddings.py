"""Turn text into a vector of numbers. Bedrock Titan in real mode, a free fake in mock mode."""
import hashlib
import json

import numpy as np

from app import config


# Example: mock_embed("refunds within 30 days") -> array of 512 floats (same text always gives same vector)
def mock_embed(text: str) -> np.ndarray:
    vector = np.zeros(config.EMBED_DIM, dtype="float32")
    for word in text.lower().split():
        word = word.strip(".,?!:;()$")
        bucket = int(hashlib.md5(word.encode()).hexdigest(), 16) % config.EMBED_DIM
        vector[bucket] += 1.0  # each word adds 1 to "its" position
    return vector


# Example: titan_embed("refunds within 30 days") -> array of 512 floats from Bedrock
def titan_embed(text: str) -> np.ndarray:
    import boto3  # imported here so mock mode works without AWS setup

    client = boto3.client("bedrock-runtime", region_name=config.AWS_REGION)
    body = json.dumps({"inputText": text, "dimensions": config.EMBED_DIM, "normalize": True})
    response = client.invoke_model(modelId=config.EMBED_MODEL, body=body)
    return np.array(json.loads(response["body"].read())["embedding"], dtype="float32")


# Example: embed("What is the refund window?") -> unit-length array of 512 floats
def embed(text: str) -> np.ndarray:
    vector = mock_embed(text) if config.LLM_MODE == "mock" else titan_embed(text)
    length = np.linalg.norm(vector)
    return vector / length if length > 0 else vector  # unit length, so dot product = cosine similarity
