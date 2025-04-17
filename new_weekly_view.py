from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QTableWidget,
                                QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem,
                                QInputDialog, QLineEdit, QMenu
                                )
from PySide6.QtCore import Qt, QDate, QRectF, QDateTime, QPoint
from PySide6.QtGui import QPen, QBrush, QColor,  QAction
from datetime import datetime, time, date, timedelta
from typing import List
import traceback

#files import
from general_calendar import CalendarBase
from db_manager import AppDB

# ===========================================================================

class WeeklyViewContainer(QWidget):
    def __init__(self, db):
        super().__init__()

        self.calendar_view = WeeklyView(db)
        self.header_view = self.calendar_view.header_view

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        layout.addWidget(self.header_view)
        layout.addWidget(self.calendar_view)

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

        #mouse tracking variables
        self.drag_start_pos = None
        self.selection_rect_item = None
        self.drag_distance_threashould = 5

        #create the headers scene
        self.header_scene = QGraphicsScene()
        self.header_view = QGraphicsView(self.header_scene)
        self.header_view.setFixedHeight(50)
        self.header_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.header_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.header_view.setStyleSheet("border: none; background: white;")

        #scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.horizontalScrollBar().valueChanged.connect(
        self.header_view.horizontalScrollBar().setValue
        )

        #coordinates
        self.scene_top_left = self.mapToScene(0,0)

        self.show_week(date.today())

# ==================== display methods ============================

    def show_week(self, start_date):
        self.scene.clear()

        self.start_date = start_date

        self.add_day_headers(start_date, self.header_scene)
        #self.add_day_headers(start_date, self.scene)

        self.add_hours_markers()

        #7 days from today
        days = [(start_date + timedelta(days=i)) for i in range(7)]

        for day_index, day_date in enumerate(days):
            day_start_dt = datetime(day_date.year, day_date.month, day_date.day, 0, 0)
            day_end_dt   = datetime(day_date.year, day_date.month, day_date.day, 23, 59)

            start_str = day_start_dt.strftime("%Y-%m-%d %H:%M:%S")
            end_str   = day_end_dt.strftime("%Y-%m-%d %H:%M:%S")
            events = self.db.get_events_in_range(start_str, end_str)

            event_positions = self.layout_events_for_day(events)

            display_index = 6 - day_index 
            #print(f"display index: {display_index}, event_positions: {event_positions}")


            for e_pos in event_positions:
                self.add_event_item(display_index, e_pos)
        
        self.draw_guidelines()

    def add_day_headers(self, start_date, scene):
        print(f" [LOG] - Creating calendar headers for the start_date: {start_date}...")
        scene.clear()
        #traceback.print_stack(limit=5)
        header_height=50
        scene_width = self.day_width * 7
        scene_height = int(24*60*self.minutes_scale) + header_height

        scene.setSceneRect(0,0, scene_width, header_height)

