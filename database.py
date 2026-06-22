import sqlite3

def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    # Jadvalni yaratish
    cursor.execute('''CREATE TABLE IF NOT EXISTS videos 
                      (url TEXT PRIMARY KEY, file_id TEXT)''')
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
    except Exception as e:
        print(f"Bazadan olishda xato: {e}")
        return None