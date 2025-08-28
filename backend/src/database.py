import asyncpg
import os
from pathlib import Path
from .config import settings


async def connect_to_db() -> asyncpg.connection.Connection:
    """
    Establish a connection to the PostgreSQL database.
    
    Returns:
        asyncpg.connection.Connection: Database connection
    """
    conn = await asyncpg.connect(
        host=settings.database_host,
        port=settings.database_port,
        user=settings.database_user,
        password=settings.database_password,
        database=settings.database_name
    )
    return conn


async def get_db_pool() -> asyncpg.Pool:
    """
    Create and return a connection pool for the database.
    
    Returns:
        asyncpg.Pool: Database connection pool
    """
    pool = await asyncpg.create_pool(
        host=settings.database_host,
        port=settings.database_port,
        user=settings.database_user,
        password=settings.database_password,
        database=settings.database_name,
        min_size=1,
        max_size=10
    )
    return pool


async def create_tables() -> None:
    """
    Create database tables if they don't already exist.
    Reads the SQL schema from database_schema.sql and executes it.
    """
    try:
        # Get the path to the database schema file
        schema_file_path = Path(__file__).parent.parent / "database_schema.sql"
        
        # Read the SQL schema
        with open(schema_file_path, 'r') as f:
            schema_sql = f.read()
        
        # Connect to database and execute schema
        conn = await connect_to_db()
        try:
            await conn.execute(schema_sql)
            print("Database tables created successfully")
        finally:
            await conn.close()
            
    except FileNotFoundError:
        print(f"Schema file not found at {schema_file_path}")
        raise
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise


async def test_connection() -> bool:
    """
    Test the database connection and return True if successful.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    conn = await connect_to_db()
    if conn:
        try:
            # Test the connection with a simple query
            result = await conn.fetchval('SELECT 1')
            print(f"Database connection test successful: {result}")
            await conn.close()
            return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            await conn.close()
            return False
    print("Database connection test failed")
    return False
