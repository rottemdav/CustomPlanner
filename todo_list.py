from PySide6.QtWidgets import ( QWidget, QVBoxLayout, QLabel, 
                                QTableWidget, QHeaderView, QPushButton,
                                QTableWidgetItem, QHBoxLayout, 
                                QListWidget, QListWidgetItem, QCheckBox, 
                                QLineEdit, QInputDialog,QAbstractItemView, QMenu,
                                QSizePolicy, QDialog, QDialogButtonBox, QDateTimeEdit,
                                QSpinBox
                                )
from PySide6.QtCore import QDate, Qt, QEvent, Signal, QSize, QDateTime
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QBrush, QColor, QAction
from datetime import timedelta, date

from db_manager import AppDB

class ToDoList(QWidget):
    def __init__(self, date:QDate, db:AppDB):
        super().__init__()

        if date:
            self.date = date.toString("yyyy-MM-dd")
        else:
            self.date = None
        self.db = db
        # self.setMinimumSize(600,800)
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
        self.tasks_list.setSpacing(1)

        # -------------- list widget styling  --------------
        self.tasks_list.setAttribute(Qt.WA_StyledBackground, True)
        self.tasks_list.setObjectName("tasksList")
        self.tasks_list.setStyleSheet("""
                #tasksList {
                    background: #FFFFFF;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 6px;
                           }
                           """)

        tasks_layout.addWidget(self.tasks_list)

        self.load_on_start()

    def add_line(self):
        line_text = self.line_input.text().strip()
        if line_text:
            #add new task as a new record in the db
            task_id = self.db.add_task(line_text, self.date)

            new_row = QListWidgetItem()
            new_row.setData(Qt.UserRole, task_id)
            new_item = TaskItem(line_text, self.db, task_id, status=0, working_date="")
            new_item.priority_changed.connect(self.load_on_start)
            new_row.setSizeHint(new_item.sizeHint())

            #add new item to the list
            self.tasks_list.addItem(new_row)
            self.tasks_list.setItemWidget(new_row, new_item)
            self.line_input.clear()

    def delete_line(self):
        curr_row = self.tasks_list.currentRow()
        if curr_row >= 0:
            curr_item = self.tasks_list.item(curr_row)
            line_id = curr_item.data(Qt.UserRole)

            #delete the record from the db
            if (line_id) is not None:
                self.db.remove_personal_task(line_id)

            self.tasks_list.takeItem(curr_row)

    def load_on_start(self):
        self.tasks_list.clear()
        if self.date:
            curr_tasks = self.db.get_tasks_by_date(self.date)
        else:
            curr_tasks = self.db.get_all_tasks()
        #print(f"curr_tasks: {curr_tasks}")

        sorted_tasks = sorted(curr_tasks, key=lambda task: (task[3])) #sort by priority
        #print(f"sorted_tasks: {sorted_tasks}")


        for line_id, text, working_date, priority in sorted_tasks:
            new_row = QListWidgetItem()
            new_row.setData(Qt.UserRole, line_id)
            new_item = TaskItem(text, self.db, line_id, status=0, working_date=working_date)
            new_item.priority_changed.connect(self.load_on_start)
            new_row.setSizeHint(new_item.sizeHint())

            #add new item to the list
            self.tasks_list.addItem(new_row)
            self.tasks_list.setItemWidget(new_row, new_item)

    def update_date_and_tasks(self, date: QDate):
        self.date = date.toString("yyyy-MM-dd")
        self.load_on_start()  

