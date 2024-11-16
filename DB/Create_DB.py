import sqlite3

conn = sqlite3.connect('Music_DB.db')

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS Music(
            Track TEXT,
            Genre TEXT,
            Musical_group TEXT,
            Album TEXT,
            Duration TEXT)""")

conn.commit()

conn.close