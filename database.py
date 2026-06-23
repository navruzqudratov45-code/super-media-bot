import sqlite3

def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    # Videolar jadvali
    cursor.execute('''CREATE TABLE IF NOT EXISTS videos
                      (url TEXT PRIMARY KEY, file_id TEXT)''')
    # Foydalanuvchilar jadvali (YANGI)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, first_name TEXT)''')
    conn.commit()
    conn.close()

def save_video(url, file_id):
    try:
        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO videos (url, file_id) VALUES (?, ?)", (url, file_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Bazaga saqlashda xato: {e}")

def get_video(url):
    try:
        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT file_id FROM videos WHERE url=?", (url,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

# --- YANGI QO'SHILGAN KODLAR ---
def save_user(user_id, first_name):
    try:
        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        # Agar foydalanuvchi bazada bo'lmasa, uni qo'shadi
        cursor.execute("INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)", (user_id, first_name))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def count_users():
    try:
        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0
