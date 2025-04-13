from PySide6.QtWidgets import ( QWidget, QVBoxLayout, QLabel, 
                                QTableWidget, QHeaderView, QPushButton,
                                QTableWidgetItem, QHBoxLayout, 
                                QListWidget, QListWidgetItem, QCheckBox, 
                                QLineEdit, QInputDialog,QAbstractItemView, QMenu
                                )
from PySide6.QtCore import QDate, Qt, QEvent, Signal
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QBrush, QColor, QAction

#import from project files
from db_manager import AppDB

class DayView(QWidget):
    daily_view_closed = Signal()
    def __init__(self, date: QDate, db:AppDB):
        super().__init__()

        self.db = db

        self.setWindowTitle(f"Daily View - {date.toString('yy-MM-dd')}")
        #self.setGeometry(200, 200, 300, 400)

        layout = QVBoxLayout(self)

        self.label = QLabel(f"תכנון יומי -  {date.toString('dddd, MMMM d, yyyy')}")
        layout.addWidget(self.label)

        #closing button
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(15,15)

        top_bar.addWidget(self.close_button)
        layout.addLayout(top_bar)

        #ToDo List
        self.todo_list = ToDoList(date, self.db)
        layout.addWidget(self.todo_list, stretch=3)

        self.daily_calendar = DailyCalendar(date, self.db)
        layout.addWidget(self.daily_calendar, stretch=7)

        #handlers
        self.close_button.clicked.connect(self.close_daily_view)

    def update_date(self, date:QDate):
        self.date = date
        self.label.setText(f"Tasks for {date.toString('dddd, MMM d')}")

        self.daily_calendar.clear_calendar()

        self.todo_list.update_date_and_tasks(date)
        self.daily_calendar.update_date_and_events(date)

    def close_daily_view(self):
        self.setVisible(False)
        self.daily_view_closed.emit()

class DailyCalendar(QWidget):
    def __init__(self, date:QDate, db:AppDB):
        super().__init__()
        self.date = date.toString("yyyy-MM-dd")
        self.db = db
        self.table = QTableWidget(19,1)

        self.table.setHorizontalHeaderLabels(["לו\"ז"])
        self.table.setVerticalHeaderLabels([f"{h:02d}:00" for h in range (6,25)])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.table.verticalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setLayoutDirection(Qt.RightToLeft)
        self.table.setStyleSheet("""
            QTableWidget::item {
                text-align:right;
            }
        """)

        #allow choosing multiple rows
        self.table.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        calendar_layout = QVBoxLayout(self)
        calendar_layout.addWidget(self.table)

        #handlers
        self.table.cellDoubleClicked.connect(self.handle_double_click)
        #self.table.selectionModel().selectionChanged.connect(self.handle_range_selection)
        self.table.viewport().installEventFilter(self)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)

        self._init_cells()

    def _init_cells(self):
         for row in range(self.table.rowCount()):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 0, item)

    def eventFilter(self, source, event):
        if source == self.table.viewport() and event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.RightButton:
                return False
            self.handle_range_selection()
        return super().eventFilter(source,event)

    def handle_double_click(self, row, column):
        start_hour = row + 6
        end_hour = start_hour + 1
        time_label = f"{start_hour:02d}:00"

        text, ok = QInputDialog.getText(self, "time block", f"add event for: {time_label}:")
        if ok and text.strip():
            self.add_time_block(start_hour, end_hour, text)
            new_item = QTableWidgetItem(text)

    def handle_range_selection(self):
        idxs = self.table.selectedIndexes()
        if not idxs:
            return
        
        top_row = min(index.row() for index in idxs)
        bottom_row = max(index.row() for index in idxs)

        if (bottom_row - top_row <= 0):
            return

        start_hour = top_row + 6
        end_hour = bottom_row + 7

        time_range = f"{start_hour:02d}:00 - {end_hour:02d}:00"
        text, ok = QInputDialog.getText(self, "time block", f"add event for: {time_range}:")
        if ok and text.strip():
            self.add_time_block(start_hour, end_hour, text,)

        self.table.clearSelection()

    def add_time_block(self, s_hour: int, e_hour: int, text: str):
        s_row = s_hour - 6
        dur = e_hour - s_hour

        if not (0 <= s_row <self.table.rowCount()) or dur <= 0:
            return
        
        #check if there's existing overlap
        for r in range(s_row, s_row + dur):
            existing_item = self.table.item(r,0)
            if existing_item and existing_item.text().strip():
                print(f"Can't add event: overlaps with another at row {r}")
                return
            
        #no overlap - create new item
        event_id = self.db.add_calendar_event(text, self.date, s_hour, e_hour,)
        new_item = QTableWidgetItem(text)
        new_item.setData(Qt.UserRole, event_id)

        #style
        new_item.setTextAlignment(Qt.AlignCenter)
        new_item.setBackground(QBrush(QColor("#CCE5FF")))

        #place data
        self.table.setItem(s_row, 0, new_item)

        if dur > 1:
            self.table.setSpan(s_row, 0, dur, 1)
            for r in range(s_row +1, s_row + dur):
                self.table.setItem(r, 0, QTableWidgetItem(""))

    def open_context_menu(self, position):
        idx = self.table.indexAt(position)
        if not idx.isValid():
            return
        
        row = idx.row()
        col = idx.column()

        selected_item = self.table.item(row,col)
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

        selected_action = popup_menu.exec(self.table.viewport().mapToGlobal(position))

        if selected_action == delete_block:
            self.delete_time_block(row, col)
        elif (selected_action in color_change_actions):
            hex = color_change_actions[selected_action]
            self.change_block_color(row,col, hex)

    def delete_time_block(self, row,col):
        row_span = self.table.rowSpan(row,col)
        event_to_delete = self.table.item(row,col)
        event_id = event_to_delete.data(Qt.UserRole)
        if (event_id):
            print(f"deleted event {event_id} in row {row}")
            self.db.remove_calendar_event(event_id)

        if row_span <= 1:
            self.table.setItem(row,col, QTableWidgetItem())
        else:
            self.table.setSpan(row,col,1,1)
            for r in range(row, row+row_span):
                self.table.setItem(r,col,QTableWidgetItem())

    def change_block_color(self, row:int, col:int, color: str):
        event_to_change = self.table.item(row,col)
        if (event_to_change):
            event_to_change.setBackground(QColor(color))

    def load_events_by_date(self):
        events = self.db.get_calendar_events_by_date(self.date)
        for event_id, text, start_hour, end_hour in events:
            dur = end_hour - start_hour
            s_row = start_hour - 6
            #self.add_time_block(start_hour, end_hour, title, )
            new_item = QTableWidgetItem(text)
            new_item.setData(Qt.UserRole, event_id)

            #style
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setBackground(QBrush(QColor("#CCE5FF")))

            #place data
            self.table.setItem(s_row, 0, new_item)

            if dur > 1:
                self.table.setSpan(s_row, 0, dur, 1)
                for r in range(s_row +1, s_row + dur):
                    self.table.setItem(r, 0, QTableWidgetItem(""))

    def update_date_and_events(self, date:QDate):
        self.date = date.toString("yyyy-MM-dd")
        self.clear_calendar()
        self.load_events_by_date()

    def clear_calendar(self):
        self.table.clearContents()

        for row in range(self.table.rowCount()):
            if self.table.rowSpan(row,0) > 1:
                self.table.setSpan(row,0,1,1)

        self._init_cells()     