class TaskItem(QWidget):
    clicked = Signal()
    priority_changed = Signal()

    def __init__ (self, task_text:str, db, task_id:int, status:int, working_date:str):
        super().__init__()
        self.db = db
        self.task_id = task_id
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # ---------------- style ------------------------------
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("taskItem")
        self.setStyleSheet("""
                #taskItem {
                    background: #FFFFFF;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 4px;
                    padding-bottom: 3px;
                }
                #taskItem QCheckBox:checked {
                    color: gray;
                    text-decoration: line-through;
                }
                           """)

        # --------------- main verical layout ------------------
        self.main_layout = QVBoxLayout(self)        
        self.main_layout.setContentsMargins(5,1,5,1)
        self.main_layout.setSpacing(2)

        # ---------------- top row -----------------------------
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0,0,0,0)

        self.task_checkbox = QCheckBox(task_text)
        self.task_checkbox.setLayoutDirection(Qt.RightToLeft)
        self.task_checkbox.clicked.connect(self.select_item)
        self.task_checkbox.stateChanged.connect(self.task_checked)
        #set the checkbox with the current status of the task
        self.task_checkbox.setChecked(status == 1)
        #if status == 1:
        #    self.setStyleSheet("text-decoration: line-through; color: gray")

        top_row.addWidget(self.task_checkbox)
        self.main_layout.addLayout(top_row)

        self.doing_date = QLabel("")
        self.doing_date.setVisible(False)
        self.doing_date.setWordWrap(True)
        self.doing_date.setStyleSheet("color: #6600CC; font-size: 10px;")
        self.doing_date.setContentsMargins(0,0,20,3)
        self.main_layout.addWidget(self.doing_date)

        if working_date:
            self.show_working_date(working_date)

        # ------------------------ actions -----------------------
        self.add_working_date_action = QAction("קביעת תאריך ביצוע", self)
        self.add_working_date_action.triggered.connect(self.set_working_date)
        self.delete_working_date_action = QAction("מחיקת תאריך ביצוע", self)
        self.delete_working_date_action.triggered.connect(self.delete_working_date)
        self.set_priority_action = QAction("קביעת עדיפות", self)
        self.set_priority_action.triggered.connect(self.set_task_priority)

        self.addAction(self.add_working_date_action)
        self.addAction(self.delete_working_date_action)
        self.addAction(self.set_priority_action)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)

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
        is_checked = (state == Qt.Checked.value)
        
        print(f"[LOG] Task status changed: {'checked' if is_checked else 'unchecked'}")

        if self.task_id is not None:
            print(f"[LOG] Changing status in the hw tasks table from {'unchecked' if not is_checked else 'checked'} to {'checked' if is_checked else 'unchecked'}")
            self.db.update_personal_task_status(self.task_id, int(is_checked))

            task_font = self.task_checkbox.font()
            task_font.setStrikeOut(is_checked)
            self.task_checkbox.setFont(task_font)

    # def contextMenuEvent(self, event):
    #     menu = QMenu(self)

    #     work_date_action = QAction("קביעת תאריך ביצוע", self)
    #     menu.addAction(work_date_action)

    #     delete_work_date_act = QAction("מחיקת תאריך ביצוע", self)
    #     menu.addAction(delete_work_date_act)

    #     selected_action = menu.exec(event.globalPos())
    #     if selected_action == work_date_action:
    #         self.set_working_date()
    #     elif selected_action == delete_work_date_act:
    #         self.delete_working_date()

# ============================ tasks actions ====================================

    def set_working_date(self):
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

            self.db.update_personal_working_date(self.task_id, chosen_datetime)

    def show_working_date(self, working_date_str: str):
        #print("show_working_date got:", working_date_str)

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

    def delete_working_date(self):
        self.doing_date.setVisible(False)
        self.db.update_personal_working_date(self.task_id, "")

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

    def set_task_priority(self):
        priority_dialog = QDialog(self)
        priority_dialog.setWindowTitle("קביעת עדיפות למשימה")
        
        layout = QVBoxLayout(priority_dialog)
        layout.addWidget(QLabel("קביעת עדיפות למשימה"))

        priority_select = QSpinBox()
        priority_select.setRange(1,30)
        #priority_select.setSuffix("עדיפות")
        priority_select.setValue(1)

        priority_select.setAlignment(Qt.AlignRight)
        priority_select.setLayoutDirection(Qt.RightToLeft)

        layout.addWidget(priority_select)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(priority_dialog.accept)
        buttons.rejected.connect(priority_dialog.reject)

        if priority_dialog.exec() == QDialog.Accepted:
            priority = priority_select.value()
            self.db.update_personal_priority(self.task_id, priority)
            self.priority_changed.emit()

            
        

