import asyncpg
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
    return False
