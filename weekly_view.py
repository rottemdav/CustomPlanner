from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QHBoxLayout
from PySide6.QtCore import Qt, QDate
from datetime import datetime, time
from typing import List

#files import
from general_calendar import CalendarBase
from db_manager import AppDB


class WeeklyCalendarView(CalendarBase):
    def __init__(self , date: QDate, db:AppDB, rows: int = 24, parent: QWidget | None = None) -> None:
        week_start = date.addDays(-date.dayOfWeek())
        print(f"week start: {week_start}")
        self.week_start_date = week_start
        headers: List[str] = [ 
            week_start.addDays(i).toString("ddd dd/MM")
            for i in range (7)
        ]

        layers = ["אישי", "לימודים"]

        super().__init__(
            date=week_start,
            db=db,
            rows=rows,
            cols=7,
            headers=headers,
            layers=layers,
            parent=parent
        )

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.layers_layout = QHBoxLayout()
        self.layers_layout.setAlignment(Qt.AlignCenter)
        self.layers_buttons = []

        for layer_name in self.layers:
            button = QCheckBox(layer_name)
            button.setLayoutDirection(Qt.RightToLeft)
            button.stateChanged.connect(self.reload_after_selection_change)
            self.layers_layout.addWidget(button)
            self.layers_buttons.append(button)
            

        self.selected_layers = []

    #style
        self.calendar_table.horizontalHeader().setStretchLastSection(True)
        self.calendar_table.verticalHeader().setDefaultSectionSize(32)

        self.main_layout.addLayout(self.layers_layout)
        self.main_layout.addWidget(self.calendar_table)

    def reload_after_selection_change(self):
        print(" [LOG] Selection Changed. Fecthing events by current checked layers..")
        self.selected_layers = [layer.text() for layer in self.layers_buttons if layer.isChecked()]
        if not self.selected_layers:
            return
        
        for layer in self.selected_layers:
            print(f" [LOG] Fetching event from layer {layer}. ")
            self.load_event_by_week(self.week_start_date, layer)

