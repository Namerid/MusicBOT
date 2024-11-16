import sqlite3

conn = sqlite3.connect('Music_DB.db')

cur = conn.cursor()

cur.execute("""DELETE FROM Music""")
    
conn.commit()

conn.close