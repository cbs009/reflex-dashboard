import reflex as rx
from ..state import State
from ..colors import CARD_BG, TEXT_COLOR, CONTENT_BG, BORDER_COLOR
from .common import placeholder_tab
from .empty_state import no_data_view
from .filters import date_picker_modal, horizontal_filter_bar
from .ai import ai_chat_component, ai_chef_placeholder
from .overview import overview_tab_content
from .customer import customer_tab_content
from .intro import intro_tab_content
from .predictive import predictive_tab_content

def index() -> rx.Component:
    return rx.box(
        rx.cond(
            # CONDITIONAL: Show No Data View if dashboard is not started
            ~State.show_dashboard,
            no_data_view(),
            # ELSE: Dashboard is active
            rx.cond(
                State.show_intro,
                rx.box(
                    intro_tab_content(),
                    height="100vh",
                    width="100%",
                    bg="black"
                ),
                # ELSE: Show New Enterprise Layout
                rx.box(
                    date_picker_modal(),
                    # 1. Main Header
                    rx.box(
                    rx.center( # Force centering using rx.center wrapper
                        rx.vstack(
                            rx.hstack(
                                rx.icon("database", size=20, color="white"),
                                rx.heading("ENTERPRISE INTELLIGENCE SUITE", size="4", color="white", font_weight="900", letter_spacing="0.05em"),
                                align="center",
                                spacing="3"
                            ),
                            rx.badge("FULL-SPECTRUM STRATEGIC DASHBOARD V10.0", color_scheme="gray", variant="soft", size="1"),
                            align="center",
                            spacing="1",
                        ),
                        width="100%"
                    ),
                    rx.box(
                        rx.hstack(
                             rx.button(
                                 rx.hstack(
                                     rx.icon("download", size=16),
                                     rx.text("Export PPT", font_size="12px"),
                                     spacing="2"
                                 ),
                                 variant="solid",
                                 size="2",
                                 color_scheme="orange",
                                 on_click=State.export_ppt,
                                 cursor="pointer"
                             ),
                        ),
                        position="absolute",
                        right="4",
                        top="50%",
                        transform="translateY(-50%)",
                    ),
                    width="100%",
                    padding="4",
                    bg="#000000",
                    border_bottom=f"1px solid {BORDER_COLOR}",
                    position="relative",
                ),
                
                # 2. Tabs Navigation (Keyboard Key Style - Centered - 3 Per Row)
                rx.tabs.root(
                    rx.tabs.list(
                        # Single Row - 6 Tabs
                        rx.tabs.trigger(
                            "BUSINESS SUMMARY", 
                            value="overview",
                            width="100%", height="60px",
                            bg="rgba(56, 161, 105, 0.15)", # Green tint
                            border="1px solid #38A169",
                            color="#38A169",
                            _active={"bg": "#38A169", "color": "white", "transform": "translateY(2px)", "box_shadow": "none"}, 
                            style={"border_radius": "8px", "box_shadow": "0px 4px 0px #22543d", "transition": "all 0.1s", "font_weight": "900", "font_size": "15px"},
                            cursor="pointer"
                        ),
                        rx.tabs.trigger(
                            "PREDICTIVE ENGINE", 
                            value="predictive",
                                width="100%", height="60px",
                            bg="rgba(128, 90, 213, 0.15)", # Purple tint
                            border="1px solid #805AD5",
                            color="#805AD5",
                            _active={"bg": "#805AD5", "color": "white", "transform": "translateY(2px)", "box_shadow": "none"}, 
                            style={"border_radius": "8px", "box_shadow": "0px 4px 0px #44337a", "transition": "all 0.1s", "font_weight": "900", "font_size": "15px"},
                            cursor="pointer"
                        ),
                        rx.tabs.trigger(
                            "STRATEGY LAB", 
                            value="strategy",
                                width="100%", height="60px",
                            bg="rgba(49, 130, 206, 0.15)", # Blue tint
                            border="1px solid #3182CE",
                            color="#3182CE",
                            _active={"bg": "#3182CE", "color": "white", "transform": "translateY(2px)", "box_shadow": "none"}, 
                            style={"border_radius": "8px", "box_shadow": "0px 4px 0px #2a4365", "transition": "all 0.1s", "font_weight": "900", "font_size": "15px"},
                            cursor="pointer"
                        ),
                        rx.tabs.trigger(
                            "FINANCIAL AUDIT", 
                            value="finance",
                                width="100%", height="60px",
                            bg="rgba(213, 63, 140, 0.15)", # Magenta tint
                            border="1px solid #D53F8C",
                            color="#D53F8C",
                            _active={"bg": "#D53F8C", "color": "white", "transform": "translateY(2px)", "box_shadow": "none"}, 
                            style={"border_radius": "8px", "box_shadow": "0px 4px 0px #702459", "transition": "all 0.1s", "font_weight": "900", "font_size": "15px"},
                            cursor="pointer"
                        ),
                        rx.tabs.trigger(
                            "OPERATIONS LAB", 
                            value="operations",
                                width="100%", height="60px",
                            bg="rgba(246, 135, 179, 0.15)", # Pinkish tint
                            border="1px solid #F687B3",
                            color="#F687B3",
                            _active={"bg": "#F687B3", "color": "white", "transform": "translateY(2px)", "box_shadow": "none"}, 
                            style={"border_radius": "8px", "box_shadow": "0px 4px 0px #97266d", "transition": "all 0.1s", "font_weight": "900", "font_size": "15px"},
                            cursor="pointer"
                        ),
                        rx.tabs.trigger(
                            "CUSTOMER SCIENCE", 
                            value="customer",
                                width="100%", height="60px",
                            bg="rgba(214, 158, 46, 0.15)", # Yellowish tint
                            border="1px solid #D69E2E",
                            color="#D69E2E",
                            _active={"bg": "#D69E2E", "color": "white", "transform": "translateY(2px)", "box_shadow": "none"}, 
                            style={"border_radius": "8px", "box_shadow": "0px 4px 0px #744210", "transition": "all 0.1s", "font_weight": "900", "font_size": "15px"},
                            cursor="pointer"
                        ),
                        
                        # Apply Grid Styles directly to the list container
                        display="grid",
                        grid_template_columns="repeat(6, 1fr)",
                        gap="16px",
                        padding_y="24px",
                        bg="transparent",
                        width="100%", 
                        max_width="1600px", 
                        margin_x="auto"
                    ),
                        
                        # 3. Filter Bar (Sticky)
                        rx.box(
                             horizontal_filter_bar(),
                             position="sticky",
                             top="0",
                             z_index="50",
                             width="100%"
                        ),
                        
                        # 4. AI Assistant
                        rx.box(
                             ai_chat_component(),
                             padding="4",
                             bg="#111111",
                             border_bottom=f"1px solid {BORDER_COLOR}"
                        ),
    
                        # 5. Tab Content Areas
                        rx.box(
                            # Empty State Hint
                            rx.cond(State.current_tab == "", ai_chef_placeholder()),
                            
                            rx.tabs.content(
                                overview_tab_content(),
                                value="overview",
                                padding="6",
                            ),
                            rx.tabs.content(predictive_tab_content(), value="predictive"),
                            rx.tabs.content(placeholder_tab("Strategy Lab"), value="strategy"),
                            rx.tabs.content(placeholder_tab("Financial Audit"), value="finance"),
                            rx.tabs.content(placeholder_tab("Operations Lab"), value="operations"),
                            rx.tabs.content(
                                customer_tab_content(),
                                value="customer",
                                padding="6"
                            ),
                            
                            bg=CONTENT_BG,
                            min_height="calc(100vh - 150px)", # Adjust for headers
                            width="100%",
                            max_width="1900px", # Limit width for readability
                            margin_x="auto"
                        ),
                        
                        
                            

                            value=State.current_tab,
                            on_change=State.set_current_tab,
                        width="100%",
                    ),
                )
            ),
        ),
        width="100%",
        min_height="100vh",
        on_mount=State.load_data,
        bg=CONTENT_BG
    )
