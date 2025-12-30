import reflex as rx
import pandas as pd
from typing import List, Dict, Any

class BaseState(rx.State):
    """The base state with shared data."""
    # Raw Data
    _df: pd.DataFrame = pd.DataFrame()
    _courier_df: pd.DataFrame = pd.DataFrame()
    
    # Debug / Deployment Status
    deployment_status: str = ""
    
    # Upload State
    is_upload_modal_open: bool = True
    sales_data_uploaded: bool = False
    courier_data_uploaded: bool = False

    # Sidebar State
    is_sidebar_open: bool = True

    def toggle_sidebar(self):
        self.is_sidebar_open = not self.is_sidebar_open
    
    def close_upload_modal(self):
        self.is_upload_modal_open = False
