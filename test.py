#!/usr/bin/env python3
import psycopg2
import subprocess
import time
import sys

def check_container_running():
    """Check if the PostgreSQL container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps"], 
            capture_output=True, 
            text=True
        )
        if "postgres_db" in result.stdout and "Restarting" in result.stdout:
            print("⚠️ PostgreSQL container is restarting")
            return False
        elif "postgres_db" in result.stdout:
            print("✅ PostgreSQL container exists") 
            return True
        else:
            print("❌ PostgreSQL container is not running!")
            return False
    except Exception as e:
        print(f"❌ Error checking container status: {e}")
        return False
def test_pgvector_functionality():
    """Test if pgvector is working properly and init script was executed."""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Successfully connected to PostgreSQL")
        
        # Check if vector extension is installed
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
        if cursor.fetchone():
            print("✅ pgvector extension is installed")
        else:
            print("❌ pgvector extension is NOT installed")
            return False
        
        # Check if initialization script created the items table
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'items'
            )
        """)
        if cursor.fetchone()[0]:
            print("✅ Table 'items' exists (init script worked)")
        else:
            print("❌ Table 'items' does NOT exist (init script failed or wasn't executed)")
            return False
            
        # Check if the HNSW index was created
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'items' AND indexdef LIKE '%hnsw%'
        """)
        if cursor.fetchone():
            print("✅ HNSW index on items table exists")
        else:
            print("❌ HNSW index on items table does NOT exist")
            return False
            
        # Check if the search_items function was created and get its definition
        cursor.execute("""
            SELECT pg_get_functiondef(oid), proargnames, proargtypes::regtype[] 
            FROM pg_proc 
            WHERE proname = 'search_items'
        """)
        function_info = cursor.fetchone()
        if function_info:
            print("✅ search_items function exists")
            print("Function definition:", function_info[0])
            print("Argument names:", function_info[1])
            print("Argument types:", function_info[2])
        else:
            print("❌ search_items function does NOT exist")
            return False
        
        # Insert test data and test vector search
        print("\nInserting test data and testing vector search...")
        # Delete any existing test data
        cursor.execute("DELETE FROM items")
        conn.commit()
        
        # Insert test vectors with proper casting to vector type
        cursor.execute("""
            INSERT INTO items (content, embedding) VALUES 
            ('Test document 1', CAST(ARRAY[0.1, 0.2, 0.3] || ARRAY(SELECT 0.0 FROM generate_series(1, 765)) AS vector(768))),
            ('Test document 2', CAST(ARRAY[0.4, 0.5, 0.6] || ARRAY(SELECT 0.0 FROM generate_series(1, 765)) AS vector(768))),
            ('Test document 3', CAST(ARRAY[0.7, 0.8, 0.9] || ARRAY(SELECT 0.0 FROM generate_series(1, 765)) AS vector(768)))
            RETURNING id
        """)
        conn.commit()
        
        # Create a test query vector
        test_vector = '[' + ','.join(['0.2', '0.2', '0.2'] + ['0.0'] * 765) + ']'
        
        # Test the search_items function with different variations
        success = False
        error_messages = []
        
        # Try different variations of the function call
        queries = [
            f"SELECT * FROM search_items(CAST('{test_vector}' AS vector(768)))",
            f"SELECT * FROM public.search_items(CAST('{test_vector}' AS vector(768)))",
            f"SELECT * FROM search_items(CAST('{test_vector}' AS vector(768)), 2)",
            f"SELECT * FROM public.search_items(CAST('{test_vector}' AS vector(768)), 2)"
        ]
        
        for query in queries:
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                if results and len(results) > 0:
                    success = True
                    print("✅ Vector similarity search function is working")
                    print("\nTop similar documents:")
                    for row in results:
                        print(f"  ID: {row[0]}, Content: {row[1]}, Similarity: {row[2]:.4f}")
                    break
            except Exception as e:
                error_messages.append(f"Query failed: {query}\nError: {str(e)}")
        
        if not success:
            print("❌ All query attempts failed:")
            for msg in error_messages:
                print(msg)
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def main():
    print("Testing PostgreSQL with pgvector initialization...\n")
    
    if not check_container_running():
        print("\nPlease start the container with: docker-compose up -d")
        sys.exit(1)
    
    # Wait a moment to ensure PostgreSQL is fully initialized
    print("\nWaiting for PostgreSQL to be ready...")
    time.sleep(3)
    
    if test_pgvector_functionality():
        print("\n✅ All tests passed! pgvector is working properly with initialization scripts.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 