from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QTableWidget,
                                QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem
                                )
from PySide6.QtCore import Qt, QDate, QRectF, QDateTime
from PySide6.QtGui import QPen
from datetime import datetime, time, date, timedelta
from typing import List

#files import
from general_calendar import CalendarBase
from db_manager import AppDB

# ===========================================================================

class WeeklyView(QGraphicsView):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.db = db
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        #size
        self.day_width = 150
        self.minutes_scale = 0.5
        scene_width = self.day_width * 7
        scene_height = int(24*60*self.minutes_scale)
        self.scene.setSceneRect(0,0,scene_width, scene_height)

        #scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.show_week(date.today())

    def show_week(self, start_date):
        self.scene.clear()

        #7 days from today
        days = [(start_date + timedelta(days=i)) for i in range(7)]

        for day_index, day_date in enumerate(days):
            day_start_dt = datetime(day_date.year, day_date.month, day_date.day, 0, 0)
            day_end_dt   = datetime(day_date.year, day_date.month, day_date.day, 23, 59)

            start_str = day_start_dt.strftime("%Y-%m-%d %H:%M:%S")
            end_str   = day_end_dt.strftime("%Y-%m-%d %H:%M:%S")
            events = self.db.get_events_in_range(start_str, end_str)

            event_positions = self.layout_events_for_day(events)

            for e_pos in event_positions:
                self.add_event_item(day_index, e_pos)
        
        self.draw_guidelines()

    def layout_events_for_day(self, events):
        """
        Sort events by start time, then assign each event a 'column' if it overlaps 
        with existing ones in that column. Return a list of dicts:
            [
              { 'event': event_row, 'column': col_index, 'start_min': ..., 'duration_min': ... },
              ...
            ]
        Where 'event_row' is a DB row like (id, title, start_time, end_time, ...).
        """

        # Sort by start_time
        # events is a list of tuples like: (id, title, start_time, end_time, description, ...)
        sorted_events = sorted(events, key=lambda e: e[2])  # e[2] is start_time

        columns = []  # each element is a list of events that occupy that column
        result = []

        for evt in sorted_events:
            evt_start = evt[2]  # string 'YYYY-MM-DD HH:MM:SS'
            evt_end   = evt[3]
            s_min = self.to_minutes(evt_start)
            e_min = self.to_minutes(evt_end)
            duration = e_min - s_min

            # find a column that doesn't overlap
            placed_col = None
            for col_index, col_events in enumerate(columns):
                last_evt = col_events[-1]
                last_evt_end = self.to_minutes(last_evt[3])  # last event end_time
                # If the new event starts after or exactly at the last event's end, no overlap
                if s_min >= last_evt_end:
                    placed_col = col_index
                    col_events.append(evt)
                    break

            # if not placed, create a new column
            if placed_col is None:
                placed_col = len(columns)
                columns.append([evt])

            result.append({
                'event': evt,
                'column': placed_col,
                'start_min': s_min,
                'duration_min': duration
            })

        return result

    def add_event_item(self, day_index, e_pos):
        """
        Create and place a QGraphicsRectItem (plus optional text) in the scene 
        according to day_index, e_pos['column'], e_pos['start_min'], e_pos['duration_min'].
        """
        col_index = e_pos['column']
        y_pos = e_pos['start_min'] * self.minutes_scale
        height = e_pos['duration_min'] * self.minutes_scale

        # x-position = day_index * day_width + col_index*(some fraction of day_width)
        # Suppose each overlap column is 1/3 of the day_width, so max 3 overlaps side by side
        # or you can do day_width / (number_of_columns_in_that_day) 
        # but for simplicity, let's assume a fixed 70 px column width:
        column_width = 70  
        x_pos = day_index * self.day_width + col_index * column_width

        # if you want a max # of columns that can fit in day_width:
        # x_pos = day_index * self.day_width + (col_index * (self.day_width/4))  
        # etc.

        # The event data
        evt = e_pos['event']
        evt_id, evt_title, _, _, evt_desc, *rest = evt  # adapt to your columns

        # Create a rectangle to represent the event
        rect_item = QGraphicsRectItem(x_pos, y_pos, column_width, height)
        rect_item.setBrush(QBrush(QColor("#87CEFA")))  # example color
        rect_item.setPen(QPen(Qt.black, 1))

        self.scene.addItem(rect_item)

        # Add text label for the event title (and maybe time or location)
        text_item = QGraphicsSimpleTextItem(evt_title, parent=rect_item)
        text_item.setPos(x_pos + 5, y_pos + 5)  # slight offset so it’s inside
        # Optionally, set a smaller font if height is small, etc.

    def draw_guidelines(self):
        """
        Draw day boundaries and hour lines for better visual structure.
        """
        # Day boundaries:
        for d in range(8):  # 0..7
            x = d * self.day_width
            self.scene.addLine(x, 0, x, self.scene.height(), QPen(Qt.gray, 1, Qt.DotLine))

        # Hour lines (24 hours)
        for h in range(25):  # 0..24
            y = h * 60 * self.minutes_scale
            self.scene.addLine(0, y, self.scene.width(), y, QPen(Qt.lightGray, 0.5, Qt.DotLine))

    def to_minutes(self, dt_str):
        """
        Convert string 'YYYY-MM-DD HH:MM:SS' to integer minutes from midnight.
        """
        # parse the string
        dt_format = "%Y-%m-%d %H:%M:%S"
        dt = datetime.datetime.strptime(dt_str, dt_format)
        return dt.hour * 60 + dt.minute




