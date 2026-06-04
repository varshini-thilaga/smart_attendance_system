import sqlite3

connect = sqlite3.connect("Face-DataBase")
connect.execute("""CREATE TABLE IF NOT EXISTS Students (
    ID INTEGER PRIMARY KEY,
    Name TEXT,
    Roll TEXT,
    personID TEXT
)""")
connect.execute("""CREATE TABLE IF NOT EXISTS TrainLog (
    trained_at TEXT
)""")
connect.commit()
connect.close()
print("Database initialized successfully.")
