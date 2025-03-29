from PySide6.QtWidgets import (
                                QApplication, QMainWindow, QCalendarWidget,
                                QPushButton, QStackedWidget, QWidget, QVBoxLayout,
                                QHBoxLayout
                               )
from PySide6.QtCore import QDate, Qt

#project files import
from daily_view import DayView
from weekly_view import WeeklyView
from main_window import MainWindow
from db_manager import init_db
import sys

if __name__ == "__main__":          
    app = QApplication(sys.argv)

    init_db()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
