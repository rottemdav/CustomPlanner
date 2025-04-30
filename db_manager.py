import sqlite3
from datetime import date, datetime, timedelta

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
                status INTEGER DEFAULT 0,
                working_date TEXT,
                priority INTEGER DEFAULT 2
            )    
        """)

        #hw tasks table
        cursor.execute( """
            CREATE TABLE IF NOT EXISTS hw_tasks_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                due_date TEXT,
                status INTEGER DEFAULT 0,
                course_num TEXT NOT NULL,
                working_date TEXT
            )    
        """)

        #events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_title TEXT NOT NULL,
                desc TEXT NOT NULL,
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

    def remove_personal_task(self, task_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personal_tasks_table WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def get_all_tasks(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, working_date, priority FROM personal_tasks_table WHERE status = 0")
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
    
    def update_personal_task_status(self, task_id, is_checked):
        #print(f"[DB-LOG] Updating HW task {task_id} status in personal tasks table...")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("UPDATE personal_tasks_table SET status = ? WHERE id =?", (is_checked, task_id))
        conn.commit()
        conn.close()
        print(f"[DB-LOG] Updated task {task_id} to status {is_checked} in personal tasks table.")

    def update_personal_working_date(self, task_id, date):
        #print(f"[DB-LOG] Updating working date for task with id: {task_id} in personal tasks table ...")
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE personal_tasks_table SET working_date = ? WHERE id =?", (date, task_id))
        print(f"[DB-LOG] Updated working date: {date} for task with id: {task_id} in personal tasks table.")
        tasks = cursor.fetchall()
        conn.commit()
        conn.close()
        return tasks
    
    def update_personal_priority(self, task_id, priority):
        #print(f"[DB-LOG] Updating priority for task with id: {task_id} in personal tasks table ...")
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE personal_tasks_table SET priority = ? WHERE id =?", (priority, task_id))
        print(f"[DB-LOG] Updated priority to: {priority} for task with id: {task_id} in personal tasks table.")
        tasks = cursor.fetchall()
        conn.commit()
        conn.close()
        return tasks
    


    # =============== HW TASKS METHODS ===============

    def add_hw_task(self, text, due_date, course):
        print(f"[DB-LOG] Adding HW task in course {course} to the hw tasks table...")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO hw_tasks_table (task, due_date, course_num) VALUES (?,?,?)", (text, due_date, course))
        task_id = cursor.lastrowid
        print(f"[DB-LOG] HW task in course {course} was added to the hw tasks table with the id {task_id}")
        conn.commit()
        conn.close

        return task_id
    
    def remove_task(self, task_id):
        print(f"[DB-LOG] Deleting HW task {task_id} from the hw tasks table...")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hw_tasks_table WHERE id = ?", (task_id,))
        print(f"[DB-LOG] Deleted HW task {task_id} from the hw tasks table.")
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

    def update_hw_task_status(self, task_id, is_checked):
        print(f"[DB-LOG] Updating HW task {task_id} status in hw tasks table...")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("UPDATE hw_tasks_table SET status = ? WHERE id =?", (is_checked, task_id))
        conn.commit()
        conn.close()
        print(f"[DB-LOG] Updated task {task_id} to status {is_checked}")

    def update_working_date(self, task_id, date):
        print(f"[DB-LOG] Updating working date for task with id: {task_id} ...")
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE hw_tasks_table SET working_date = ? WHERE id =?", (date, task_id))
        print(f"[DB-LOG] Updated working date: {date} for task with id: {task_id}.")
        tasks = cursor.fetchall()
        conn.commit()
        conn.close()
        return tasks



    # =============== EVENT METHODS    ===============

    def add_calendar_event(self, event_title: str, event_desc: str, 
                           event_date: str,
                           event_start_time: int, event_end_time: int, layer:str,
                           block_color:str, file_path:str, time_created: datetime):
        time_created = datetime.now()
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO events_table (event_title,  event_date, desc,
                                                 event_start_time, event_end_time, layer,
                                                 block_color, file_path, time_created) 
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                       (event_title, event_date, event_desc , event_start_time, event_end_time, layer , block_color, "" , time_created.isoformat())
                        )
        event_id = cursor.lastrowid
        conn.commit()
        print(f"[DB-LOG] Wrote event num {event_id} to the events_table. Start time: {event_start_time}")
        conn.close()
        return event_id
    
    def add_repeated_calendar_event(self, recur_num, event_title: str, event_desc: str, 
                           event_date: str,
                           event_start_time: int, event_end_time: int, layer:str,
                           block_color:str, file_path:str, time_created: datetime):
        time_created = datetime.now()
        start_dt = datetime.strptime(event_start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(event_end_time, "%Y-%m-%d %H:%M:%S")

        conn = self._connect()
        cursor = conn.cursor()
        ids = []

        for i in range(recur_num):
            loop_start_time = start_dt + timedelta(weeks=i)
            loop_end_time = end_dt + timedelta(weeks=i)
            loop_start_time_str = loop_start_time.strftime("%Y-%m-%d %H:%M:%S")
            loop_end_time_str = loop_end_time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                        INSERT INTO events_table (event_title,  event_date, desc,
                                                    event_start_time, event_end_time, layer,
                                                    block_color, file_path, time_created) 
                        VALUES (?,?,?,?,?,?,?,?,?)""",
                        (event_title, loop_start_time.date().isoformat(),
                          "" , loop_start_time_str, loop_end_time_str, layer , 
                          block_color, "" , time_created.isoformat())
                            )
            ids.append(cursor.lastrowid)
        event_id = cursor.lastrowid
        conn.commit()
        print(f"[DB‑LOG] Wrote {len(ids)} weekly copies; first id {ids[0]}")
        conn.close()
        return event_id
    
    def remove_calendar_event(self, event_id):
        #print(f"[DB-LOG] Removing event with id: {event_id} layer from events table...")
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events_table WHERE id = ?", (event_id,))
        conn.commit()
        print(f"[DB-LOG] - Deleted event {event_id} successfully from events_table.")
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
        
        print(f" [get_calendar_events_by_week]: Getting calendar events by date {start_date}...")

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
    
    def get_events_in_range(self, start_dt_str, end_dt_str):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM events_table
        WHERE NOT (event_end_time <= ? OR event_start_time >= ?)
        """, (start_dt_str, end_dt_str))
        events = cursor.fetchall()
        conn.close()
        return events

    def update_event_layer(self, event_id, new_layer):
        print(f"[DB-LOG] Updating event with id: {event_id} layer in events table...")
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE events_table SET layer = ? WHERE id =?", (new_layer, event_id))
        print(f"[DB-LOG] Updated event with id: {event_id} layer in events table to layer: '{new_layer}'")
        events = cursor.fetchall()
        conn.commit()
        conn.close()
        return events
    
    def update_event_color(self, event_id, new_color):
        print(f"[DB-LOG] Updating event with id: {event_id} color in events table...")
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE events_table SET block_color = ? WHERE id =?", (new_color, event_id))
        print(f"[DB-LOG] Updated event with id: {event_id} layer in events table to layer: '{new_color}'")
        events = cursor.fetchall()
        conn.commit()
        conn.close()
        return events


