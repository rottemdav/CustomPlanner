from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QTableWidget,
                                QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem)
from PySide6.QtCore import Qt, QDate, QRectF, QDateTime
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
            button.setChecked(True)
            button.stateChanged.connect(self.reload_after_selection_change)
            self.layers_layout.addWidget(button)
            self.layers_buttons.append(button)

        self.calendar_table.scrollToItem(
            self.calendar_table.item(8,0),
            QTableWidget.PositionAtTop
        )

    #style
        self.calendar_table.horizontalHeader().setStretchLastSection(True)
        self.calendar_table.verticalHeader().setDefaultSectionSize(32)

        self.main_layout.addLayout(self.layers_layout)
        self.main_layout.addWidget(self.calendar_table)

    def reload_after_selection_change(self):
        print(" [LOG] Selection Changed. Fecthing events by current checked layers..")
            
        self.clear_calendar()
        self.selected_layers = [layer.text() for layer in self.layers_buttons if layer.isChecked()]

        print(f" [LOG] Selected layers: {self.selected_layers}")

        if not self.selected_layers:
            return
        
        for layer in self.selected_layers:
            print(f" [LOG] Fetching event from layer {layer}. ")
            self.load_event_by_week(self.week_start_date, layer)

# ===========================================================================

class WeeklyView(QGraphicsView):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.db = db
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        #size
        self.day_width = 150
        self.minutes = 0.5
        scene_width = self.day_width * 7
        scene_height = int(24*60*self.minutes_scale)
        self.scene.setSceneRect(0,0,scene_width, scene_height)

        #scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.show_week(datetime.date.today())

    def show_week(self, start_date):
        self.scene.clear()

        #7 days from today
        days = [start_date + datetime.timedelta(days=i) for i in range(7)]

        for day_index, day_date in enumerate(days):
            day_start_dt = datetime.datetime(day_date.year, day_date.month, day_date.day, 0, 0)
            day_end_dt   = datetime.datetime(day_date.year, day_date.month, day_date.day, 23, 59)

            start_str = day_start_dt.strftime("%Y-%m-%d %H:%M:%S")
            end_str   = day_end_dt.strftime("%Y-%m-%d %H:%M:%S")
            events = self.db.get_events_in_range(start_str, end_str)

            event_positions = self.layout_events_for_day(events)

            for e_pos in event_positions:
                self.add_event_item(day_index, e_pos)
        
        self.draw_guidelines()
