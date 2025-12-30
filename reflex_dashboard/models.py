import reflex as rx
from pydantic import BaseModel

class MonthlyValue(BaseModel):
    month: str
    value: str
    is_shaded: bool = False

class StateSummary(BaseModel):
    state: str
    monthly_values: list[MonthlyValue]
    total_value: str

class ChannelSummary(BaseModel):
    channel: str
    monthly_values: list[MonthlyValue]
    total_value: str
    children: list[StateSummary]
    is_total: bool = False

class InvRetChannel(BaseModel):
    channel: str
    inv: str = "-"
    ret: str = "-"
    ret_color: str = "black"
    val: str = "" # For pct row
    color: str = ""

class InvRetRow(BaseModel):
    month: str
    channels: list[InvRetChannel]
    grand_total_inv: str = "-"
    grand_total_ret: str = "-"
    grand_total_val: str = "" # For pct row
    is_pct: bool = False
    is_total: bool = False
