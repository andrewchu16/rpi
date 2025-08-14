import asyncpg
from config import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME

async def connect_to_db() -> asyncpg.connection.Connection:
    """Establish a connection to the PostgreSQL database."""
    conn = await asyncpg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME
    )
    return conn

async def get_db_pool():
    """Create and return a connection pool for the database."""
    pool = await asyncpg.create_pool(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        min_size=1,
        max_size=10
    )
    return pool

async def test_connection():
    """Test the database connection and return True if successful."""
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

