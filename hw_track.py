from PySide6.QtWidgets import ( QWidget, QVBoxLayout, QLabel, 
                                QTableWidget, QHeaderView, QPushButton,
                                QTableWidgetItem, QHBoxLayout, 
                                QListWidget, QListWidgetItem, QCheckBox, 
                                QLineEdit, QInputDialog,QAbstractItemView, QMenu,
                                QComboBox, QGridLayout, QDateEdit, QDialog, QDialogButtonBox, QDateTimeEdit,
                                QSizePolicy
                                )
from PySide6.QtCore import QDate, Qt, QEvent, Signal, QDateTime, QSize
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

        #add task button
        self.add_button = QPushButton("+")
        self.add_button.setFixedWidth(25)
        self.add_button.clicked.connect(self.add_to_list)

        #delte task button
        self.delete_button = QPushButton("-")
        self.delete_button.setFixedWidth(25)
        self.delete_button.clicked.connect(self.delete_task)

        #courses list
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

        #the main hw tracking lists
        hw_list_layout = QGridLayout()
        #create the hw grid
        for i in range(2):
            for j in range(3):
                course_hw_list = QListWidget()
                #course_hw_list.setMinimumWidth
                course_hw_list.setSelectionMode(QAbstractItemView.SingleSelection)
                course_hw_list.setSelectionBehavior(QAbstractItemView.SelectRows)

                course_name = self.courses_list.itemText((3*(i))+j)
                course_label = QLabel(course_name)

                #individual list layout and widget
                col_layout = QVBoxLayout()
                col_layout.addWidget(course_label, alignment=Qt.AlignCenter)
                col_layout.addWidget(course_hw_list)

                course_hw_widget = QWidget()
                course_hw_widget.setLayout(col_layout)

                self.hw_list_widgets.append(course_hw_list)
                hw_list_layout.addWidget(course_hw_widget, i, j)
            
        main_layout.addLayout(hw_list_layout)
        
        self.load_on_start()

    def add_to_list(self):
        print(f"[LOG] Adding new task to the hw tracking list...")
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

        new_item = TaskItemWidget(task_text, due_date, self.db, task_id, status=0, working_date="")

        #add to the list
        new_row.setSizeHint(new_item.sizeHint())
        target_list.addItem(new_row)
        target_list.setItemWidget(new_row, new_item)        

        print(f"[LOG] Added task with id  {task_id} to the to-do list.")

        self.new_input.clear()

    def delete_task(self):
        print(f"[LOG] Deleting a task to the hw tracking list...")
        course_index = -1
        curr_row = -1
        for i, lst in enumerate(self.hw_list_widgets):
            if lst.currentRow() >= 0:
                course_index = i
                curr_row = lst.currentRow()
                break
        
        if course_index < 0:
            print(f" [DEBUG] no course was chosen. tried to reach course in index {course_index}. Returning.")
            return

        target_list = self.hw_list_widgets[course_index]
        
        curr_row = target_list.currentRow()
        if curr_row >= 0:
            curr_item = target_list.item(curr_row)
            task_id = curr_item.data(Qt.UserRole)

            #delete the record from the db
            if (task_id) is not None:
                self.db.remove_task(task_id)

            target_list.takeItem(curr_row)

    def load_on_start(self):
        print("Loading Existing Tasks...")
        for course_list in self.hw_list_widgets:
            course_list.clear()

        all_tasks = self.db.get_all_hw_tasks()

        for task_id, task_desc, due_date_str, status, course_num, working_date in all_tasks:
            try:
                list_index = list(COURSE_NUMS.values()).index(course_num)
            except ValueError:
                print(f"[WARN] unknown course_id {course_num}. Skipping")
                continue

            #build tasks list
            item = QListWidgetItem()
            task_widget = TaskItemWidget(task_desc, due_date_str, self.db, task_id, status, working_date)
            item.setData(Qt.UserRole, task_id)
            item.setSizeHint(task_widget.sizeHint())
            target_list = self.hw_list_widgets[list_index]
            target_list.addItem(item)
            target_list.setItemWidget(item, task_widget)

        print("Finished Loading.")

    # def update_date_and_tasks(self, date: QDate):
    #     self.date = date.toString("yyyy-MM-dd")
    #     self.load_on_start()

