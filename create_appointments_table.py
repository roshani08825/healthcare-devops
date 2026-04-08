import sqlite3
import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    doctor TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
            reason TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ Table 'appointments' created successfully!")
