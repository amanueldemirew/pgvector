from llama_index.readers.database import DatabaseReader
from .config import DB_URL


def fetch_and_preview_data(query: str, limit_preview: int = 2):
    """
    Fetches data from the database and converts it to Document objects.

    Args:
        query (str): SQL query to execute.
        limit_preview (int): Number of documents to preview before indexing.

    Returns:
        list[Document]: List of Document objects.
    """
    
    db = DatabaseReader(uri=DB_URL)
    texts = db.sql_database.run_sql(command=query)
    return texts
