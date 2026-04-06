import psycopg2
import sys
from psycopg2.extras import RealDictCursor

# UPDATED with your new password
DB_URL = "postgresql://postgres.vjjbjyllpedhgtrzivdd:ticksheet123!@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def get_conn():
    return psycopg2.connect(DB_URL)

def run_query(sql):
    try:
        conn = get_conn()
        conn.autocommit = True
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            if sql.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                for row in rows: print(row)
            else:
                print("Success: Command executed.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def seed():
    print("Starting Direct Terminal Seed...")
    # 1. Create Roles
    run_query("INSERT INTO roles (name) VALUES ('Admin'), ('Manager'), ('Member') ON CONFLICT DO NOTHING;")
    
    # 2. Create Admin (Password_hash is a placeholder; backend will handle real hashes)
    run_query("""
        INSERT INTO users (email, password_hash, first_name, last_name, is_verified, role_id) 
        VALUES ('admin@tickmarks.com', 'placeholder_hash', 'Admin', 'User', true, 1) 
        ON CONFLICT (email) DO NOTHING;
    """)
    print("Seed process finished.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db_tool.py seed  OR  python db_tool.py \"SELECT...\"")
    elif sys.argv[1] == "seed":
        seed()
    else:
        run_query(sys.argv[1])
