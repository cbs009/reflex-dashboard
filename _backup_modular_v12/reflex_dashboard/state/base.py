import reflex as rx
import pandas as pd
import datetime
import calendar

class BaseState(rx.State):
    """Core state variables and basic UI state."""
    # Raw Data
    _df: pd.DataFrame = pd.DataFrame()
    _courier_df: pd.DataFrame = pd.DataFrame()
    
    # Filter Options
    months: list[str] = []
    states: list[str] = []
    brands: list[str] = []
    channels: list[str] = []
    supply_types: list[str] = []
    
    # Selected Filters
    selected_months: list[str] = []
    selected_states: list[str] = []
    selected_brands: list[str] = []
    selected_channels: list[str] = []
    selected_supply_types: list[str] = []
    
    # Date Range Filter
    start_date: str = ""
    end_date: str = ""

    # Sidebar State
    is_sidebar_open: bool = True
    
    # Debug / Deployment Status
    deployment_status: str = ""
    
    # Upload State
    is_upload_modal_open: bool = True
    sales_data_uploaded: bool = False
    courier_data_uploaded: bool = False

    # --- Custom Date Picker State ---
    show_picker: bool = False
    picker_target: str = "start" # "start" or "end"
    picker_view_date: str = "" # The month we are looking at
    picker_temp_date: str = "" # The date currently selected in the picker (before OK)

    def set_start_date(self, val: str):
        self.start_date = val
        
    def set_end_date(self, val: str):
        self.end_date = val

    def toggle_sidebar(self):
        self.is_sidebar_open = not self.is_sidebar_open

    def open_picker(self, target: str):
        self.picker_target = target
        current_val = self.start_date if target == "start" else self.end_date
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        if current_val:
            self.picker_view_date = current_val
            self.picker_temp_date = current_val
        else:
            self.picker_view_date = today_str
            self.picker_temp_date = today_str
        self.show_picker = True

    def close_picker(self):
        self.show_picker = False

    def picker_prev_month(self):
        try:
            dt = datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d")
            first = dt.replace(day=1)
            prev = first - datetime.timedelta(days=1)
            self.picker_view_date = prev.strftime("%Y-%m-%d")
        except:
             pass

    def picker_next_month(self):
        try:
            dt = datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d")
            days_in_month = calendar.monthrange(dt.year, dt.month)[1]
            next_month = dt + datetime.timedelta(days=days_in_month)
            self.picker_view_date = next_month.replace(day=1).strftime("%Y-%m-%d")
        except:
            pass
    
    def picker_select_date(self, date_str: str):
        self.picker_temp_date = date_str

    def picker_confirm(self):
        if self.picker_target == "start":
            self.set_start_date(self.picker_temp_date)
        else:
            self.set_end_date(self.picker_temp_date)
        self.show_picker = False

    @rx.var
    def picker_calendar_grid(self) -> list[dict]:
        if not self.picker_view_date: return []
        try:
            dt = datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d")
            year = dt.year
            month = dt.month
            c = calendar.Calendar(firstweekday=6)
            grid = []
            for date_obj in c.itermonthdates(year, month):
                is_current_month = (date_obj.month == month)
                date_str = date_obj.strftime("%Y-%m-%d")
                grid.append({
                    "day": date_obj.day,
                    "date_str": date_str,
                    "is_current_month": is_current_month,
                    "is_selected": (date_str == self.picker_temp_date),
                })
            return grid
        except:
            return []
        
    @rx.var
    def picker_display_year(self) -> str:
        if not self.picker_temp_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%Y") 
        except:
            return ""

    @rx.var
    def picker_display_date_formatted(self) -> str:
        if not self.picker_temp_date: return "Select date"
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%a, %b %d")
        except:
            return "Select date"

    @rx.var
    def picker_display_weekday(self) -> str:
        if not self.picker_temp_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%A")
        except:
            return ""

    @rx.var
    def picker_display_day(self) -> str:
        if not self.picker_temp_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%d")
        except:
            return ""

    @rx.var
    def picker_display_month(self) -> str:
        if not self.picker_temp_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%B")
        except:
            return ""

    @rx.var
    def picker_month_year_title(self) -> str:
        if not self.picker_view_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d").strftime("%B %Y")
        except:
            return ""
