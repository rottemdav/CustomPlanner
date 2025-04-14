import sqlite3
from datetime import date, datetime

DB_FILE = "planner.db"

class AppDB:
    def __init__(self, DB_FILE="planner.db"):
        self.db_file = DB_FILE
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_file)


    def _init_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        #personal tasks table
        cursor.execute( """
            CREATE TABLE IF NOT EXISTS personal_tasks_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_date TEXT,
                task TEXT NOT NULL,
                due_date TEXT,
                status INTEGER DEFAULT 0        
            )    
        """)

        #hw tasks table
        cursor.execute( """
            CREATE TABLE IF NOT EXISTS hw_tasks_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                due_date TEXT,
                status INTEGER DEFAULT 0,
                course_num TEXT NOT NULL
            )    
        """)

        #events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_title TEXT NOT NULL,
                desc TEXT,
                event_date TEXT NOT NULL,
                event_start_time TEXT NOT NULL,
                event_end_time TEXT NOT NULL,
                layer TEXT NOT NULL,
                block_color TEXT,
                file_path TEXT,
                time_created TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


        conn.commit()
        conn.close()
    # =============== PERSONAL TASK METHODS ===============

    def add_task(self, text, task_date):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personal_tasks_table (task, task_date) VALUES (?,?)", (text, task_date))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close

        return task_id

    def remove_task(self, task_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personal_tasks_table WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def get_all_tasks(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, task FROM personal_tasks_table WHERE status = 0")
        tasks = cursor.fetchall()
        conn.close()

        return tasks

    def get_tasks_by_date(self, date):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, task FROM personal_tasks_table WHERE task_date = ? and status = 0", (date,))
        tasks = cursor.fetchall()
        conn.close()

        return tasks

    # =============== HW TASKS METHODS ===============

    def add_hw_task(self, text, due_date, course):
        print(f" [LOG] Adding HW task in course {course} to the hw tasks table...")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO hw_tasks_table (task, due_date, course_num) VALUES (?,?,?)", (text, due_date, course))
        task_id = cursor.lastrowid
        print(f" [LOG] HW task in course {course} was added to the hw tasks table with the id {task_id}")
        conn.commit()
        conn.close

        return task_id
    
    def remove_task(self, task_id):
        print(f" [LOG] Deleting HW task {task_id} from the hw tasks table...")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personal_tasks_table WHERE id = ?", (task_id,))
        print(f" [LOG] Deleted HW task {task_id} from the hw tasks table.")
        conn.commit()
        conn.close()

    def get_all_hw_tasks(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT  * 
                        FROM hw_tasks_table
                        """)
        tasks = cursor.fetchall()
        conn.close()
        print(tasks)
        return tasks

    # =============== EVENT METHODS    ===============

    def add_calendar_event(self, event_title: str, event_date: str,
                           event_start_time: int, event_end_time: int, layer:str,
                           block_color:str, file_path:str, time_created: datetime):
        time_created = datetime.now()
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO events_table (event_title,  event_date,
                                                 event_start_time, event_end_time, layer,
                                                 block_color, file_path, time_created) 
                       VALUES (?,?,?,?,?,?,?,?)""",
                       (event_title, event_date, event_start_time, event_end_time, "" , block_color, "" , time_created.isoformat())
                        )
        event_id = cursor.lastrowid
        conn.commit()
        print(f"wrote event num {event_id} to the events_table.")
        conn.close()
        return event_id
    
    def remove_calendar_event(self, event_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events_table WHERE id = ?", (event_id,))
        conn.commit()
        print(f"deleted event {event_id} successfully from events_table.")
        conn.close()

    def get_calendar_events_by_date(self, date: str):
        
        print(f"Getting calendar events by date {date}...")

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""SELECT id, event_title, event_date, event_start_time, event_end_time, layer, block_color, file_path, time_created
                          FROM events_table 
                          WHERE event_date = ? 
                       """, (date,))
        events = cursor.fetchall()
        conn.close()
        print(events)
        return events
    
    def get_calendar_events_by_week(self, start_date: str, end_date: str,layer:str):
        
        print(f"Getting calendar events by date {date}...")

        conn = self._connect()
        cursor = conn.cursor()
        if (layer == "all"):
            cursor.execute("""SELECT id, event_title, event_date, event_start_time, event_end_time, block_color
                          FROM events_table 
                          WHERE event_date >=  ? AND event_date < ? 
                       """, (start_date, end_date))
        else:
            cursor.execute("""SELECT id, event_title, event_date, event_start_time, event_end_time, block_color
                          FROM events_table 
                          WHERE event_date >=  ? AND event_date < ? AND layer = ?
                       """, (start_date, end_date, layer))
        events = cursor.fetchall()
        conn.close()
        print(events)
        return events

