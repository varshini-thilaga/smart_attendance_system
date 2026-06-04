import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "attendease.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','class_teacher')),
            class_name TEXT DEFAULT '',
            section TEXT DEFAULT '',
            year TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS TeacherClasses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            year TEXT NOT NULL,
            class_name TEXT NOT NULL,
            section TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            UNIQUE(teacher_id, year, class_name, section),
            FOREIGN KEY(teacher_id) REFERENCES Users(id)
        );

        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            year TEXT NOT NULL DEFAULT '',
            class_name TEXT NOT NULL,
            section TEXT NOT NULL,
            teacher_id INTEGER,
            UNIQUE(roll_no, year, class_name, section),
            FOREIGN KEY(teacher_id) REFERENCES Users(id)
        );

        CREATE TABLE IF NOT EXISTS Attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            year TEXT NOT NULL DEFAULT '',
            class_name TEXT NOT NULL DEFAULT '',
            section TEXT NOT NULL DEFAULT '',
            fn_status TEXT DEFAULT 'Ab' CHECK(fn_status IN ('P','Ab')),
            an_status TEXT DEFAULT 'Ab' CHECK(an_status IN ('P','Ab')),
            subject TEXT,
            marked_by INTEGER,
            UNIQUE(student_id, date),
            FOREIGN KEY(student_id) REFERENCES Students(id)
        );

        CREATE TABLE IF NOT EXISTS AttendancePhotos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT NOT NULL,
            class_name TEXT NOT NULL,
            section TEXT NOT NULL,
            date TEXT NOT NULL,
            session_type TEXT NOT NULL DEFAULT 'FN',
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS Timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            year TEXT NOT NULL DEFAULT '',
            class_name TEXT NOT NULL DEFAULT '',
            section TEXT NOT NULL DEFAULT '',
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            FOREIGN KEY(teacher_id) REFERENCES Users(id)
        );

        CREATE TABLE IF NOT EXISTS TrainLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT, class_name TEXT, section TEXT,
            trained_at TEXT DEFAULT (datetime('now'))
        );
    """)
    # Migrate: add missing columns if upgrading from old schema
    for col, definition in [
        ("year", "TEXT DEFAULT ''"),
        ("class_name", "TEXT DEFAULT ''"),
        ("section", "TEXT DEFAULT ''"),
    ]:
        try:
            conn.execute(f"ALTER TABLE Users ADD COLUMN {col} {definition}")
        except Exception:
            pass
    for col, definition in [
        ("year", "TEXT DEFAULT ''"),
    ]:
        try:
            conn.execute(f"ALTER TABLE Students ADD COLUMN {col} {definition}")
        except Exception:
            pass
    for col, definition in [
        ("year", "TEXT DEFAULT ''"),
        ("class_name", "TEXT DEFAULT ''"),
        ("section", "TEXT DEFAULT ''"),
    ]:
        try:
            conn.execute(f"ALTER TABLE Attendance ADD COLUMN {col} {definition}")
        except Exception:
            pass
    # Ensure TeacherClasses table exists (migration for older DBs)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS TeacherClasses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                year TEXT NOT NULL,
                class_name TEXT NOT NULL,
                section TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                UNIQUE(teacher_id, year, class_name, section),
                FOREIGN KEY(teacher_id) REFERENCES Users(id)
            )
        """)
    except Exception:
        pass
    # Ensure AttendancePhotos table exists
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS AttendancePhotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                class_name TEXT NOT NULL,
                section TEXT NOT NULL,
                date TEXT NOT NULL,
                session_type TEXT NOT NULL DEFAULT 'FN',
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
    except Exception:
        pass

    cur = conn.execute("SELECT id FROM Users WHERE role='admin' LIMIT 1")
    if not cur.fetchone():
        conn.execute(
            "INSERT INTO Users(full_name,email,password,role) VALUES(?,?,?,?)",
            ("Admin", "admin@attendease.com", hash_password("admin123"), "admin")
        )
    conn.commit()
    conn.close()
    print("Database initialized.")


if __name__ == "__main__":
    init_db()
