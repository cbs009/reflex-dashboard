import reflex as rx
from ..state.ai import AIState as State
from ..constants import SIDEBAR_BG, TEXT_COLOR, ACCENT_BLUE, BORDER_COLOR, TEXT_SECONDARY

def nav_item(label: str, icon: str, tab_id: str):
    is_active = State.current_tab == tab_id
    char_icon = icon if icon.startswith("fa") else f"fa-solid fa-{icon}"
    
    return rx.hstack(
        rx.center(
            rx.el.i(class_name=f"{char_icon} text-[14px]"),
            width="5", height="5"
        ),
        rx.text(label, font_size="14.5px", font_weight=rx.cond(is_active, "800", "700"), letter_spacing="-0.01em"),
        spacing="4",
        padding_y="3.5",
        padding_x="5",
        width="100%",
        border_radius="0 14px 14px 0",
        border_left=rx.cond(is_active, "4px solid #3b82f6", "0px solid transparent"),
        background_color=rx.cond(is_active, "#f1f5ff", "transparent"),
        color=rx.cond(is_active, "#4f46e5", "#64748b"),
        transition="all 0.1s ease-in-out",
        cursor="pointer",
        on_click=lambda: State.set_tab(tab_id),
        _hover=rx.cond(is_active, {}, {"background_color": "#f8fafc", "color": "#0f172a"})
    )

def date_picker_modal():
    # Keep existing modal logic for now, just style it slightly better if needed
    return rx.dialog.root(
        rx.dialog.content(
             rx.flex(
                 rx.center(
                     rx.vstack(
                         rx.text(State.picker_display_weekday, color="white", font_size="sm", opacity=0.8, text_align="center", width="100%"),
                         rx.text(State.picker_display_day, color="white", font_size="6xl", font_weight="bold", line_height="1", text_align="center", width="100%"), 
                         rx.text(State.picker_display_month, color="white", font_size="2xl", font_weight="bold", text_align="center", width="100%"),
                         rx.text(State.picker_display_year, color="white", font_size="2xl", opacity=0.7, text_align="center", width="100%"),
                         spacing="1", align="center", justify="center", height="100%", width="100%"
                     ),
                     width="160px", bg=ACCENT_BLUE, padding="4", height="100%",
                 ),
                 rx.vstack(
                    rx.hstack(
                         rx.icon("chevron-left", on_click=State.picker_prev_month, cursor="pointer", color="black", size=18),
                         rx.text(State.picker_month_year_title, color="black", font_size="sm", font_weight="bold"), 
                         rx.icon("chevron-right", on_click=State.picker_next_month, cursor="pointer", color="black", size=18),
                        width="100%", padding_x="4", padding_top="4", align="center", justify="between"
                    ),
                    rx.grid(*[rx.center(rx.text(day, color=ACCENT_BLUE, font_size="xs", font_weight="bold")) for day in ["S", "M", "T", "W", "T", "F", "S"]], columns="7", width="100%", padding_x="4", margin_top="2"),
                    rx.grid(rx.foreach(State.picker_calendar_grid, lambda item: rx.center(rx.text(item["day"], font_size="sm", color=rx.cond(item["is_selected"], "white", rx.cond(item["is_current_month"], "black", "gray.300")), font_weight=rx.cond(item["is_selected"], "bold", "normal")), bg=rx.cond(item["is_selected"], ACCENT_BLUE, "transparent"), border_radius="full", width="30px", height="30px", cursor="pointer", _hover={"bg": rx.cond(item["is_selected"], ACCENT_BLUE, "gray.100")}, on_click=lambda: State.picker_select_date(item["date_str"]))), columns="7", width="100%", padding_x="4", row_gap="1"),
                    rx.spacer(),
                    rx.hstack(rx.text("Clear", color="#E53E3E", font_size="xs", font_weight="bold", cursor="pointer"), rx.spacer(), rx.text("CANCEL", on_click=State.close_picker, color=ACCENT_BLUE, font_size="xs", font_weight="bold", cursor="pointer"), rx.text("OK", on_click=State.picker_confirm, color=ACCENT_BLUE, font_size="xs", font_weight="bold", cursor="pointer"), width="100%", justify="end", padding="4", spacing="4", align="center"),
                    bg="white", width="280px", height="100%"
                 ),
                 height="350px", width="fit-content", overflow="hidden", border_radius="4px",
             ),
             bg="transparent", padding="0", overflow="hidden", max_width="none", box_shadow="xl"
        ),
        open=State.show_picker,
    )

def sidebar_component():
    return rx.box(
        # Logo Section
        rx.hstack(
            rx.center(
                rx.el.i(class_name="fa-solid fa-gear text-white text-[12px]"),
                bg="#020617", width="9", height="9", border_radius="8px"
            ),
            rx.vstack(
                rx.text("ENTERPRISE", font_size="11px", font_weight="900", letter_spacing="0.1em", line_height="1", color="#020617"),
                rx.text("INTEL V12", font_size="11px", font_weight="900", letter_spacing="0.1em", line_height="1", color="#020617"),
                spacing="0", align_items="start"
            ),
            spacing="3", padding_x="6", padding_y="12", align_items="center"
        ),
        # Navigation Groups
        rx.vstack(
            rx.text("MAIN MODULES", font_size="11px", font_weight="900", color="slate.400", padding_x="8", padding_y="3", letter_spacing="0.15em"),
            nav_item("Business Summary", "house-chimney", "business-summary"),
            nav_item("Executive View", "chart-line", "executive"),
            nav_item("Predictive Engine", "brain", "predictive"),
            nav_item("Strategy Lab", "flask-vial", "prescriptive"),
            
            rx.text("ADVANCED LABS", font_size="11px", font_weight="900", color="slate.400", padding_x="8", padding_y="3", letter_spacing="0.15em", margin_top="10"),
            nav_item("Statistical Lab", "microscope", "statistical"),
            nav_item("Strategic Matrices", "grid-2", "matrices"),
            nav_item("Financial Audit", "file-invoice-dollar", "financial"),
            nav_item("Ops Intelligence", "truck-fast", "operations"),
            nav_item("Customer Science", "users-viewfinder", "customer"),
            nav_item("Governance & Audit", "shield-check", "governance"),
            
            align_items="start", width="100%", spacing="1"
        ),
        width="280px",
        height="100vh",
        background_color="white",
        border_right="1px solid #e2e8f0",
        position="sticky",
        top="0",
        left="0",
        z_index="100",
        display={"initial": "none", "lg": "block"}
    )
