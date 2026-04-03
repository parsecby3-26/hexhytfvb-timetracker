# automate_supabase.py
# Script to automatically initialize the Supabase database with the provided schema

import psycopg2
import sys

# Your database URL
DATABASE_URL = "postgresql://postgres.kpotdnigexmoxrkwsowb:nvkBIluO0i0OMtHl@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

def run_sql():
    try:
        # 1. Connect to Supabase
        print("Connecting to Supabase Database...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 2. Read the SQL File
        print("Reading initialize_database.sql...")
        with open('initialize_database.sql', 'r') as f:
            sql_script = f.read()

        # 3. Execute the SQL
        print("Executing SQL script (creating tables and seeding admin)...")
        cur.execute(sql_script)

        # 4. Commit and Close
        conn.commit()
        print("\n" + "=" * 50)
        print("✓ SUCCESS: Database Initialized!")
        print("✓ Admin User Created: hexhytfvb@gmail.com")
        print("✓ Tables Created: Users, Roles, User_Roles, Projects, etc.")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        sys.exit(1)
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_sql()
