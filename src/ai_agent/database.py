from llama_index.readers.database import DatabaseReader
from sqlalchemy import create_engine
from sqlalchemy.sql import text


def fetch_and_preview_data(query: str, limit_preview: int = 2):
    """
    Fetches data from the database and converts it to Document objects.

    Args:
        query (str): SQL query to execute.
        limit_preview (int): Number of documents to preview before indexing.

    Returns:
        list[Document]: List of Document objects.
    """

    # Create engine first with proper SSL mode
    engine = create_engine(
        "postgresql://task_tracker_owner:npg_0wVhjBfipD5x@ep-small-hat-a826rta1-pooler.eastus2.azure.neon.tech/task_tracker",
        connect_args={"sslmode": "require"},
    )
    # Initialize DatabaseReader directly with engine
    db = DatabaseReader(engine=engine)

    # Execute query with result checking
    try:
        documents = db.load_data(query=query)
        return documents
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise


