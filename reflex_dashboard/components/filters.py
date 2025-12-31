import reflex as rx
from ..state import State
from ..colors import ACCENT_COLOR, BORDER_COLOR

def date_picker_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
             rx.flex(
                 # Left Panel (Header Display - Teal)
                 rx.center(
                     rx.vstack(
                         rx.text(State.picker_display_weekday, color="white", font_size="sm", opacity=0.8, text_align="center", width="100%"),
                         rx.text(State.picker_display_day, color="white", font_size="6xl", font_weight="bold", line_height="1", text_align="center", width="100%"), 
                         rx.text(State.picker_display_month, color="white", font_size="2xl", font_weight="bold", text_align="center", width="100%"),
                         rx.text(State.picker_display_year, color="white", font_size="2xl", opacity=0.7, text_align="center", width="100%"),
                         
                         spacing="1",
                         align="center",
                         justify="center",
                         height="100%",
                         width="100%"
                     ),
                     width="160px",
                     bg="#009688", # Teal
                     padding="4",
                     height="100%",
                 ),
                 
                 # Right Panel (Calendar - White)
                 rx.vstack(
                    # Header Month Year
                    rx.hstack(
                         rx.icon("chevron-left", on_click=State.picker_prev_month, cursor="pointer", color="black", size=18),
                         rx.text(State.picker_month_year_title, color="black", font_size="sm", font_weight="bold"), 
                         rx.icon("chevron-right", on_click=State.picker_next_month, cursor="pointer", color="black", size=18),
                        width="100%",
                        padding_x="4",
                        padding_top="4",
                        align="center",
                        justify="between"
                    ),
                    
                    # Weekday Headers
                    rx.grid(
                        *[rx.center(rx.text(day, color="#009688", font_size="xs", font_weight="bold")) for day in ["S", "M", "T", "W", "T", "F", "S"]],
                        columns="7",
                        width="100%",
                        padding_x="4",
                        margin_top="2"
                    ),
                    
                    # Days Grid
                    rx.grid(
                        rx.foreach(
                            State.picker_calendar_grid,
                            lambda item: rx.center(
                                    rx.text(
                                    item["day"], 
                                    font_size="sm",
                                    color=rx.cond(item["is_selected"], "white", rx.cond(item["is_current_month"], "black", "gray.300")),
                                    font_weight=rx.cond(item["is_selected"], "bold", "normal")
                                ),
                                bg=rx.cond(item["is_selected"], "#009688", "transparent"), # Teal selected
                                border_radius="full", 
                                width="30px",
                                height="30px",
                                cursor="pointer",
                                _hover={"bg": rx.cond(item["is_selected"], "#009688", "gray.100")},
                                on_click=lambda: State.picker_select_date(item["date_str"])
                            )
                        ),
                        columns="7",
                        width="100%",
                        padding_x="4",
                        row_gap="1"
                    ),
                    
                    rx.spacer(),
                    
                    # Footer
                    rx.hstack(
                        rx.text("Clear", color="#E53E3E", font_size="xs", font_weight="bold", cursor="pointer"),
                        rx.spacer(),
                        rx.text("CANCEL", on_click=State.close_picker, color="#009688", font_size="xs", font_weight="bold", cursor="pointer"),
                        rx.text("OK", on_click=State.picker_confirm, color="#009688", font_size="xs", font_weight="bold", cursor="pointer"),
                        width="100%",
                        justify="end",
                        padding="4",
                        spacing="4",
                        align="center"
                    ),
                    
                    bg="white", # White background for calendar
                    width="280px",
                    height="100%"
                 ),
                 
                 height="350px",
                 width="fit-content",
                 overflow="hidden",
                 border_radius="4px", # Slightly rounded
             ),
             bg="transparent", 
             padding="0",
             overflow="hidden",
             max_width="none",
             box_shadow="xl"
        ),
        open=State.show_picker,
    )

