from database import get_conn

conn = get_conn()

migrations = [
    ("Users",      "year",       "TEXT DEFAULT ''"),
    ("Users",      "class_name", "TEXT DEFAULT ''"),
    ("Users",      "section",    "TEXT DEFAULT ''"),
    ("Students",   "year",       "TEXT DEFAULT ''"),
    ("Attendance", "year",       "TEXT DEFAULT ''"),
    ("Attendance", "class_name", "TEXT DEFAULT ''"),
    ("Attendance", "section",    "TEXT DEFAULT ''"),
    ("TrainLog",   "year",       "TEXT DEFAULT ''"),
    ("Timetable",  "year",       "TEXT DEFAULT ''"),
    ("Timetable",  "class_name", "TEXT DEFAULT ''"),
    ("Timetable",  "section",    "TEXT DEFAULT ''"),
]

for table, col, defn in migrations:
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")
        print(f"  Added   {table}.{col}")
    except Exception as e:
        print(f"  Skipped {table}.{col} — {e}")

conn.commit()
conn.close()
print("Migration complete.")
