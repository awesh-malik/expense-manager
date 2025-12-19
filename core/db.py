import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2 import errors # Import error codes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback to ensure we catch the right variable
DATABASE_URL = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, sslmode='require')
        return conn
    except Exception as e:
        logger.error(f"DB Connection Failed: {e}")
        raise e

def init_db():
    """Creates tables if they don't exist."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_states (
                    user_id BIGINT PRIMARY KEY,
                    chat_id BIGINT,
                    state TEXT DEFAULT 'DASHBOARD',
                    data JSONB DEFAULT '{}'::jsonb,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    amount NUMERIC(10, 2) NOT NULL,
                    description TEXT,
                    involved_users TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("✅ Database Schema Initialized.")
    except Exception as e:
        logger.error(f"Schema Init Failed: {e}")
    finally:
        conn.close()

def get_user_state(user_id):
    """
    Fetches user state. Auto-heals (creates tables) if missing.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT state, data FROM user_states WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            if result:
                return result
            return {'state': 'DASHBOARD', 'data': {}}
    except errors.UndefinedTable:
        # 🚑 SELF-HEALING LOGIC
        logger.warning("Tables missing. Initializing DB...")
        conn.rollback() # Must rollback the failed transaction
        conn.close()    # Close bad connection
        init_db()       # Create tables
        return get_user_state(user_id) # Retry recursively
    except Exception as e:
        logger.error(f"Get State Failed: {e}")
        return {'state': 'DASHBOARD', 'data': {}}
    finally:
        if not conn.closed:
            conn.close()

# ... (Keep update_user_state, add_transaction, get_balances as they were) ...

def update_user_state(user_id, chat_id, state, data=None):
    conn = get_db_connection()
    data = data if data is not None else {}
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_states (user_id, chat_id, state, data, updated_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    state = EXCLUDED.state, 
                    chat_id = EXCLUDED.chat_id,
                    data = EXCLUDED.data,
                    updated_at = CURRENT_TIMESTAMP;
            """, (user_id, chat_id, state, Json(data)))
            conn.commit()
    except errors.UndefinedTable:
        # 🚑 SELF-HEALING LOGIC
        conn.rollback()
        conn.close()
        init_db()
        update_user_state(user_id, chat_id, state, data) # Retry
    finally:
        if not conn.closed:
            conn.close()

def add_transaction(user_id, amount, description, involved=None):
    conn = get_db_connection()
    involved = involved if involved else []
    try:
        with conn.cursor() as cur:
            # Ensure user exists in 'users' table first to satisfy Foreign Key
            cur.execute("""
                INSERT INTO users (user_id, username) VALUES (%s, 'User')
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id,))
            
            cur.execute("""
                INSERT INTO transactions (user_id, amount, description, involved_users)
                VALUES (%s, %s, %s, %s)
            """, (user_id, amount, description, involved))
            conn.commit()
    finally:
        conn.close()

def get_balances():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.username, SUM(t.amount) as total
                FROM transactions t
                JOIN users u ON t.user_id = u.user_id
                GROUP BY u.username
            """)
            return cur.fetchall()
    except errors.UndefinedTable:
        return [] # Return empty if tables don't exist yet
    finally:
        conn.close()

def get_all_users():
    """
    Fetches all registered users for the Members list.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT username, joined_at FROM users ORDER BY joined_at DESC")
            return cur.fetchall()
    except Exception:
        return []
    finally:
        conn.close()

def register_user(user_id, username, full_name):
    """
    Manually adds a user (used for the 'Join' button).
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, username, full_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE 
                SET username = EXCLUDED.username, full_name = EXCLUDED.full_name
            """, (user_id, username, full_name))
            conn.commit()
    finally:
        conn.close()
