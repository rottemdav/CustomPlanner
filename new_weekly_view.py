from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QTableWidget,
                                QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem,
                                QGraphicsTextItem,
                                QInputDialog, QLineEdit, QMenu, QSpacerItem, QSizePolicy, QLabel,
                                QComboBox, QPushButton,QDialog
                                )
from PySide6.QtCore import Qt, QDate, QRectF, QDateTime, QPoint
from PySide6.QtGui import QPen, QBrush, QColor,  QAction, QTextOption
from datetime import datetime, time, date, timedelta
from typing import List
import traceback

#files import
from general_calendar import CalendarBase
from db_manager import AppDB
from constants import COLORS_PALETTE, LAYERS_COLORS


# ===========================================================================

class WeeklyViewContainer(QWidget):
    def __init__(self, db):
        super().__init__()

        self.calendar_view = WeeklyView(db)
        self.header_view = self.calendar_view.header_view

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        #categories widget
        self.layers_widget = QWidget()
        self.layers_filter = QHBoxLayout(self.layers_widget)
        self.layers_filter.setAlignment(Qt.AlignCenter)
        self.layers_filter.setContentsMargins(0,0,0,0)
        self.layers_buttons = {}
        self.create_layers_buttons()

        layout.addWidget(self.layers_widget)
        layout.addSpacerItem(QSpacerItem(0,10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.header_view)
        layout.addWidget(self.calendar_view)

    def create_layers_buttons(self):
        for layer_name, color in LAYERS_COLORS.items():
            #print(f"layer: {layer_name}, color: {color}")
            button = QCheckBox(layer_name)
            button.setLayoutDirection(Qt.RightToLeft)
            button.setChecked(True)
            button.setStyleSheet(f"background-color: {COLORS_PALETTE[color]}; padding: 4px;")
            #button.stateChanged.connect(self.calendar_view.show_week()) --> check the calendar functions
            self.layers_filter.addWidget(button)
            self.layers_buttons[layer_name] = button

    def get_active_layers(self):
        active_layers = [ layer for layer, button in self.layers_buttons.item() if button.isChecked()]
        self.calendar_view.filter_layers(active_layers)

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

        self.centerOn(0, 8 *60 * self.minutes_scale)
        self.ensureVisible(0,25*60*self.minutes_scale,1,1)

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
        #print(f"[LOG] - Creating calendar headers for the start_date: {start_date}...")
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
        **IMPORTANT** - The events already exist in the DB - the newest event is already in the DB.
        This function is being called for each day separetaly!
        Sort events by start time, then assign each event a 'column' if it overlaps 
        """
        # Sort by start_time
        # events is a list of tuples like: (id, title, start_time, end_time, description, ...)
        sorted_events = sorted(events, key=lambda e: (e[4], e[5]))  # e[4] is start_time
        print(f"sorted_events: {sorted_events}") if sorted_events else None

        columns = []  # each element is a list of events that occupy that column
        result = []

        for evt in sorted_events:
            print(f"[PLACE EVENTS - LOG] Checking overlapping for event: {evt[0]}")
            #print(f"event: {evt}, evt[2]: {evt[2]}, evt[3]: {evt[3]}")
            partition = 1
            overlap_event_ids = []
            evt_start = evt[4]  # string 'YYYY-MM-DD HH:MM:SS'
            evt_end   = evt[5]
            s_min = self.to_minutes(evt_start)
            e_min = self.to_minutes(evt_end)
            duration = e_min - s_min

            # find a column that doesn't overlap
            placed_col = None
            last_evt = None
            for col_index, col_events in enumerate(columns):
                last_evt = col_events[-1]
                print(f"[OVERLAP-LOG] col index: {col_index}, last_evt: {last_evt}")
                last_evt_end = self.to_minutes(last_evt[5])  # last event end_time
                # If the new event starts after or exactly at the last event's end, no overlap
                #print(f"[OVERLAP-LOG] s_min: {s_min}, last_evt_end: {last_evt_end}")
                if s_min >= last_evt_end:
                    placed_col = col_index
                    col_events.append(evt)
                    break

            # if not placed, create a new column
            if placed_col is None:
                placed_col = len(columns)
                columns.append([evt])
                if last_evt:
                    for r in result:
                        if r["event"][0] == last_evt[0]:
                            r["partition"] = r["partition"]+1
                            partition = r["partition"]

                            #overlap_event_ids.append(list((r.get("overlap_ids"),[]))) #add the already interescted event to the concurrent list
                            overlap_event_ids.extend(r["overlap_ids"]) if r["overlap_ids"] else None #add the already interescted event to the concurrent list                            
                            #print(f"[OVERLAP-LOG] overlapping events: {overlap_event_ids}")
                            break
                    
                    overlap_event_ids.append(last_evt[0]) # add the previous event_id to a list so the size will be updated
                    #print(f"[OVERLAP-LOG] overlapping events: {overlap_event_ids}, last_evt: {last_evt[0]}")
                            
                    

            result.append({
                'event': evt,
                'column': placed_col,
                'start_min': s_min,
                'duration_min': duration,
                'partition': partition,
                'overlap_ids': overlap_event_ids
            })
            
            #print(f"[PLACE EVENT - LOG] Result last append: {result[-1]}")

        #print(f" [layout_events_for_day] - result: {result}")
        return result

    def add_event_item(self, day_index, e_pos):
        """
        Create and place a QGraphicsRectItem (plus optional text) in the scene 
        according to day_index, e_pos['column'], e_pos['start_min'], e_pos['duration_min'].
        """
        col_index = e_pos['column']
        y_pos = e_pos['start_min'] * self.minutes_scale
        height = e_pos['duration_min'] * self.minutes_scale
        partition = e_pos['partition']
        overlap_ids = e_pos['overlap_ids']

        # x-position = day_index * day_width + col_index*(some fraction of day_width)
        
        column_width = self.day_width / (partition) # if col_index = 0 -> day_width / 1 
        x_pos = day_index * self.day_width + col_index * column_width

        if (partition > 1): #theres overlapping events and adjustments need to be made
            self.change_overlapping_events_pos(day_index, overlap_ids, column_width)

        # max number of cols that can fit in day_width: x_pos = day_index * self.day_width + (col_index * (self.day_width/4))  
        # The event data
        evt = e_pos['event']
        evt_id, evt_title, event_desc, _, _, _, event_layer, *rest = evt  # adapt to your columns
        #print(f"evt: {evt}")
        #print(f"evt_id: {evt_id}, evt_title: {evt_title}, event_desc: {event_desc}, event_layer: {event_layer}")

        # Create a rectangle to represent the event
        rect = QRectF(x_pos, y_pos, column_width, height)
        rect_item = EventBlock(rect, evt_id, evt_title, event_layer, self.db)

        #move the adding to the DB to here
        
        self.scene.addItem(rect_item)

        # Add text label for the event title (and maybe time or location)
        # text_item = QGraphicsTextItem(evt_title, parent=rect_item)
        # text_item.setTextWidth(column_width)
        # text_item.setPos(x_pos + 5, y_pos + 5)  # slight offset so it’s inside

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

    def filter_layers(self, active_layers: list[str]):
        for event in self.scene.item():
            if isinstance(event, EventBlock):
                event.setVisible(event.layer in active_layers)

    def change_overlapping_events_pos(self, day_index: int, overlap_ids: list[str], new_col_width: float):

        for i, e_id in enumerate(overlap_ids):
            new_x = day_index * self.day_width + i * new_col_width

            for event in self.scene.items():
                if hasattr(event, "event_id") and event.event_id == e_id:
                    rect = event.rect()
                    new_rect = QRectF(new_x, rect.y(), new_col_width, rect.height())
                    #print(f"event_id: {e_id}, new_x: {new_x}, new_col_width: {new_col_width}")
                    event.setRect(new_rect)
                    break #found the overlap event, advance to the next one

# ========================= interactive functionalities ============================

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        first_column_x = self.mapToScene(self.viewport().rect().topLeft()).x()
        normalized_x = scene_pos.x() + first_column_x

        if event.button() == Qt.LeftButton:
            print("[LOG] left-mouse click detected! ")
            if scene_pos.y() >= 0 and (normalized_x >= 0 and normalized_x <= (7 * self.day_width)):
                self.drag_start_pos = event.pos() #save the current coordinates of the click

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_start_pos:
            release_pos = event.pos()
            drag_distance = (release_pos - self.drag_start_pos).manhattanLength()
           #print(f"drag click distance: {drag_distance}")

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
            start_pos = self.mapToScene(self.drag_start_pos)
            current_pos = self.mapToScene(event.pos())

            x = start_pos.x()
            y_start = min(start_pos.y(), current_pos.y())
            y_end =  max(start_pos.y(), current_pos.y())

            first_column_x = self.mapToScene(self.viewport().rect().topLeft()).x()
            normalized_x = x
            day_index = int(( normalized_x )/ self.day_width)
            #rint(f"norm_x: {normalized_x}, self.day_widht: {self.day_width} day index: {day_index}")
            #print(f"y_start: {y_start}, current_pos_y: {current_pos.y()}, drag_start_pos_y: {self.drag_start_pos.y()}")
            truncated_x = day_index * self.day_width
            
            minutes_start = int(y_start / self.minutes_scale)
            rounded_minutes_start = (minutes_start // 30) * 30
            truncated_y_start = rounded_minutes_start * self.minutes_scale
            
            minutes_end = int(y_end / self.minutes_scale)
            rounded_minutes_end = ((minutes_end + 29) // 30) * 30
            truncated_y_end = rounded_minutes_end * self.minutes_scale
            

            if self.selection_rect_item:
                try:
                    self.scene.removeItem(self.selection_rect_item)
                except RuntimeError as e:
                    print(f" [WARN] Selection rect already deleted: {e}")

            #draw new rectangle
            if normalized_x > 0 and normalized_x < 7 * self.day_width:
                rect = QRectF(truncated_x, truncated_y_start, self.day_width, truncated_y_end - truncated_y_start)
                self.selection_rect_item = QGraphicsRectItem(rect)
                self.selection_rect_item.setBrush(QBrush(QColor(211,211,211,80)))
                self.selection_rect_item.setPen(QPen(Qt.lightGray, 1))
                self.scene.addItem(self.selection_rect_item)

        return super().mouseMoveEvent(event)
  
# ================================= handlers methods ===============================

    def handle_single_click(self, scene_pos):
        day_index = int(scene_pos.x() / self.day_width)
        if day_index > 6:
            return

        #correction for the right-to-left layout
        rtl_day_index = 6 - day_index

        minutes = int(scene_pos.x() / self.day_width)
        hour = minutes // 30
        minute = round((minutes % 60) / 30) * 30

        clicked_date = self.start_date + timedelta(days=rtl_day_index)

        self.create_new_event(clicked_date, hour, hour+1, minute, minute)

    def handle_span_click(self, scene_end_pos):
        day_index = int(scene_end_pos.x() / self.day_width)
        if day_index > 6:
            return

        #correction for the right-to-left layout
        rtl_day_index = 6 - day_index
        calibrated_start_pos = self.mapToScene(self.drag_start_pos)
        start_minutes = int(min(calibrated_start_pos.y(), scene_end_pos.y())/ self.minutes_scale)
        end_minutes = int(max(calibrated_start_pos.y(), scene_end_pos.y())/ self.minutes_scale)
        start_hour = start_minutes // 60
        end_hour = end_minutes // 60
        start_minute = round((start_minutes % 60) / 30 ) * 30
        end_minute = round((end_minutes % 60) / 30 ) * 30

        print(f"start_minutes: {start_minutes}, end_minutes: {end_minutes}, start_hour: {start_hour}, end_hour: {end_hour}")
        
        clicked_date = self.start_date + timedelta(days =rtl_day_index)

        self.create_new_event(clicked_date, start_hour, end_hour, start_minute, end_minute)

# ================================= data methods ===================================

    def create_new_event(self, event_date, start_hour, end_hour, start_minute, end_minute):
        start_dt = datetime(event_date.year, event_date.month, event_date.day, start_hour, start_minute)
        end_dt = datetime(event_date.year, event_date.month, event_date.day, end_hour, end_minute)
        time_range_for_text = f"{end_dt.strftime('%H:%M')} - {start_dt.strftime('%H:%M %d/%m/%Y ')}"
        time_range = f"{start_dt.strftime('%d/%m/%Y %H:%M')} - {end_dt.strftime('%d/%m/%Y %H:%M')}"

        new_event_dialog = CustomEventDialog(time_range,time_range_for_text, self)
        if new_event_dialog.exec() == QDialog.Accepted:
            title,layer = new_event_dialog.get_data()
            if title:
                start_dt_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
                end_dt_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                event_date = event_date.strftime("%Y-%m-%d")
                self.db.add_calendar_event(title, event_date, "", start_dt_str, end_dt_str, layer,"","", QDate.currentDate())

                self.show_week(self.start_date)

class EventBlock(QGraphicsRectItem):
    def __init__(self, rect, event_id, title, layer, db, parent=None):
        super().__init__(rect, parent)

        self.event_id = event_id
        self.event_title = title
        self.db = db
        self.layer = layer

        fallback_layer = LAYERS_COLORS.get(self.layer, "grey")
        # example - rect_item.setBrush(QBrush(QColor("#87CEFA")))  # example color
        self.setBrush(QBrush(QColor(COLORS_PALETTE[fallback_layer])))
        self.setPen(QPen(Qt.black, 1))
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        #create the title
        self.title_item = QGraphicsTextItem(self.event_title, self)
        self.title_item.setTextWidth(rect.width() - 4 )
        self.title_item.setDefaultTextColor(Qt.black)
        self.title_item.setPos(rect.x() +2, rect.y() + 2)
        
        #align center
        title_option = QTextOption()
        title_option.setAlignment(Qt.AlignCenter)
        self.title_item.document().setDefaultTextOption(title_option)


    def contextMenuEvent(self, event):
        menu = QMenu()
        #delete action
        delete_action = QAction("Delete", menu)
        menu.addAction(delete_action)

        #change layer sub-menu
        change_layer_menu = menu.addMenu("Change Category")
        layer_options = {}
        for layer_name in LAYERS_COLORS.keys():
            change_layer_action = QAction(layer_name, change_layer_menu)
            change_layer_menu.addAction(change_layer_action)
            layer_options[change_layer_action] = layer_name #map action to its layer

        selected_action = menu.exec(event.screenPos())
        if selected_action == delete_action:
            print(f"[LOG] - Deleting event {self.event_id}")
            self.db.remove_calendar_event(self.event_id)
            self.scene().removeItem(self)
        
        elif selected_action in layer_options:
            new_layer = layer_options[selected_action]
            print(f"[EVENT LOG] - Changing layer of event with id: {self.event_id} to '{new_layer}")
            self.layer = new_layer

            color = COLORS_PALETTE.get(LAYERS_COLORS.get(new_layer, "grey"), "#E0E0E0")
            self.setBrush(QBrush(QColor(color)))

            self.db.update_event_layer(self.event_id, new_layer)

        return super().contextMenuEvent(event)
    
class CustomEventDialog(QDialog):
    def __init__(self, time_str, time_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("אירוע חדש")
        
        layout = QVBoxLayout(self)

        #event title
        self.event_title = QLineEdit()
        self.event_title.setPlaceholderText("הוספת שם")
        
        layout.addWidget(QLabel(f"זמן: {time_text}"))
        layout.addWidget(self.event_title)

        self.layer_select = QComboBox()
        self.layer_select.addItems(LAYERS_COLORS.keys())
        self.layer_select.setLayoutDirection(Qt.RightToLeft)
        
        layout.addWidget(QLabel("קטגוריה:"))
        layout.addWidget(self.layer_select)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("יצירה")
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("ביטול")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFocusPolicy(Qt.NoFocus)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)

    def get_data(self):
        return self.event_title.text().strip(), self.layer_select.currentText()