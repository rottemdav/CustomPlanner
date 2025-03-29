import sqlite3

DB_FILE = "planner.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute( """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_date TEXT,
            task TEXT NOT NULL,
            due_date TEXT,
            status INT DEFAULT 0           
        )    
    """)

    conn.commit()
    conn.close()

def add_task(text, task_date):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task, task_date) VALUES (?,?)", (text, task_date))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close

    return task_id

def remove_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task FROM tasks WHERE status = 0")
    tasks = cursor.fetchall()
    conn.close()

    return tasks

def get_tasks_by_date(date):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task FROM tasks WHERE task_date = ? and status = 0", (date,))
    tasks = cursor.fetchall()
    conn.close()

    return tasks