def filter_popover(label: str, icon: str, items: list, selected_items: list, toggle_all_fn, toggle_item_fn) -> rx.Component:
    """Helper to create a filter popover."""
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.hstack(
                    rx.icon(icon, size=16),
                    rx.text(label, font_size="sm", font_weight="bold"),
                    rx.icon("chevron-down", size=14, color="gray.400"),
                    spacing="2",
                    align="center"
                ),
                variant="ghost", 
                color_scheme="gray",
                color="white",
                _hover={"bg": "rgba(255,255,255,0.1)"}
            )
        ),
        rx.popover.content(
             rx.vstack(
                rx.checkbox("Select All", on_change=toggle_all_fn, color_scheme="gray", size="1"),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            items,
                            lambda item: rx.checkbox(
                                item,
                                checked=selected_items.contains(item),
                                on_change=lambda checked: toggle_item_fn(item, checked),
                                color_scheme="gray", 
                                size="1",
                                color="white"
                            )
                        ),
                        spacing="2",
                        align_items="start"
                    ),
                    type="always",
                    scrollbars="vertical",
                    style={"height": 150},
                ),
                spacing="2",
                width="100%"
            ),
            bg="#1A202C", 
            border=f"1px solid {BORDER_COLOR}",
            width="200px"
        ),
    )

def horizontal_filter_bar() -> rx.Component:
    """The modern horizontal filter bar."""
    return rx.box(
        rx.flex(
            # Left Side: Date Range + Filters
            rx.hstack(
                # 1. Date Range
                rx.hstack(
                    rx.icon("calendar-days", size=16, color=ACCENT_COLOR),
                    rx.text("PERIOD:", font_weight="900", color="white", font_size="xs"),
                    
                    # From
                    rx.box(
                        rx.hstack(
                            rx.text(rx.cond(State.start_date, State.start_date, "From"), color="white", font_size="sm", font_weight="medium"),
                            rx.icon("chevron-down", size=12, color="gray.500"),
                            spacing="2", align="center"
                        ),
                        padding="2",
                        border=f"1px solid {BORDER_COLOR}",
                        border_radius="md",
                        cursor="pointer",
                        on_click=lambda: State.open_picker("start"),
                        _hover={"bg": "rgba(255,255,255,0.05)"}
                    ),
                    rx.text("-", color="gray.500"),
                    # To
                    rx.box(
                        rx.hstack(
                            rx.text(rx.cond(State.end_date, State.end_date, "To"), color="white", font_size="sm", font_weight="medium"),
                            rx.icon("chevron-down", size=12, color="gray.500"),
                            spacing="2", align="center"
                        ),
                        padding="2",
                        border=f"1px solid {BORDER_COLOR}",
                        border_radius="md",
                        cursor="pointer",
                        on_click=lambda: State.open_picker("end"),
                        _hover={"bg": "rgba(255,255,255,0.05)"}
                    ),
                    spacing="3",
                    align="center",
                    border_right=f"1px solid {BORDER_COLOR}",
                    padding_right="6",
                    margin_right="4"
                ),
                
                # 2. Filters Group (Increased Spacing)
                rx.hstack(
                     filter_popover("Region", "map", State.states, State.selected_states, State.toggle_all_states, State.toggle_state),
                     filter_popover("Brand", "tag", State.brands, State.selected_brands, State.toggle_all_brands, State.toggle_brand),
                     filter_popover("Channel", "share-2", State.channels, State.selected_channels, State.toggle_all_channels, State.toggle_channel),
                     filter_popover("Supply", "truck", State.supply_types, State.selected_supply_types, State.toggle_all_supply, State.toggle_supply),
                     spacing="5" # Increased spacing between filters
                ),
                align="center",
            ),
            
            rx.spacer(),
            
            # 3. Clear Filters Action (More Prominent)
            rx.button(
                "Reset Filters",
                icon="rotate-ccw",
                variant="surface", # More visible than ghost
                color_scheme="red",
                size="2", # Slightly larger
                on_click=State.reset_filters # Assuming this method exists or will track, otherwise just UI for now
            ),

            width="100%",
            max_width="1900px", # Align with dashboard content
            margin_x="auto",    # Center align
            align="center",
            justify="between", # Ensure separation
            padding_x="6",
            padding_y="4"
        ),
        
        width="100%",
        bg="#111111", 
        border_bottom=f"1px solid {BORDER_COLOR}"
    )
