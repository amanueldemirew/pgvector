import psycopg2
import logging
import psycopg2

connection_string = "postgresql://postgres:postgres@localhost:5432/postgres"
db_name = "vector_db"

# Connect to default database first
conn = psycopg2.connect(connection_string)
conn.autocommit = True

try:
    with conn.cursor() as c:
        # Drop database if exists and create new one
        c.execute(f"DROP DATABASE IF EXISTS {db_name}")
        c.execute(f"CREATE DATABASE {db_name}")
        
        # Connect to the new database to create extension
        conn.close()
        new_conn = psycopg2.connect(f"postgresql://postgres:postgres@localhost:5432/{db_name}")
        new_conn.autocommit = True
        with new_conn.cursor() as c:
            c.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
    print(f"Database '{db_name}' created successfully with pgvector extension!")

except Exception as e:
    print(f"Error: {e}")

finally:
    conn.close()
    if 'new_conn' in locals():
        new_conn.close() 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    logger.info("Connecting to PostgreSQL database...")
    conn = psycopg2.connect(
        dbname="vector_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Enable the pgvector extension
    logger.info("Enabling pgvector extension...")
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create embeddings table
    logger.info("Creating embeddings table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pg_embeddings (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        embedding vector(768) NOT NULL
    );
    """)
    conn.commit()
    logger.info("Database setup completed successfully!")

except Exception as e:
    logger.error(f"An error occurred: {str(e)}")
    raise
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
    logger.info("Database connection closed.") 