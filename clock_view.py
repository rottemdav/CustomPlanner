from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer, QTime, Qt
import sys

class ClockView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clock")

        #Qlabel where the time will be shown
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("font-size: 36px; font-family: Consolas;")
        self.clock_label.setAlignment(Qt.AlignCenter)

        #layout defining
        clock_layout = QVBoxLayout()
        clock_layout.addWidget(self.clock_label)
        self.setLayout(clock_layout)

        #time updating
        time = QTimer(self)
        time.timeout.connect(self.update_time)
        time.start(1000)
        self.update_time()

    def update_time(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.clock_label.setText(current_time)