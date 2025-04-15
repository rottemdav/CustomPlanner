from PySide6.QtWidgets import ( QWidget, QVBoxLayout, QLabel, 
                                QTableWidget, QHeaderView, QPushButton,
                                QTableWidgetItem, QHBoxLayout, 
                                QListWidget, QListWidgetItem, QCheckBox, 
                                QLineEdit, QInputDialog,QAbstractItemView, QMenu
                                )
from PySide6.QtCore import QDate, Qt, QEvent, Signal
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QBrush, QColor, QAction
from datetime import datetime, time, timedelta

#import from project files
from db_manager import AppDB

class CalendarBase(QWidget):
    def __init__(self, date:QDate, db:AppDB, rows: int, cols: int ,
                 headers: list[str], layers: list[str], parent=None):
        if (len(headers) != cols):
            return
        
        super().__init__()
        self.datetime = date
        self.event_date = self.datetime.toString("yyyy-MM-dd")
        self.db = db
        self.rows_num = rows
        self.cols_num = cols
        self.layers = layers
        self.headers = headers
        self.start_hour = rows % 24

        self.calendar_table = self.init_calendar_table_()

        #install event filter
        self.calendar_table.viewport().installEventFilter(self)
        self.calendar_table.cellDoubleClicked.connect(self.handle_double_click)

        self.col_width = self.calendar_table.columnWidth(0)

    def init_calendar_table_(self) -> QTableWidget:
        self.calendar_table = QTableWidget(self.rows_num, self.cols_num)
        self.calendar_table.setLayoutDirection(Qt.RightToLeft)
        self.calendar_table.setHorizontalHeaderLabels(self.headers)

        hour_labels = [F"{hour:02d}:00" for hour in range(self.rows_num)]
        self.calendar_table.setVerticalHeaderLabels(hour_labels)
        self.calendar_table.verticalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.calendar_table.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.calendar_table.setSelectionBehavior(QAbstractItemView.SelectItems)

        #handlers
        self.calendar_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.calendar_table.customContextMenuRequested.connect(self.open_context_menu)

        for row in range(self.rows_num):
            for col in range(self.cols_num):
                new_item = QTableWidgetItem("")
                new_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                new_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.calendar_table.setItem(row, col, new_item)

        return self.calendar_table

    def eventFilter(self, source, event):
        #print(f"[DEBUG] Event received: {event.type()}, from {source}")
        if source == self.calendar_table.viewport() and event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.RightButton:
                return False
            print(f"[DEBUG] :Left mouse released on table")
            self.handle_range_selection()
        return super().eventFilter(source,event)
    
    def handle_double_click(self, row, column):
        print(f"[DEBUG] cellDoubleClicked triggered: row {row}, column{column}")
        start_hour = row + self.start_hour
        end_hour = start_hour + 1
        time_label = f"{start_hour:02d}:00"

        idxs = self.calendar_table.selectedIndexes()
        if not idxs:
            return

        #cols = [index.column() for index in idxs]
        #col = cols[0]

        qdate = self.week_start_date.addDays(column)
        fulldate = qdate.toPython() # datetime.date

        start_dt = datetime.combine(fulldate, time(hour=start_hour))
        end_dt = datetime.combine(fulldate, time(hour=end_hour))

        text, ok = QInputDialog.getText(self, "time block", f"add event for: {time_label}:")
        if ok and text.strip():
            self.add_time_block(start_dt, end_dt, text, "double click")
            #new_item = QTableWidgetItem(text)

    def handle_range_selection(self):
        idxs = self.calendar_table.selectedIndexes()
        if not idxs:
            return
        
        rows = [index.row() for index in idxs]
        cols = [index.column() for index in idxs]
        
        top_row = min(rows)
        bottom_row = max(rows)
        col = cols[0]

        if any(c != col for c in cols):
            print("Selection error: multi-column selection not allowed")
            return

        if (bottom_row - top_row <= 0):
            return

        start_hour = self.start_hour + top_row
        end_hour = self.start_hour + bottom_row + 1

        qdate = self.week_start_date.addDays(col)
        fulldate = qdate.toPython() # datetime.date

        start_dt = datetime.combine(fulldate, time(hour=start_hour))
        end_dt = datetime.combine(fulldate, time(hour=end_hour))

        time_range = f"{start_dt.strftime('%d/%m/%Y %H/%M')} - {end_dt.strftime('%H/%M')}"
        text, ok = QInputDialog.getText(self, "time block", f"add event for: {time_range}:")
        if ok and text.strip():
            self.add_time_block(start_dt, end_dt, text, "multi-select")

        self.calendar_table.clearSelection()

    def add_time_block(self, start_dt: datetime, end_dt: datetime, text: str, action: str):
        print(f"[DEBUG] add_time_block triggered: start_time: {start_dt} end_time: {end_dt}")
        s_hour = start_dt.hour
        e_hour = end_dt.hour
        s_row = s_hour - self.start_hour
        dur = e_hour - s_hour
        weekday = (start_dt.weekday() + 1) % 7

        if not (0 <= s_row <self.calendar_table.rowCount()) or dur <= 0:
            return
        
        #check if there's existing overlap
        for r in range(s_row, s_row + dur):
            existing_item = self.calendar_table.item(r,weekday)
            if existing_item and existing_item.text().strip():
                print(f"Can't add event: overlaps with another at row {r}")
                return
            
        #no overlap - create new item
        # add the event to the DB
        event_id = self.db.add_calendar_event(
            event_title=text,
            event_date=start_dt.date().isoformat(), 
            event_start_time = start_dt, 
            event_end_time = end_dt,
            layer="",
            block_color = "#E0E0E0",
            file_path="",
            time_created=datetime.now()
            )
        print(f"Added event {event_id} to the db.")

        #create an item in the widget and display it
        new_item = QTableWidgetItem(text)
        new_item.setData(Qt.UserRole, event_id)


        #style
        new_item.setTextAlignment(Qt.AlignCenter)
        new_item.setBackground(QBrush(QColor("#E0E0E0")))

        #place data
        self.calendar_table.setItem(s_row, weekday, new_item)

        if dur > 1:
            self.calendar_table.setSpan(s_row, weekday,  dur, 1)
            for r in range(s_row +1, s_row + dur):
                self.calendar_table.setItem(r, weekday, QTableWidgetItem(""))

    def open_context_menu(self, position):
        idx = self.calendar_table.indexAt(position)
        if not idx.isValid():
            return
        
        row = idx.row()
        col = idx.column()

        selected_item = self.calendar_table.item(row,col)
        if selected_item is None or not selected_item.text().strip():
            return
        
        popup_menu = QMenu(self)
        delete_block = QAction("delete", self)
        popup_menu.addAction(delete_block)

        colors = {"pink": "#FFD7EA",
                  "blue":"#CCFFFF",
                  "green": "#E5FFCC",
                  "purple" : "#E5CCFF",
                  "yellow": "#FFFFCC"}
        color_change_actions = {}

        for color, hex in colors.items():
            action = QAction("change to "+ color, self)
            popup_menu.addAction(action)
            color_change_actions[action] = hex

        selected_action = popup_menu.exec(self.calendar_table.viewport().mapToGlobal(position))

        if selected_action == delete_block:
            self.delete_time_block(row, col)
        elif (selected_action in color_change_actions):
            hex = color_change_actions[selected_action]
            self.change_block_color(row,col, hex)

    def delete_time_block(self, row,col):
        row_span = self.calendar_table.rowSpan(row,col)
        event_to_delete = self.calendar_table.item(row,col)
        event_id = event_to_delete.data(Qt.UserRole)
        if (event_id):
            print(f"deleted event {event_id} in row {row}")
            self.db.remove_calendar_event(event_id)

        if row_span <= 1:
            self.calendar_table.setItem(row,col, QTableWidgetItem())
        else:
            self.calendar_table.setSpan(row,col,1,1)
            for r in range(row, row+row_span):
                self.calendar_table.setItem(r,col,QTableWidgetItem())

    def change_block_color(self, row:int, col:int, color: str):
        event_to_change = self.calendar_table.item(row,col)
        if (event_to_change):
            event_to_change.setBackground(QColor(color))

