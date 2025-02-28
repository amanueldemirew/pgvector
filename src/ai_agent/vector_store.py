from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.storage.storage_context import StorageContext
from sqlalchemy import make_url
from .config import VECTOR_DB_URL, VECTOR_STORE_SETTINGS


def create_vector_store():
    """
    Creates and configures the PostgreSQL vector store.

    Returns:
        tuple: (vector_store, storage_context)
    """
    url = make_url(VECTOR_DB_URL)

    vector_store = PGVectorStore.from_params(
        database="vector_db",
        host=url.host,
        password=url.password,
        port=str(url.port),
        user=url.username,
        **VECTOR_STORE_SETTINGS,
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return vector_store, storage_context


