# import psycopg2
# from config.settings import DB_URL

# def get_connection():
#     return psycopg2.connect(DB_URL)

import psycopg2
from config.settings import DB_URL

# ✅ Get DB connection using full connection string
def get_connection():
    return psycopg2.connect(DB_URL)

# ✅ Fetch user info (name, role) from database
def get_user_info(name):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, role FROM users WHERE name = %s", (name,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return {"name": result[0], "role": result[1]}
        else:
            return None
    except Exception as e:
        print(f"❌ DB Error: {e}")
        return None
