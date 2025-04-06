from PySide6.QtWidgets import (
                                QApplication, QMainWindow, QCalendarWidget,
                                QPushButton, QStackedWidget, QWidget, QVBoxLayout,
                                QHBoxLayout
                               )
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QIcon


#classes import
from daily_view import DayView
from weekly_view import WeeklyView, WeeklyCalendarView
from clock_view import ClockView
from db_manager import AppDB
from menu_bar import TopBar
from hw_track import HWTracking
import sys

#inherting from QMainWindows
class MainWindow(QMainWindow):
    def __init__(self, db: AppDB):
        super().__init__()
        self.db = db

        self.setWindowTitle("Custom Planner")
        self.setWindowIcon(QIcon("assets/app_icon.ico"))
        self.setGeometry(100,100,600,700) # x, y,width height

        #top tool bar
        self.top_bar = TopBar(self)
        self.addToolBar(self.top_bar)

        #define the central layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget) #the verical main layout

        content_layout = QHBoxLayout()

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.day_view = DayView(QDate.currentDate(), self.db)
        self.day_view.setVisible(False)
        content_layout.addWidget(self.day_view, 1)

        #clock layout
        self.clock = ClockView()
        right_layout.addWidget(self.clock)

        #set the monthly calendar
        self.monthly_calendar = QCalendarWidget()
        self.monthly_calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.monthly_calendar.clicked.connect(self.open_daily_view)
        self.monthly_calendar.setLayoutDirection(Qt.RightToLeft)

        # set the weekly view
        self.weekly_view = WeeklyCalendarView(QDate.currentDate(), self.db)

        # define the stack to switch between the views
        self.calendar_stack = QStackedWidget()
        self.calendar_stack.addWidget(self.monthly_calendar) # index 0
        self.calendar_stack.addWidget(self.weekly_view) #index 1
        self.calendar_view = "month"

        self.hw_track = HWTracking(QDate.currentDate())

        self.right_view_stack = QStackedWidget()
        self.right_view_stack.addWidget(self.calendar_stack) #index 0
        self.right_view_stack.addWidget(self.hw_track) #index 1
        self.right_view = "calendar"

        right_layout.addWidget(self.right_view_stack, 1)
        content_layout.addWidget(right_widget, 2)     

        main_layout.addLayout(content_layout)

        #handlers
        self.day_view.daily_view_closed.connect(self.restore_size)

    def toggle_weekly_monthly(self):
        if self.calendar_view == "month":
            self.calendar_stack.setCurrentIndex(1)
            self.top_bar.switch_action.setText("Switch to Month View")
            self.calendar_view = "week"
        else:
            self.calendar_stack.setCurrentIndex(0)
            self.top_bar.switch_action.setText("Switch to Week View")
            self.calendar_view = "month"

    def switch_to_hw_track(self):
        if self.right_view == "calendar":
            self.right_view_stack.setCurrentIndex(1)
            print("Right View: Switched to HW tracking.")
            self.top_bar.hw_track.setText("Switch to Calendar")
            self.right_view = "hw_track"

        elif self.right_view == "hw_track":
            self.right_view_stack.setCurrentIndex(0)
            print("Right View: Switched to Calendar.")
            self.top_bar.hw_track.setText("Switch to Homework Tracking")
            self.right_view = "calendar"

    

             
    def open_daily_view(self, date: QDate):
        self.resize(1100,700)
        self.day_view.update_date(date)
        self.day_view.setVisible(True)
    
    def restore_size(self):
        self.resize(600,700)