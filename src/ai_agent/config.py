import os
import psycopg2
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from .database import fetch_and_preview_data 
from llama_index.core import StorageContext
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url
import os

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
# Load environment variables from .env file
load_dotenv()

# Check if API key is loaded
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY environment variable is not set. Please check your .env file."
    )

# Database Settings
DB_URL = "postgresql://task_tracker_owner:npg_0wVhjBfipD5x@ep-small-hat-a826rta1-pooler.eastus2.azure.neon.tech/task_tracker?sslmode=require"
VECTOR_DB_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
DB_NAME = "postgres"

# Vector Store Settings
TABLE_NAME = "items"
EMBED_DIM = 768
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 32

# Configure global settings
Settings.chunk_size = CHUNK_SIZE
Settings.chunk_overlap = CHUNK_OVERLAP
Settings.llm = Gemini(model_name="models/gemini-1.5-flash", api_key=GOOGLE_API_KEY)
Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")

def init_database():
    """Initialize the database and required tables."""
    url = make_url(VECTOR_DB_URL)
    conn = psycopg2.connect(
        host=url.host,
        port=url.port,
        user=url.username,
        password=url.password,
        database=DB_NAME
    )
    conn.autocommit = True
    
    with conn.cursor() as cursor:
        # Create the vector extension if it doesn't exist
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Create the items table if it doesn't exist
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id bigserial PRIMARY KEY,
            content TEXT,
            embedding vector({EMBED_DIM})
        )
        """)
    return conn

def verify_embeddings(conn):
    """Verify that embeddings are being saved correctly."""
    with conn.cursor() as cursor:
        # Check total number of rows
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        total_rows = cursor.fetchone()[0]
        
        # Check rows with non-null embeddings
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE embedding IS NOT NULL")
        rows_with_embeddings = cursor.fetchone()[0]
        
        # Get a sample embedding to verify dimension
        cursor.execute(f"SELECT embedding FROM {TABLE_NAME} WHERE embedding IS NOT NULL LIMIT 1")
        sample = cursor.fetchone()
        
        print("\nEmbedding Verification Results:")
        print(f"Total rows in database: {total_rows}")
        print(f"Rows with embeddings: {rows_with_embeddings}")
        if sample:
            embedding_dim = len(sample[0])
            print(f"Embedding dimension verified: {embedding_dim} (Expected: {EMBED_DIM})")
        else:
            print("No embeddings found in the database")
        
        return rows_with_embeddings > 0

# Initialize database
conn = init_database()

try:
    # Example query - modify based on your needs
    query = "SELECT * FROM tasks_ksi LIMIT 2"
    documents = fetch_and_preview_data(query)
    print(f"\nSuccessfully loaded {len(documents)} documents")

    # Initialize vector store
    url = make_url(VECTOR_DB_URL)
    vector_store = PGVectorStore.from_params(
        database=DB_NAME,
        host=url.host,
        password=url.password,
        port=str(url.port),
        user=url.username,
        table_name=TABLE_NAME,
        embed_dim=EMBED_DIM
    )

    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Create the index
    print("\nGenerating and storing embeddings...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )
    
    # Verify embeddings were saved correctly
    if verify_embeddings(conn):
        print("\nSuccess: Embeddings were generated and saved correctly!")
    else:
        print("\nWarning: No embeddings were found in the database!")

finally:
    # Ensure database connection is closed
    conn.close()