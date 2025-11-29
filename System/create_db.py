import psycopg
import sys

# Connection parameters
conn_params = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "abdoreda12",
    "dbname": "postgres"  # Connect to default database to create new one
}

try:
    # Connect to PostgreSQL default database
    with psycopg.connect(**conn_params, autocommit=True) as conn:
        with conn.cursor() as cur:
            # Check if database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'khalifa_db'")
            exists = cur.fetchone()
            
            if exists:
                print("Database 'khalifa_db' already exists.")
            else:
                # Create database with UTF-8 encoding
                cur.execute("CREATE DATABASE khalifa_db WITH ENCODING 'UTF8' TEMPLATE=template0")
                print("Database 'khalifa_db' created successfully!")
                
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
