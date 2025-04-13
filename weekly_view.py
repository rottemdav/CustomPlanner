from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, QDate
from datetime import datetime, time
from typing import List

#files import
from general_calendar import CalendarBase
from db_manager import AppDB


class WeeklyCalendarView(CalendarBase):
    def __init__(self , date: QDate, db:AppDB, rows: int = 24, parent: QWidget | None = None) -> None:
        week_start = date.addDays(-date.dayOfWeek()%7)
        self.week_start_date = week_start
        headers: List[str] = [ 
            week_start.addDays(i).toString("ddd dd/MM")
            for i in range (7)
        ]

        super().__init__(
            date=week_start,
            db=db,
            rows=rows,
            cols=7,
            headers=headers,
            parent=parent
        )

        self.calendar_table.horizontalHeader().setStretchLastSection(True)
        self.calendar_table.verticalHeader().setDefaultSectionSize(32)

