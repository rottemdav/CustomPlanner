from PySide6.QtWidgets import ( QWidget, QVBoxLayout, QLabel, 
                                QTableWidget, QHeaderView, QPushButton,
                                QTableWidgetItem, QHBoxLayout, 
                                QListWidget, QListWidgetItem, QCheckBox, 
                                QLineEdit )
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QTableWidgetItem

#import from project files
from db_manager import add_task, remove_task, get_all_tasks, get_tasks_by_date

class DayView(QWidget):
    def __init__(self, date: QDate):
        super().__init__()
        self.setWindowTitle(f"Daily View - {date.toString('yy-MM-dd')}")
        #self.setGeometry(200, 200, 300, 400)

        layout = QVBoxLayout(self)

        self.label = QLabel(f"תכנון יומי -  {date.toString('dddd, MMMM d, yyyy')}")
        layout.addWidget(self.label)

        #closing button
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(30,30)
        self.close_button.clicked.connect(self.close_daily_view)

        top_bar.addWidget(self.close_button)
        layout.addLayout(top_bar)

        #ToDo List
        self.todo_list = ToDoList(date)
        layout.addWidget(self.todo_list)

        #tasks table
        self.table = QTableWidget(19,1)
        self.table.setHorizontalHeaderLabels(["לו\"ז"])
        self.table.setVerticalHeaderLabels([f"{h:02d}:00" for h in range (6,25)])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.table)

        for row in range(self.table.rowCount()):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 0, item)

    def update_date(self, date:QDate):
        self.date = date
        self.label.setText(f"Tasks for {date.toString('dddd, MMM d')}")

        self.table.clearContents()

        self.todo_list.update_date_and_tasks(date)

    def close_daily_view(self):
        self.setVisible(False)

class ToDoList(QWidget):
    def __init__(self, date:QDate):
        super().__init__()
        self.date = date.toString("yyy-MM-dd")

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
            task_id = add_task(line_text, self.date)

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
                remove_task(line_id)

            self.tasks_list.takeItem(curr_row)

    def load_on_start(self):
        self.tasks_list.clear()
        curr_date_tasks = get_tasks_by_date(self.date)

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

        

