from PySide6.QtWidgets import ( QWidget, QVBoxLayout, QLabel, 
                                QTableWidget, QHeaderView, QPushButton,
                                QTableWidgetItem, QHBoxLayout, 
                                QListWidget, QListWidgetItem, QCheckBox, 
                                QLineEdit )
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QTableWidgetItem

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
        self.todo_list = ToDoList()
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

    def close_daily_view(self):
        self.setVisible(False)

class ToDoList(QWidget):
    def __init__(self):
        super().__init__()

        tasks_layout = QVBoxLayout(self)

        #single line layout
        line_layout = QHBoxLayout()
        self.line_input = QLineEdit()
        self.line_input.setPlaceholderText("משימה חדשה")
        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.add_line)

        #organizing the layout
        line_layout.addWidget(self.line_input)
        line_layout.addWidget(self.add_button)

        tasks_layout.addLayout(line_layout)

        #create the tasks list
        self.tasks_list = QListWidget()
        tasks_layout.addWidget(self.tasks_list)

    def add_line(self):
        line_text = self.line_input.text().strip()
        if line_text:
            new_item = QListWidgetItem()
            checkbox = QCheckBox(line_text)

            #set alignment RTL
            checkbox.setLayoutDirection(Qt.RightToLeft)
            checkbox.setStyleSheet("text-align: right")
            checkbox.setContentsMargins(0,0,10,0)

            #add new item
            self.tasks_list.addItem(new_item)
            self.tasks_list.setItemWidget(new_item, checkbox)
            self.line_input.clear()



        

