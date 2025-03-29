from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt

class WeeklyView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weekly Planner")
        
        layout = QVBoxLayout(self)

        #create the table
        self.table = QTableWidget(5,7)

        #define layout to be right-to-left
        self.table.setLayoutDirection(Qt.RightToLeft)

        self.table.setHorizontalHeaderLabels(["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"])
        #self.table.setVerticalHeaderLabels(f"{h:02d}:00" for h in range(6,25))
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.table.verticalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)


        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

        layout.addWidget(self.table)