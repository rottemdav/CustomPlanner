from PySide6.QtWidgets import (
                                QApplication, QMainWindow, QCalendarWidget,
                                QPushButton, QStackedWidget, QWidget, QVBoxLayout,
                                QHBoxLayout
                               )
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QIcon


#files import
from daily_view import DayView
from weekly_view import WeeklyView
from clock_view import ClockView
import sys

#inherting from QMainWindows
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Planner")
        self.setWindowIcon(QIcon("assets/app_icon.ico"))
        self.setGeometry(100,100,1000,600) # x, y,width height

        #define the central layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget) #the verical main layout

        #the clock and the toggle button layout
        toggle_clock_layout = QHBoxLayout()
        main_layout.addLayout(toggle_clock_layout)

        #define the toggle button to switch between weekly and monthly view
        self.toggle_button = QPushButton("Switch to Weekly View")
        self.toggle_button.clicked.connect(self.toggle_weekly_monthly)

        #clock layout
        self.clock = ClockView()
        toggle_clock_layout.addWidget(self.clock)
        toggle_clock_layout.addWidget(self.toggle_button)

        #horizontal content
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        self.day_view = DayView(QDate.currentDate())
        self.day_view.setVisible(False)

        #set the monthly calendar
        self.monthly_calendar = QCalendarWidget()
        self.monthly_calendar.clicked.connect(self.open_daily_view)
        self.monthly_calendar.setLayoutDirection(Qt.RightToLeft)

        # set the weekly view
        self.weekly_view = WeeklyView()

        # define the stack to switch between the views
        self.stack = QStackedWidget()
        self.stack.addWidget(self.monthly_calendar) # index 0
        self.stack.addWidget(self.weekly_view) #index 1

        content_layout.addWidget(self.stack, 2)
        content_layout.addWidget(self.day_view, 1)
        
        self.current_view = "month"

    def toggle_weekly_monthly(self):
        if self.current_view == "month":
            self.stack.setCurrentIndex(1)
            self.toggle_button.setText("Switch To Monthly View")
            self.current_view = "week"
        else:
            self.stack.setCurrentIndex(0)
            self.toggle_button.setText("Switch to Weekly View")
            self.current_view = "month"
             
    def open_daily_view(self, date: QDate):
        self.day_view.update_date(date)
        self.day_view.setVisible(True)