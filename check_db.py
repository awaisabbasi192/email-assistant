import sqlite3

conn = sqlite3.connect('email_assistant.db')
cursor = conn.cursor()

# Check emails table
cursor.execute('SELECT * FROM emails LIMIT 5')
print("EMAILS TABLE:")
print(cursor.fetchall())

# Check drafts table
cursor.execute('SELECT * FROM drafts LIMIT 5')
print("\nDRAFTS TABLE:")
print(cursor.fetchall())

conn.close()
