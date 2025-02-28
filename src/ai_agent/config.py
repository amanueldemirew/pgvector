import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# Load environment variables from .env file
load_dotenv()

# Check if API key is loaded
if not os.getenv("GOOGLE_API_KEY"):
    raise EnvironmentError(
        "GOOGLE_API_KEY environment variable is not set. Please check your .env file."
    )

# Database Settings
DB_URL = "postgresql://task_tracker_owner:npg_0wVhjBfipD5x@ep-small-hat-a826rta1-pooler.eastus2.azure.neon.tech/task_tracker?sslmode=require"
VECTOR_DB_URL = "postgresql://postgres:postgres@localhost:5432/vector_db"

# API Settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
model_name = "models/embedding-001"
embed_model = GeminiEmbedding(model_name=model_name)
# LLM Settings
Settings.llm = Gemini(model_name="models/gemini-1.5-flash-001", api_key=GOOGLE_API_KEY)
Settings.embed_model = embed_model
# Vector Store Settings
VECTOR_STORE_SETTINGS = {
    "table_name": "pgs_embeddings",
    "embed_dim": 768,
    "hnsw_kwargs": {
        "hnsw_m": 16,
        "hnsw_ef_construction": 64,
        "hnsw_ef_search": 40,
        "hnsw_dist_method": "vector_cosine_ops",
    },
}
