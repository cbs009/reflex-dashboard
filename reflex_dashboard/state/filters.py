import reflex as rx
import datetime
import calendar
from .base import BaseState

class FilterState(BaseState):
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
    min_date: str = ""
    max_date: str = ""

    def reset_filters(self):
        """Reset all filters to default state (Select All)."""
        self.selected_months = self.months
        self.selected_states = self.states
        self.selected_brands = self.brands
        self.selected_channels = self.channels
        self.selected_supply_types = self.supply_types
        # Reset dates to full range
        self.start_date = self.min_date
        self.end_date = self.max_date

    def set_start_date(self, val: str):
        self.start_date = val
        
    def set_end_date(self, val: str):
        self.end_date = val

    # Helper properties for Select All/None logic
    def toggle_all_months(self, select: bool):
        self.selected_months = self.months if select else []
    
    def toggle_all_states(self, select: bool):
        self.selected_states = self.states if select else []
        
    def toggle_all_brands(self, select: bool):
        self.selected_brands = self.brands if select else []
        
    def toggle_all_channels(self, select: bool):
        self.selected_channels = self.channels if select else []
        
    def toggle_all_supply(self, select: bool):
        self.selected_supply_types = self.selected_supply_types if select else []

    # Toggle Individual Filters
    def toggle_month(self, month: str, checked: bool):
        if checked:
            self.selected_months = self.selected_months + [month]
        else:
            self.selected_months = [m for m in self.selected_months if m != month]

    def toggle_state(self, state: str, checked: bool):
        if checked:
            self.selected_states = self.selected_states + [state]
        else:
            self.selected_states = [s for s in self.selected_states if s != state]

    def toggle_brand(self, brand: str, checked: bool):
        if checked:
            self.selected_brands = self.selected_brands + [brand]
        else:
            self.selected_brands = [b for b in self.selected_brands if b != brand]

    def toggle_channel(self, channel: str, checked: bool):
        if checked:
            self.selected_channels = self.selected_channels + [channel]
        else:
            self.selected_channels = [c for c in self.selected_channels if c != channel]
            
    def toggle_supply(self, supply: str, checked: bool):
        if checked:
            self.selected_supply_types = self.selected_supply_types + [supply]
        else:
            self.selected_supply_types = [s for s in self.selected_supply_types if s != supply]

    # --- Custom Date Picker State ---
    show_picker: bool = False
    picker_target: str = "start" # "start" or "end"
    picker_view_date: str = "" # The month we are looking at
    picker_temp_date: str = "" # The date currently selected in the picker (before OK)

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
        """Returns the grid for the current view month."""
        if not self.picker_view_date: return []
        try:
            dt = datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d")
            year = dt.year
            month = dt.month
            
            c = calendar.Calendar(firstweekday=6) # Sunday start
            
            grid = []
            for date_obj in c.itermonthdates(year, month):
                is_current_month = (date_obj.month == month)
                date_str = date_obj.strftime("%Y-%m-%d")
                
                # Check strict equality for today and selected
                # We return simple types
                grid.append({
                    "day": date_obj.day,
                    "date_str": date_str,
                    "is_current_month": is_current_month,
                    "is_selected": (date_str == self.picker_temp_date),
                    # "is_today": (date_str == datetime.date.today().strftime("%Y-%m-%d")) # Optional
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
             # Keep this for compatibility if used elsewhere, but we primarily use the split ones below
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

    @rx.var
    def dashboard_title(self) -> str:
        """Dynamic dashboard title based on date range."""
        base_title = "Interactive Sales Dashboard"
        if self.start_date and self.end_date:
            try:
                # Parse YYYY-MM-DD
                s_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
                e_date = datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
                
                # Format as Apr'25 - Nov'25
                # Using %b for Month abbr, %y for 2-digit year
                s_str = s_date.strftime("%b'%y")
                e_str = e_date.strftime("%b'%y")
                
                return f"{base_title} ({s_str} - {e_str})"
            except Exception:
                return base_title
        return base_title