#        self.scene.setSceneRect(0, -header_height, scene_width, scene_height)

        for i in range(7):
            #format text
            current_date = start_date + timedelta(days=i)
            day_name = current_date.strftime("%A")
            date_str = current_date.strftime("%d/%m") #formmated as dd/mm
            header_text = f"{day_name}\n{date_str}"

            #reverved the placement order
            display_index = 6 - i

            #create the object
            header_item = QGraphicsSimpleTextItem(header_text)

            #get the object of the rectangle
            text_rect_obj = header_item.boundingRect()
            
            #calcualte the center
            x_center = display_index * self.day_width + (self.day_width - text_rect_obj.width()) / 2
            y_center = (header_height - text_rect_obj.height()) / 2
            
            header_item.setPos(x_center, y_center)
            header_item.setData(0,"header")
            scene.addItem(header_item)

            header_margin = QGraphicsRectItem(display_index * self.day_width, 0,
                                              self.day_width,header_height)
            header_margin.setPen(QPen(Qt.black, 1))
            scene.addItem(header_margin)

    def add_hours_markers(self):
        for hour in range(24):
            hour_text = f"{hour:02d}:00"
            hour_label = QGraphicsSimpleTextItem(hour_text)

            y_pos = hour * 60 * self.minutes_scale
            hour_label.setPos(self.scene.sceneRect().width() + 5, y_pos - 5)
            self.scene.addItem(hour_label)

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
        #print(f"sorted_events: {sorted_events}")

        columns = []  # each element is a list of events that occupy that column
        result = []

        for evt in sorted_events:
            print(f"event: {evt}, evt[2]: {evt[2]}, evt[3]: {evt[3]}")
            evt_start = evt[4]  # string 'YYYY-MM-DD HH:MM:SS'
            evt_end   = evt[5]
            s_min = self.to_minutes(evt_start)
            e_min = self.to_minutes(evt_end)
            duration = e_min - s_min

            # find a column that doesn't overlap
            placed_col = None
            for col_index, col_events in enumerate(columns):
                last_evt = col_events[-1]
                last_evt_end = self.to_minutes(last_evt[5])  # last event end_time
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
        rect = QRectF(x_pos, y_pos, column_width, height)
        rect_item = EventBlock(rect, evt_id, self.db)
        #rect_item.setBrush(QBrush(QColor("#87CEFA")))  # example color
        #rect_item.setPen(QPen(Qt.black, 1))

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
            self.scene.addLine(x, 0, x, self.scene.height(), QPen(Qt.gray, 1))

        # Hour lines (24 hours)
        for h in range(25):  # 0..24
            y = h * 60 * self.minutes_scale
            self.scene.addLine(0, y, self.scene.width(), y, QPen(Qt.lightGray, 0.5))

    def to_minutes(self, dt_str):
        """
        Convert string 'YYYY-MM-DD HH:MM:SS' to integer minutes from midnight.
        """
        # parse the string
        dt_format = "%Y-%m-%d %H:%M:%S"
        dt = datetime.strptime(dt_str, dt_format)
        return dt.hour * 60 + dt.minute

