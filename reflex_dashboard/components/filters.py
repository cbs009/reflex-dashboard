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

def sidebar_component() -> rx.Component:
    """The modern filter sidebar."""
    return rx.box(
        rx.vstack(
            # Sidebar Header (Centered Dashboard + Period)
            rx.box(
                rx.vstack(
                    rx.hstack(
                         rx.icon("layout-dashboard", size=20, color=ACCENT_COLOR),
                         rx.heading("DASHBOARD", size="3", color="white", font_weight="900", letter_spacing="0.1em"),
                         align="center",
                         spacing="3",
                         justify="center"
                     ),
                     rx.center(
                         rx.hstack(
                             rx.icon("calendar-days", size=16, color="white"),
                             rx.text("PERIOD", font_weight="900", color="white", font_size="xs", letter_spacing="0.1em"),
                             align="center", spacing="2", justify="center"
                         )
                     ),
                     spacing="2",
                     align="center",
                     justify="center",
                     width="100%"
                ),
                
                # Close Button (Absolute)
                rx.box(
                    rx.button(
                         rx.icon("x", size=18, color="white"),
                         variant="ghost",
                         size="1", 
                         on_click=State.toggle_sidebar,
                         color_scheme="gray"
                    ),
                    position="absolute",
                    top="0",
                    right="0"
                ),
                
                position="relative",
                width="100%",
                margin_bottom="6",
                padding_x="2"
            ),
            
            # Date Range Filter
            rx.vstack(
                # Vertical Layout
                rx.vstack(
                    rx.box(
                        rx.text("FROM", font_size="xs", color="white", font_weight="900", margin_bottom="2", text_align="center", width="100%"),
                        rx.box(
                            rx.hstack(
                                rx.text(rx.cond(State.start_date, State.start_date, "Select Date"), color="white", font_size="sm", font_weight="medium"),
                                rx.icon("chevron-down", size=14, color="gray.600"),
                                width="100%",
                                align="center",
                                justify="center",
                                spacing="2"
                            ),
                            bg="rgba(255,255,255,0.03)", 
                            border=f"1px solid {BORDER_COLOR}",
                            border_radius="md",
                            padding="3",
                            width="100%",
                            cursor="pointer",
                            on_click=lambda: State.open_picker("start"),
                            _hover={"border_color": ACCENT_COLOR, "bg": "rgba(255,255,255,0.05)"},
                            transition="all 0.2s"
                        ),
                        width="100%"
                    ),
                    rx.box(
                        rx.text("TO", font_size="xs", color="white", font_weight="900", margin_bottom="2", text_align="center", width="100%"),
                        rx.box(
                             rx.hstack(
                                rx.text(rx.cond(State.end_date, State.end_date, "Select Date"), color="white", font_size="sm", font_weight="medium"),
                                rx.icon("chevron-down", size=14, color="gray.600"),
                                width="100%",
                                align="center",
                                justify="center",
                                spacing="2"
                             ),
                            bg="rgba(255,255,255,0.03)",
                            border=f"1px solid {BORDER_COLOR}",
                            border_radius="md",
                            padding="3",
                            width="100%",
                            cursor="pointer",
                             on_click=lambda: State.open_picker("end"),
                             _hover={"border_color": ACCENT_COLOR, "bg": "rgba(255,255,255,0.05)"},
                             transition="all 0.2s"
                        ),
                        width="100%"
                    ),
                    width="100%",
                    spacing="4" 
                ),
                padding="0", 
                width="100%",
                margin_bottom="8" 
            ),
            
            rx.accordion.root(
                
                # State Filter
                rx.accordion.item(
                    header=rx.center(
                        rx.hstack(
                            rx.icon("map", size=16, color=ACCENT_COLOR),
                            rx.text("REGION", font_weight="900", color="white", font_size="sm", letter_spacing="0.1em"),
                            align="center", spacing="2", justify="center"
                        ),
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_states, color_scheme="gray", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.states,
                                    lambda state: rx.checkbox(
                                        state,
                                        checked=State.selected_states.contains(state),
                                        on_change=lambda checked: State.toggle_state(state, checked),
                                        color_scheme="gray", 
                                        size="1" 
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
                    style={"background": "transparent", "border": "none"}
                ),

                # Brand Filter
                rx.accordion.item(
                    header=rx.center(
                        rx.hstack(
                            rx.icon("tag", size=16, color=ACCENT_COLOR),
                            rx.text("BRAND", font_weight="900", color="white", font_size="sm", letter_spacing="0.1em"),
                            align="center", spacing="2", justify="center"
                        ),
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_brands, color_scheme="gray", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.brands,
                                    lambda brand: rx.checkbox(
                                        brand,
                                        checked=State.selected_brands.contains(brand),
                                        on_change=lambda checked: State.toggle_brand(brand, checked),
                                        color_scheme="gray",
                                        size="1"
                                    ),
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
                    style={"background": "transparent", "border": "none"}
                ),
                
                # Channel Filter
                rx.accordion.item(
                    header=rx.center(
                        rx.hstack(
                            rx.icon("share-2", size=16, color=ACCENT_COLOR),
                            rx.text("CHANNEL", font_weight="900", color="white", font_size="sm", letter_spacing="0.1em"),
                            align="center", spacing="2", justify="center"
                        ),
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_channels, color_scheme="gray", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.channels,
                                    lambda channel: rx.checkbox(
                                        channel,
                                        checked=State.selected_channels.contains(channel),
                                        on_change=lambda checked: State.toggle_channel(channel, checked),
                                        color_scheme="gray",
                                        size="1"
                                    ),
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
                    style={"background": "transparent", "border": "none"}
                ),

               # Supply Type Filter
                rx.accordion.item(
                    header=rx.center(
                        rx.hstack(
                            rx.icon("truck", size=16, color=ACCENT_COLOR),
                            rx.text("SUPPLY TYPE", font_weight="900", color="white", font_size="sm", letter_spacing="0.1em"),
                            align="center", spacing="2", justify="center"
                        ),
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_supply, color_scheme="gray", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.supply_types,
                                    lambda st: rx.checkbox(
                                        st,
                                        checked=State.selected_supply_types.contains(st),
                                        on_change=lambda checked: State.toggle_supply(st, checked),
                                        color_scheme="gray",
                                        size="1"
                                    ),
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
                    style={"background": "transparent", "border": "none"}
                ),
                
                type="multiple",
                collapsible=True,
                width="100%",
                variant="outline", # Clean variant
                margin_top="16",
            ),
            
            width="100%",
            spacing="1",
            padding_top="500px", # Added spacing from top edge
        ),
        width="280px", # Slightly wider for elegance
        height="100vh", # Full height
        bg="#111111", # Darker background
        padding="6",
        border_right="1px solid #333333",
        display=rx.cond(State.is_sidebar_open, "block", "none"), 
        position="sticky",
        top="0",
        z_index="1000"
    )
