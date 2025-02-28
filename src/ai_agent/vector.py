import asyncio
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import load_index_from_storage
from llama_index.core import Document
import os

from .database import fetch_and_preview_data
from .queries import TASK_HIERARCHY_QUERY
from .vector_store import create_vector_store


def main():
    # Create vector store and storage context
    vector_store, storage_context = create_vector_store()

    # Try to load existing index from storage
    try:
        if os.path.exists("./storage"):
            print("Loading existing index...")
            index = load_index_from_storage(storage_context)
            if index and len(index.docstore.docs) > 0:
                print(f"Loaded index with {len(index.docstore.docs)} documents.")
                return index
            else:
                print("No valid index found, creating a new one.")
    except Exception as e:
        print(f"Error loading index: {e}")
        print("Creating new index...")

    # Fetch documents
    documents = fetch_and_preview_data(TASK_HIERARCHY_QUERY)
    print(documents[0])
    # Make sure documents are properly formatted as Document objects


    # Create embedding model and index
    index = VectorStoreIndex(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    # Persist index to disk
    index.storage_context.persist()
    print("Index saved to disk")

    return index


if __name__ == "__main__":
    index = main()
    # Do something with the index to demonstrate it works
    print(f"Index contains {len(index.docstore.docs)} documents")
