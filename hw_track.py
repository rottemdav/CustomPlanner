from PySide6.QtWidgets import ( QWidget, QVBoxLayout, QLabel, 
                                QTableWidget, QHeaderView, QPushButton,
                                QTableWidgetItem, QHBoxLayout, 
                                QListWidget, QListWidgetItem, QCheckBox, 
                                QLineEdit, QInputDialog,QAbstractItemView, QMenu,
                                QComboBox, QGridLayout, QDateEdit
                                )
from PySide6.QtCore import QDate, Qt, QEvent, Signal
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QBrush, QColor, QAction

from db_manager import AppDB
from constants import COURSE_NUMS

class HWTracking(QWidget):
    def __init__(self, date:QDate, db:AppDB):
        super().__init__()

        self.date = date.toString("yyyy-MM-dd")
        self.setLayoutDirection(Qt.RightToLeft)
        self.db = db

        main_layout = QVBoxLayout(self)
        
        #single line layout
        new_submission = QHBoxLayout()
        self.new_input = QLineEdit()
        self.new_input.setPlaceholderText("הגשה חדשה")
        
        #enables to add task on enter-click
        #self.new_input.returnPressed.connect(self.add_line)

        self.add_button = QPushButton("+")
        self.add_button.setFixedWidth(25)
        self.add_button.clicked.connect(self.add_to_list)

        self.delete_button = QPushButton("-")
        self.delete_button.setFixedWidth(25)
        #self.delete_button.clicked.connect(self.delete_line)

        self.courses_list = QComboBox()
        self.courses_list.addItems(["אותות אקראיים", "ענ\"ת", "מערכות לומדות","מעגלים אלקטרוניים","מל\"מ"])
        self.courses_list.setCurrentIndex(-1)

        self.date_chooser = QDateEdit()
        self.date_chooser.setCalendarPopup(True)
        self.date_chooser.setDate(QDate.currentDate())
        self.date_chooser.setLayoutDirection(Qt.RightToLeft)
        self.date_chooser.setAlignment(Qt.AlignRight)
        self.date_chooser.calendarWidget().setLayoutDirection(Qt.RightToLeft)
        self.date_chooser.calendarWidget().setFirstDayOfWeek(Qt.Sunday)


        #organizing the layout
        new_submission.addWidget(self.new_input)
        new_submission.addWidget(self.add_button)
        new_submission.addWidget(self.delete_button)
        new_submission.addWidget(self.courses_list)
        new_submission.addWidget(self.date_chooser)

        main_layout.addLayout(new_submission)

        self.hw_list_widgets = []

        hw_list_layout = QGridLayout()
        #create the hw grid
        for i in range(2):
            for j in range(3):
                course_hw_list = QListWidget()
                course_name = self.courses_list.itemText((3*(i))+j)
                course_label = QLabel(course_name)

                col_layout = QVBoxLayout()
                col_layout.addWidget(course_label, alignment=Qt.AlignCenter)
                col_layout.addWidget(course_hw_list)

                course_hw_widget = QWidget()
                course_hw_widget.setLayout(col_layout)

                self.hw_list_widgets.append(course_hw_list)
                hw_list_layout.addWidget(course_hw_widget, i, j)
            
        main_layout.addLayout(hw_list_layout)
        
    #    self.load_on_start()

    def add_to_list(self):
        print(f" [LOG] Adding new task to the hw tracking list...")
        task_text = self.new_input.text().strip()
        chosen_course = self.courses_list.currentIndex()
        if not task_text or chosen_course < 0:
            print(f" [DEBUG] No course chose or empty line. STOP.")
            return

        target_list = self.hw_list_widgets[chosen_course]
        due_date = self.date_chooser.date().toString("yyyy-MM-dd")

        course_name = self.courses_list.itemText(chosen_course)

        #add to the db
        task_id = self.db.add_hw_task(task_text, due_date, COURSE_NUMS[course_name])

        #create the task and the widget
        new_row = QListWidgetItem()
        new_row.setData(Qt.UserRole, task_id)
        new_item = QCheckBox(task_text)
        #style
        new_item.setLayoutDirection(Qt.RightToLeft)
        new_item.setStyleSheet("text-align:right")
        new_item.setContentsMargins(0,0,10,0)

        #add to the list
        target_list.addItem(new_row)
        target_list.setItemWidget(new_row, new_item)

        print(f" [LOG] Added task with id  {task_id} to the to-do list.")

        self.new_input.clear()
        

    # def add_line(self):
    #     line_text = self.line_input.text().strip()
    #     if line_text:
    #         #add new task as a new record in the db
    #         task_id = self.db.add_task(line_text, self.date)

    #         new_item = QListWidgetItem()
    #         new_item.setData(Qt.UserRole, task_id)

    #         #set alignment RTL
    #         checkbox = QCheckBox(line_text)
    #         checkbox.setLayoutDirection(Qt.RightToLeft)
    #         checkbox.setStyleSheet("text-align: right")
    #         checkbox.setContentsMargins(0,0,10,0)

    #         #add new item
    #         self.tasks_list.addItem(new_item)
    #         self.tasks_list.setItemWidget(new_item, checkbox)
    #         self.line_input.clear()

    # def delete_line(self):
    #     curr_row = self.tasks_list.currentRow()
    #     if curr_row >= 0:
    #         curr_item = self.tasks_list.item(curr_row)
    #         line_id = curr_item.data(Qt.UserRole)

    #         #delete the record from the db
    #         if (line_id) is not None:
    #             self.db.remove_task(line_id)

    #         self.tasks_list.takeItem(curr_row)

    # def load_on_start(self):
    #     self.tasks_list.clear()
    #     curr_date_tasks = self.db.get_tasks_by_date(self.date)

    #     for line_id, text in curr_date_tasks:
    #         item = QListWidgetItem()
    #         item.setData(Qt.UserRole, line_id)

    #         checkbox = QCheckBox(text)
    #         checkbox.setLayoutDirection(Qt.RightToLeft)
    #         checkbox.setStyleSheet("text-align: right")
    #         checkbox.setContentsMargins(0,0,10,0)

    #         self.tasks_list.addItem(item)
    #         self.tasks_list.setItemWidget(item, checkbox)

    # def update_date_and_tasks(self, date: QDate):
    #     self.date = date.toString("yyyy-MM-dd")
    #     self.load_on_start()

        
