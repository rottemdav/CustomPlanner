from PySide6.QtWidgets import QMenuBar, QWidget, QMenu, QToolBar
from PySide6.QtGui import  QAction


class TopBar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)
        
        #switch to weekly-view button
        self.switch_action = QAction("Switch to Weekly View", self)
        self.switch_action.triggered.connect(parent.toggle_weekly_monthly)
        self.addAction(self.switch_action)

        #switch to submissions view
        self.hw_track = QAction("Homework Tracking")
        self.hw_track.triggered.connect(parent.switch_to_hw_track)
        self.addAction(self.hw_track)




