import sqlite3

def init_db():
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS birthdays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_date TEXT,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_birthday(user_id: int, event_date: str, description: str):
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO birthdays (user_id, event_date, description) VALUES (?, ?, ?)",
        (user_id, event_date, description)
    )
    conn.commit()
    conn.close()

def get_all_birthdays(user_id: int):
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT description, event_date FROM birthdays WHERE user_id = ? ORDER BY event_date",
        (user_id,)
    )
    result = cursor.fetchall()
    conn.close()
    return result

def get_birthdays_by_date(user_id: int, event_date: str):
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, description FROM birthdays WHERE user_id = ? AND event_date = ?",
        (user_id, event_date)
    )
    result = cursor.fetchall()
    conn.close()
    return result

def delete_birthday_by_id(event_id: int):
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM birthdays WHERE id = ?", (event_id,)
    )
    conn.commit()
    conn.close()