class TaskItemWidget(QWidget):
    clicked = Signal()
    def __init__ (self, task_desc: str, due_date_str: str, db, task_id: int, status:int, working_date:str):
        
        super().__init__()
        self.db = db
        self.task_id = task_id
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        #caculating days left
        due_date = QDate.fromString(due_date_str, "yyyy-MM-dd")
        today = QDate.currentDate()
        days_remaining = today.daysTo(due_date)

        # --------------- main verical layout ------------------
        self.main_layout = QVBoxLayout(self)        
        self.main_layout.setContentsMargins(5,1,5,1)
        self.main_layout.setSpacing(2)

        # ---------------- top row -----------------------------
        top_row = QHBoxLayout(self)
        top_row.setContentsMargins(0,0,0,0)

        self.task_checkbox = QCheckBox(task_desc)
        self.task_checkbox.setLayoutDirection(Qt.RightToLeft)
        self.task_checkbox.clicked.connect(self.select_item)
        self.task_checkbox.stateChanged.connect(self.task_checked)
        #set the checkbox with the current status of the task
        self.task_checkbox.setChecked(status == 1)
        if status == 1:
            self.setStyleSheet("text-decoration: line-through; color: gray")

        formatted_date = QDate.fromString(due_date_str, "yyyy-MM-dd").toString("dd/MM/yyyy")
        self.due_date = QLabel(f"{formatted_date}")
        self.due_date.setAlignment(Qt.AlignCenter)
        self.due_date.setStyleSheet("font-weight: bold; color: #000000")

        remaining_text = f"{days_remaining} days left"
        self.remaining_label = QLabel(remaining_text)
        self.remaining_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        top_row.addWidget(self.task_checkbox)
        top_row.addWidget(self.due_date)
        top_row.addWidget(self.remaining_label)
        self.main_layout.addLayout(top_row)

        self.doing_date = QLabel("")
        self.doing_date.setVisible(False)
        self.doing_date.setWordWrap(True)
        self.doing_date.setStyleSheet("color: #6600CC; font-size: 10px;")
        self.doing_date.setContentsMargins(0,0,20,0)
        self.main_layout.addWidget(self.doing_date)

        if working_date:
            self.show_working_date(working_date)

    def sizeHint(self):
        height = self.main_layout.sizeHint().height()
        return QSize(0, height)

    def select_item(self):
        parent = self.parent()
        while parent and not isinstance(parent, QListWidget):
            parent= parent.parent()
        if isinstance(parent, QListWidget):
            list_widget = parent
            index = list_widget.indexAt(self.mapTo(list_widget, self.rect().center()))
            if index.isValid():
                #list_widget.setCurrentRow(index.row())
                item = list_widget.item(index.row())
                return item.data(Qt.UserRole) #task_id
            
        return None

    def task_checked(self, state):
        is_checked = state == Qt.Checked.value
        
        print(f"[LOG] Task status changed: {'checked' if is_checked else 'unchecked'}")

        if self.task_id is not None:
            print(f"[LOG] Changing status in the hw tasks table from {'unchecked' if not is_checked else 'checked'} to {'checked' if is_checked else 'unchecked'}")
            self.db.update_hw_task_status(self.task_id, int(is_checked))
            if is_checked:
                self.setStyleSheet("text-decoration: line-through; color: gray")
            else:
                self.setStyleSheet("")

    def contextMenuEvent(self, event):
        menu = QMenu (self)

        work_date_action = QAction("קביעת תאריך ביצוע", self)
        menu.addAction(work_date_action)

        selected_action = menu.exec(event.globalPos())
        if selected_action == work_date_action:
            self.set_work_date()

    def set_work_date(self):
        date_dialog = QDialog(self)
        date_dialog.setWindowTitle("בחירת תאריך ביצוע")

        layout = QVBoxLayout(date_dialog)
        layout.addWidget(QLabel("בחירת תאריך ביצוע משימה:"))
        
        date_chooser = QDateTimeEdit()
        date_chooser.setCalendarPopup(True)
        date_chooser.setDateTime(QDateTime.currentDateTime())
        date_chooser.setDisplayFormat("HH:mm dd/MM/yyyy")
        date_chooser.setLayoutDirection(Qt.RightToLeft)
        date_chooser.setAlignment(Qt.AlignRight)
        date_chooser.calendarWidget().setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(date_chooser)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(date_dialog.accept)
        buttons.rejected.connect(date_dialog.reject)
        

        if date_dialog.exec() == QDialog.Accepted:
            chosen_datetime = date_chooser.dateTime().toString("HH:mm dd-MM-yyyy")
            self.show_working_date(chosen_datetime)

            self.db.update_working_date(self.task_id, chosen_datetime)

    def show_working_date(self, working_date_str: str):
        print("show_working_date got:", working_date_str)

        if not working_date_str:
            print(f"[WARN] - 'show_working_date' : exited because working_date_str is None.")
            return
        dt = QDateTime.fromString(working_date_str, "HH:mm dd-MM-yyyy")
        if not dt.isValid():
            print(f"[LOG] - 'show_working_date': dt: {dt}")
            print(f"[WARN] - 'show_working_date' : exited because dt is not valid.")
            return
        
        chosen_date_str = dt.date().toString("dd/MM/yyyy")
    
        self.doing_date.setText(f"עושה ב: {chosen_date_str}")
        self.doing_date.setVisible(True)
        print(f"the doing_date status: {self.doing_date.isVisible()}")
        print("widget sizeHint: ", self.sizeHint())

        self.adjustSize()
        self.updateGeometry()

        p = self.parentWidget()
        while p and not isinstance(p, QListWidget):
            p = p.parentWidget()
        if not p:
            return
        lw = p
        for row in range(lw.count()):
            item = lw.item(row)
            if lw.itemWidget(item) is self:
                item.setSizeHint(self.sizeHint())
                break
        lw.doItemsLayout()
        lw.clearSelection()