# ===================== interactive functionalities ============================

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        first_column_x = self.mapToScene(self.viewport().rect().topLeft()).x()
        normalized_x = scene_pos.x() + first_column_x

        if event.button() == Qt.LeftButton:
            print(" [LOG] left-mouse click detected! ")
            if scene_pos.y() >= 0 and (normalized_x >= 0 and normalized_x <= (7 * self.day_width)):
                self.drag_start_pos = event.pos() #save the current coordinates of the click

                # day_index = int(scene_pos.x() / self.day_width)

                # #correction for the right-to-left layout
                # rtl_day_index = 6 - day_index

                # minutes = int(scene_pos.y() / self.minutes_scale)
                # hour = minutes // 60
                # minute = minutes % 60

                # clicked_date = self.start_date + timedelta(days=rtl_day_index)

                # self.create_new_event(clicked_date, hour, 00)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_start_pos:
            release_pos = event.pos()
            drag_distance = (release_pos - self.drag_start_pos).manhattanLength()
            print(f"drag click distance: {drag_distance}")

            if drag_distance < self.drag_distance_threashould:
                #single click identified
                scene_pos = self.mapToScene(release_pos)
                self.handle_single_click(scene_pos)

            if drag_distance > self.drag_distance_threashould:
                #span click identified
                scene_end_pos = self.mapToScene(release_pos)
                self.handle_span_click(scene_end_pos)

            if self.selection_rect_item:
                try:
                    self.scene.removeItem(self.selection_rect_item)
                except RuntimeError as e:
                    print(f" [WARN] Selection rect already deleted: {e}")
                self.selection_rect_item = None

            self.drag_start_pos = None


        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.drag_start_pos:
            current_pos = self.mapToScene(event.pos())

            x = self.drag_start_pos.x()
            y_start = min(self.drag_start_pos.y(), current_pos.y())
            y_end =  max(self.drag_start_pos.y(), current_pos.y())

            first_column_x = self.mapToScene(self.viewport().rect().topLeft()).x()
            normalized_x = x + first_column_x
            day_index = int(( normalized_x )/ self.day_width)
            #print(f"norm_x: {x + first_column_x}, self.day_widht: {self.day_width} day index: {day_index}")
            truncated_x = day_index * self.day_width
            
            if self.selection_rect_item:
                try:
                    self.scene.removeItem(self.selection_rect_item)
                except RuntimeError as e:
                    print(f" [WARN] Selection rect already deleted: {e}")

            #draw new rectangle
            if normalized_x > 0 and normalized_x < 7 * self.day_width:
                rect = QRectF(truncated_x, y_start, self.day_width, y_end - y_start)
                self.selection_rect_item = QGraphicsRectItem(rect)
                self.selection_rect_item.setBrush(QBrush(QColor(211,211,211,80)))
                self.selection_rect_item.setPen(QPen(Qt.lightGray, 1))
                self.scene.addItem(self.selection_rect_item)

        return super().mouseMoveEvent(event)
    # =========================== handlers methods ===============================

    def handle_single_click(self, scene_pos):
        day_index = int(scene_pos.x() / self.day_width)
        if day_index > 6:
            return

        #correction for the right-to-left layout
        rtl_day_index = 6 - day_index

        minutes = int(scene_pos.x() / self.day_width)
        hour = minutes // 60
        minute = minutes % 60

        clicked_date = self.start_date + timedelta(days=rtl_day_index)

        self.create_new_event(clicked_date, hour, hour+1, 0)

    def handle_span_click(self, scene_end_pos):
        day_index = int(scene_end_pos.x() / self.day_width)
        if day_index > 6:
            return

        #correction for the right-to-left layout
        rtl_day_index = 6 - day_index

        start_minutes = int(min(self.drag_start_pos.y(), scene_end_pos.y())/ self.minutes_scale)
        end_minutes = int(max(self.drag_start_pos.y(), scene_end_pos.y())/ self.minutes_scale)
        start_hour = start_minutes // 60
        end_hour = end_minutes // 60
        start_minute = start_minutes % 60
        end_minute = end_minutes % 60
        
        clicked_date = self.start_date + timedelta(days =rtl_day_index)

        self.create_new_event(clicked_date, start_hour, end_hour, 0)

    # =========================== data methods ===================================

    def create_new_event(self, event_date, start_hour, end_hour,  minute):
        start_dt = datetime(event_date.year, event_date.month, event_date.day, start_hour, minute)
        end_dt = datetime(event_date.year, event_date.month, event_date.day, end_hour, minute)

        if (end_hour - start_hour <= 1):
            title, ok = QInputDialog.getText(self, "New Event", f"Create Event on: {event_date.strftime('%d/%m')} at {start_hour:02d}:{minute:02d}",
                                            QLineEdit.Normal, "")
        else:
            title, ok = QInputDialog.getText(self, "New Event", 
                                             f"Create Event on: {event_date.strftime('%d/%m')} from {start_hour:02d}:{minute:02d} to {end_hour:02d}:{minute:02d}",
                                            QLineEdit.Normal, 
                                            "")
        
        if ok and title:

            start_dt_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
            end_dt_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
            event_date = event_date.strftime("%Y-%m-%d")

            self.db.add_calendar_event(title, event_date, "", start_dt_str, end_dt_str, "","","", QDate.currentDate())

            self.show_week(self.start_date)


class EventBlock(QGraphicsRectItem):
    def __init__(self, rect, event_id, db, parent=None):
        super().__init__(rect, parent)

        self.event_id = event_id
        self.db = db
        self.setBrush(Qt.lightGray)
        self.setPen(QPen(Qt.black, 1))
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setAcceptHoverEvents

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = QAction("Delete", menu)
        menu.addAction(delete_action)

        selected_action = menu.exec(event.screenPos())
        if selected_action == delete_action:
            print(f" [LOG] - Deleting event {self.event_id}")
            self.db.remove_calendar_event(self.event_id)
            self.scene().removeItem(self)

        return super().contextMenuEvent(event)