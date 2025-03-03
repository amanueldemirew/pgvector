-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a table for Gemini embeddings (768 dimensions for text-embedding-gecko)
CREATE TABLE items (
    id bigserial PRIMARY KEY, 
    content TEXT,
    embedding vector(768)
);

-- Create an HNSW index for vector similarity search
-- Cosine similarity is recommended for Gemini embeddings
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

-- Optional: Create a function to search by similarity
CREATE OR REPLACE FUNCTION search_items(query_embedding vector(768), match_count INT)
RETURNS TABLE (
    id bigint,
    content TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        items.id,
        items.content,
        1 - (items.embedding <=> query_embedding) AS similarity
    FROM items
    ORDER BY items.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql; 