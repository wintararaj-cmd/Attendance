import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url or "sqlite" in db_url:
    print("❌ DATABASE_URL is not set to PostgreSQL in .env")
    exit(1)

print(f"Checking connection to: {db_url}")

try:
    # Parse URL
    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    # Only connect to 'postgres' database first to check/create the target db
    con = psycopg2.connect(
        dbname='postgres',
        user=username,
        host=hostname,
        password=password,
        port=port
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    
    # Check if database exists
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database}'")
    exists = cur.fetchone()
    
    if not exists:
        print(f"⚠️ Database '{database}' does not exist. Creating it...")
        cur.execute(f"CREATE DATABASE {database}")
        print(f"✅ Database '{database}' created successfully!")
    else:
        print(f"✅ Database '{database}' already exists.")
        
    cur.close()
    con.close()
    
    # Now valid connection to the actual database
    con = psycopg2.connect(
        dbname=database,
        user=username,
        host=hostname,
        password=password,
        port=port
    )
    print("✅ Successfully connected to the target database!")
    con.close()

except Exception as e:
    print(f"❌ Error connecting to PostgreSQL: {e}")
    print("Please check your .env file credentials and ensure PostgreSQL is running.")
