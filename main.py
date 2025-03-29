from PySide6.QtWidgets import (
                                QApplication, QMainWindow, QCalendarWidget,
                                QPushButton, QStackedWidget, QWidget, QVBoxLayout,
                                QHBoxLayout
                               )
from PySide6.QtCore import QDate, Qt
from daily_view import DayView
from weekly_view import WeeklyView
from main_window import MainWindow
import sys

if __name__ == "__main__":          
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
