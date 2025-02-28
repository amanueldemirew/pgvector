from llama_index.embeddings.gemini import GeminiEmbedding
from dotenv import load_dotenv



embed_model = GeminiEmbedding(model_name="models/embedding-001")
embedding = embed_model.get_text_embedding("Test input")

print(embedding)
