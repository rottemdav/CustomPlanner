from PySide6.QtWidgets import (
                                QApplication
                               )
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QIcon

#project files import
from main_window import MainWindow
from db_manager import init_db
import sys

if __name__ == "__main__":          
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/app_icon.ico"))

    init_db()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
