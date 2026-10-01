import sqlite3

conn = sqlite3.connect("instance/database.db")
cursor = conn.cursor()

columns = [
    ("meta_description", "TEXT"),
    ("review", "TEXT"),
    ("buying_guide", "TEXT"),
    ("ai_generated", "BOOLEAN DEFAULT 0")
]

for name, col_type in columns:
    try:
        cursor.execute(f"ALTER TABLE deals ADD COLUMN {name} {col_type}")
        print(f"Added: {name}")
    except sqlite3.OperationalError as e:
        print(f"Skipped {name}: {e}")

conn.commit()
conn.close()

print("Database updated successfully.")