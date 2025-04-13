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

        #formatting the information
        formatted_date = QDate.fromString(due_date, "yyyy-MM-dd").toString("dd/MM/yyyy")

        new_item = TaskItemWidget(task_text, formatted_date)

        #add to the list
        target_list.addItem(new_row)
        target_list.setItemWidget(new_row, new_item)

        print(f" [LOG] Added task with id  {task_id} to the to-do list.")

        self.new_input.clear()

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


class TaskItemWidget(QWidget):
    def __init__ (self, task_desc: str, due_date_str: str):
        super().__init__()

        #caculating days left
        due_date = QDate.fromString(due_date_str, "dd/MM/yyyy")
        today = QDate.currentDate()
        days_remaining = today.daysTo(due_date)

        task_layout = QHBoxLayout(self)
        task_layout.setContentsMargins(10,0,10,0)

        self.task_checkbox = QCheckBox(task_desc)
        self.task_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.due_date = QLabel(f"{due_date_str}")
        self.due_date.setAlignment(Qt.AlignCenter)
        self.due_date.setStyleSheet("font-weight: bold; color: #000877")

        remaining_text = f"{days_remaining} days left"
        self.remaining_label = QLabel(remaining_text)
        self.remaining_label.setAlignment(Qt.AlignLeft)

        task_layout.addWidget(self.task_checkbox)
        task_layout.addWidget(self.due_date)
        task_layout.addWidget(self.remaining_label)