# =================  default opening functions  ============

    def load_events_by_date(self):
        events = self.db.get_calendar_events_by_date(self.date)
        for event_id, text, _, start_hour, end_hour, _, _, _, _ in events:
            start_dt = datetime.fromisoformat(start_hour)
            end_dt = datetime.fromisoformat(end_hour)
            dur = end_dt.hour - start_dt.hour
            s_row = start_dt.hour - 6
            #self.add_time_block(start_hour, end_hour, title, )
            new_item = QTableWidgetItem(text)
            new_item.setData(Qt.UserRole, event_id)

            #style
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setBackground(QBrush(QColor("#CCE5FF")))

            #place data
            self.calendar_table.setItem(s_row, 0, new_item)

            if dur > 1:
                self.calendar_table.setSpan(s_row, 0, dur, 1)
                for r in range(s_row +1, s_row + dur):
                    self.calendar_table.setItem(r, 0, QTableWidgetItem(""))

    def load_event_by_week(self, week_start_date, layer_filter=None):
        week_start = week_start_date.toPython()
        week_end = week_start + timedelta(days = 7)

        events = self.db.get_calendar_events_by_week(start_date = week_start.isoformat(),
                                                    end_date=week_end.isoformat(),
                                                    layer = layer_filter
                                                    )

        for event_id, text, event_date, start_str, end_str, color in events:
            start_dt = datetime.fromisoformat(start_str)
            end_dt = datetime.fromisoformat(end_str)

            s_row = start_dt.hour - self.start_hour
            dur = end_dt.hour - start_dt.hour

            day_offset = (start_dt.date() - week_start).days
            if not (0 <= day_offset <= 6):
                print(f"[DEBUG] out of range event on {start_dt.date()}")
                continue

            #create new item in the widget
            new_item = QTableWidgetItem(text)
            new_item.setData(Qt.UserRole, event_id)

            #style
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setBackground(QBrush(QColor("#CCE5FF")))

            self.calendar_table.setItem(s_row, day_offset, new_item)

            if dur > 1:
                self.calendar_table.setSpan(s_row, day_offset, dur, 1)
                for r in range(s_row +1, s_row + dur):
                    self.calendar_table.setItem(r, day_offset, QTableWidgetItem(""))

    def update_date_and_events(self, date:QDate, mode:str, layer:str):
        self.clear_calendar()
        self.date = date.toString("yyyy-MM-dd")
        if (mode == "week"):
            week_start = date.addDays(-date.dayOfWeek() % 7 )
            self.load_event_by_week(week_start, layer)
        
        else:
            self.load_events_by_date()

    def clear_calendar(self):
        self.calendar_table.clearContents()

        for row in range(self.calendar_table.rowCount()):
            if self.calendar_table.rowSpan(row,0) > 1:
                self.calendar_table.setSpan(row,0,1,1)

        #self._init_cells()     
