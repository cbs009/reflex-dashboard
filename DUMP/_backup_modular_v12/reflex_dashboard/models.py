import reflex as rx

class MonthlyValue(rx.Base):
    month: str
    value: str
    is_shaded: bool = False

class StateSummary(rx.Base):
    state: str
    monthly_values: list[MonthlyValue]
    total_value: str

class ChannelSummary(rx.Base):
    channel: str
    monthly_values: list[MonthlyValue]
    total_value: str
    children: list[StateSummary] = []
    is_total: bool = False

class InvRetChannel(rx.Base):
    channel: str
    inv: str = "-"
    ret: str = "-"
    ret_color: str = "black"
    val: str = "" # For pct row
    color: str = ""

class InvRetRow(rx.Base):
    month: str
    channels: list[InvRetChannel]
    grand_total_inv: str = "-"
    grand_total_ret: str = "-"
    grand_total_val: str = "" # For pct row
    is_pct: bool = False
    is_total: bool = False
