from PySide6.QtWidgets import (
                                QApplication, QMainWindow, QCalendarWidget,
                                QPushButton, QStackedWidget, QWidget, QVBoxLayout,
                                QHBoxLayout, QLayout, QSizePolicy
                               )
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QIcon 


#classes import
from daily_view import DayView
from weekly_view import WeeklyCalendarView
from clock_view import ClockView
from db_manager import AppDB
from menu_bar import TopBar
from hw_track import HWTracking
from new_weekly_view import WeeklyView, WeeklyViewContainer
from general_todo_list import GeneralTodoList
import sys

#inherting from QMainWindows
class MainWindow(QMainWindow):
    def __init__(self, db: AppDB):
        super().__init__()
        self.db = db

        self.setWindowTitle("Custom Planner")
        self.setWindowIcon(QIcon("assets/app_icon.ico"))
        #self.setGeometry(100,100,600,700) # x, y,width height
        #self.setMinimumSize(1200,700)

        #top tool bar
        self.top_bar = TopBar(self)
        self.addToolBar(self.top_bar)

        #define the central layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget) #the verical main layout
        main_layout.setSizeConstraint(QLayout.SetMinimumSize)

        content_layout = QHBoxLayout()

        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)

        self.day_view = DayView(QDate.currentDate(), self.db)
        self.day_view.setVisible(False)
        self.day_view.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
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
        self.new_weekly_view = WeeklyViewContainer(self.db)
        #self.new_weekly_view.calendar_view.show_week(QDate.currentDate().toPython())
        
        self.weekly_view = WeeklyCalendarView(QDate.currentDate(), self.db)
        self.weekly_view.calendar_table.setFocusPolicy(Qt.StrongFocus)
        self.weekly_view.calendar_table.setMouseTracking(True)
        self.weekly_view.calendar_table.setEnabled(True)

        # define the stack to switch between the views
        self.calendar_stack = QStackedWidget()
        self.calendar_stack.addWidget(self.monthly_calendar) # index 0
        self.calendar_stack.addWidget(self.weekly_view) #index 1
        self.calendar_stack.addWidget(self.new_weekly_view) #index 2
        self.calendar_view = "month"

        self.calendar_stack.currentChanged.connect(lambda _: self.adjustSize())

        self.hw_track = HWTracking(QDate.currentDate(), self.db)
        self.general_todo_list = GeneralTodoList(self.db)

        self.right_view_stack = QStackedWidget()
        self.right_view_stack.addWidget(self.calendar_stack) #index 0
        self.right_view_stack.addWidget(self.hw_track) #index 1
        self.right_view_stack.addWidget(self.general_todo_list) #index 2
        self.right_view = "calendar"

        self.right_view_stack.currentChanged.connect(lambda _: self.adjustSize())

        right_layout.addWidget(self.right_view_stack, 1)
        content_layout.addWidget(self.right_widget, 2)     

        main_layout.addLayout(content_layout, stretch = 1)

        #handlers
        self.day_view.daily_view_closed.connect(self.restore_size)

        self.adjustSize()
    
    # ----------------------- windows change function -----------------------------

    def toggle_weekly_monthly(self):
        if self.calendar_view == "month":
            #self.weekly_view.update_date_and_events(QDate.currentDate(), "week", "all")
            week_start = QDate.currentDate().addDays(-(QDate.currentDate().dayOfWeek() % 7))
            self.new_weekly_view.calendar_view.show_week(week_start.toPython())

            self.calendar_stack.setCurrentIndex(2)
            self.top_bar.calendar_switch_act.setText("Switch to Month View")
            self.calendar_view = "week"

            self.new_weekly_view.setFocus()
            #self.right_widget.resize(1200,700)
        else:
            self.calendar_stack.setCurrentIndex(0)
            self.top_bar.calendar_switch_act.setText("Switch to Week View")
            self.calendar_view = "month"
            #self.right_widget.resize(600, 700)

        #self.resize(self.right_widget.width(), 700)

    def switch_to_calendars(self):
        self.right_view_stack.setCurrentIndex(0)
        self.top_bar.calendar_switch_act.setEnabled(True)
        self._resize_to_current()

    def switch_to_hw_track(self):
        self.right_view_stack.setCurrentIndex(1)
        self.top_bar.calendar_switch_act.setEnabled(False)
        self._resize_to_current()

    def switch_to_do_list(self):
        self.right_view_stack.setCurrentIndex(2)
        self.top_bar.calendar_switch_act.setEnabled(False)
        self._resize_to_current()

    def _resize_to_current(self):
        self.centralWidget().layout().activate()
        page = self.right_view_stack.currentWidget()
        #self.right_view_stack.setFixedSize(page.sizeHint())
        self.adjustSize()


    def open_daily_view(self, date: QDate):
        was_hidden = not self.day_view.isVisible()

        self.day_view.update_date(date)
        self.day_view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.day_view.setVisible(True)
        
        if was_hidden:
             self.resize(self.width() + self.day_view.daily_calendar.day_width, 700)
        #print(f"self.width(): {self.width()}, daily_calendar_width: {self.day_view.daily_calendar.day_width}")
        #self.resize(1200, 700)
    
    def restore_size(self):
        self.resize(600,700)

    def debug_method(self):
        print("Checking if the weekly_view is visible...")
        self.weekly_view.isVisible()