class ToDoList(QWidget):
    def __init__(self, date:QDate, db:AppDB):
        super().__init__()

        self.date = date.toString("yyyy-MM-dd")
        self.db = db
        tasks_layout = QVBoxLayout(self)

        #single line layout
        line_layout = QHBoxLayout()
        self.line_input = QLineEdit()
        self.line_input.setPlaceholderText("משימה חדשה")
        
        #enables to add task on enter-click
        self.line_input.returnPressed.connect(self.add_line)

        self.add_button = QPushButton("+")
        self.add_button.setFixedWidth(25)
        self.add_button.clicked.connect(self.add_line)

        self.delete_button = QPushButton("-")
        self.delete_button.setFixedWidth(25)
        self.delete_button.clicked.connect(self.delete_line)

        #organizing the layout
        line_layout.addWidget(self.line_input)
        line_layout.addWidget(self.add_button)
        line_layout.addWidget(self.delete_button)

        tasks_layout.addLayout(line_layout)

        #create the tasks list
        self.tasks_list = QListWidget()
        tasks_layout.addWidget(self.tasks_list)

        self.load_on_start()

    def add_line(self):
        line_text = self.line_input.text().strip()
        if line_text:
            #add new task as a new record in the db
            task_id = self.db.add_task(line_text, self.date)

            new_item = QListWidgetItem()
            new_item.setData(Qt.UserRole, task_id)

            #set alignment RTL
            checkbox = QCheckBox(line_text)
            checkbox.setLayoutDirection(Qt.RightToLeft)
            checkbox.setStyleSheet("text-align: right")
            checkbox.setContentsMargins(0,0,10,0)

            #add new item
            self.tasks_list.addItem(new_item)
            self.tasks_list.setItemWidget(new_item, checkbox)
            self.line_input.clear()

    def delete_line(self):
        curr_row = self.tasks_list.currentRow()
        if curr_row >= 0:
            curr_item = self.tasks_list.item(curr_row)
            line_id = curr_item.data(Qt.UserRole)

            #delete the record from the db
            if (line_id) is not None:
                self.db.remove_task(line_id)

            self.tasks_list.takeItem(curr_row)

    def load_on_start(self):
        self.tasks_list.clear()
        curr_date_tasks = self.db.get_tasks_by_date(self.date)

        for line_id, text in curr_date_tasks:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, line_id)

            checkbox = QCheckBox(text)
            checkbox.setLayoutDirection(Qt.RightToLeft)
            checkbox.setStyleSheet("text-align: right")
            checkbox.setContentsMargins(0,0,10,0)

            self.tasks_list.addItem(item)
            self.tasks_list.setItemWidget(item, checkbox)

    def update_date_and_tasks(self, date: QDate):
        self.date = date.toString("yyyy-MM-dd")
        self.load_on_start()

        

