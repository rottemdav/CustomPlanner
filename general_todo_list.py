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
from todo_list import ToDoList

class GeneralTodoList(QWidget):
    def __init__(self, db:AppDB):
        super().__init__()

        self.setLayoutDirection(Qt.RightToLeft)
        self.db = db

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
    
        self.todo_label = QLabel("רשימת משימות:")
        self.todo_label.setStyleSheet("""
                                      font-size: 24pt;
                                      font-weight: 600;
                                      """)
        main_layout.addWidget(self.todo_label, 0, Qt.AlignHCenter)

        self.todo_list = ToDoList(date=None, db=self.db)
        self.todo_list.setFixedWidth(600)
        self.todo_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_layout.addWidget(self.todo_list, 1, Qt.AlignHCenter)

        main_layout.addStretch(1)


