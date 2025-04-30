from PySide6.QtWidgets import QMenuBar, QWidget, QMenu, QToolBar
from PySide6.QtGui import  QAction
from PySide6.QtCore import Signal


class TopBar(QToolBar):
    calendars_req = Signal()
    hw_track_req = Signal()
    todo_list_req = Signal()


    def __init__(self, parent):
        super().__init__(parent)
        
        #switch to weekly-view button
        self.calendar_switch_act = QAction("Switch to Weekly View", self)
        self.calendar_switch_act.triggered.connect(parent.toggle_weekly_monthly)
        self.addAction(self.calendar_switch_act)

        self.goto_calendaer = QAction("Calendars", self)
        self.goto_calendaer.triggered.connect(parent.switch_to_calendars)
        self.addAction(self.goto_calendaer)

        #switch to submissions view
        self.hw_track = QAction("Homework Tracking", self)
        self.hw_track.triggered.connect(parent.switch_to_hw_track)
        self.addAction(self.hw_track)

        #go to general todo list
        self.general_todo_list_switch = QAction("General To-Do List")
        self.general_todo_list_switch.triggered.connect(parent.switch_to_do_list)
        self.addAction(self.general_todo_list_switch)




