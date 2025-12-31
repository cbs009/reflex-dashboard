import reflex as rx
from ..state import State
from ..colors import CARD_BG, BORDER_COLOR

MONTH_COL_WIDTH = "110px"

def monthly_summary_table() -> rx.Component:
    return rx.box(
        # 1. Main Title Bar
        rx.flex(
            rx.box(
                rx.text(f"Monthly Summary of Gross Sale Value (Channel wise) {State.table_date_range_title}", font_size="md", font_weight="900", color="white", letter_spacing="0.05em", text_align="center", width="100%"),
                rx.box(height="12px"), # Gap between title and subtitle
                rx.text("Breakdown by Channel and Top 5 States", font_size="xs", font_weight="bold", color="white", letter_spacing="0.05em", text_align="center", width="100%"),
                rx.box(height="12px"), # Extra spacing
                width="100%",
            ),
            align="center",
            justify="center",
            padding="4",
            bg=CARD_BG,
            border_bottom=f"1px solid {BORDER_COLOR}",
            border_top_left_radius="xl",
            border_top_right_radius="xl",
        ),
        
        # 2. Table Container
        rx.box(
            # HEADER ROW
            rx.flex(
                rx.box(
                    rx.center(
                        rx.text("CHANNEL / REGION", font_weight="bold", color="white", font_size="10px", letter_spacing="0.1em"),
                        height="100%",
                        width="100%"
                    ),
                    width="150px", min_width="150px", max_width="150px", padding_left="0", padding_y="0", border_right=f"1px solid {BORDER_COLOR}"
                ),
                rx.foreach(
                    State.summary_table_columns,
                    lambda col: rx.flex(
                        rx.text(col, font_weight="bold", color="white", font_size="10px", text_align="center", width="100%", letter_spacing="0.1em"),
                        width="100%", # Flex width
                        min_width=MONTH_COL_WIDTH,
                        flex="1", 
                        padding_y="3", 
                        border_right=f"1px solid {BORDER_COLOR}", 
                        justify="center", 
                        align="center",
                        overflow="hidden"
                    )
                ),

                rx.box(rx.text("TOTAL", font_weight="bold", color="white", font_size="10px", text_align="center", letter_spacing="0.1em"), width="140px", min_width="140px", max_width="140px", padding_y="3", overflow="hidden", bg="#064E3B"),
                bg="#064E3B",
                width="100%", # Stretched
                min_width="max-content", # Prevent squishing
                align="center",
                border_bottom=f"1px solid {BORDER_COLOR}",
            ),
            
            # BODY ROWS
            rx.vstack(
                rx.foreach(
                    State.monthly_summary_data,
                    lambda row: rx.box(
                        # Condition: Grand Total Footer vs Data Rows
                        rx.cond(
                            row.is_total,
                             # FOOTER ROW (Grand Total)
                             rx.flex(
                                 rx.box(rx.text(row.channel, font_weight="900", color="white", font_size="sm", letter_spacing="0.05em", text_transform="capitalize"), width="150px", min_width="150px", max_width="150px", padding_left="4", padding_y="2", border_right=f"1px solid {BORDER_COLOR}", overflow="hidden"),
                                rx.foreach(
                                    row.monthly_values,
                                    lambda m, i: rx.flex(
                                        rx.text(m.value, color="white", font_size="10px", font_weight="medium", text_align="center", width="100%"),  
                                        width="100%",
                                        min_width=MONTH_COL_WIDTH,
                                        flex="1", 
                                        padding_y="2", 
                                        border_right=f"1px solid {BORDER_COLOR}", 
                                        bg=rx.cond(i % 2 == 0, "rgba(255,255,255,0.03)", "rgba(255,255,255,0.01)"),
                                        justify="center",
                                        align="center",
                                        overflow="hidden"
                                    )
                                ),
                                    rx.box(rx.text(row.total_value, font_weight="900", color="#22c55e", font_size="sm", text_align="center"), width="140px", min_width="140px", max_width="140px", padding_y="2", overflow="hidden", bg="#000000"), # Black for total column
                                bg="#064E3B", # Dark Green for Total ROW
                                width="100%",
                                min_width="max-content",
                                align="center",
                                border_top=f"1px solid {BORDER_COLOR}",
                            ),
                            # DATA ROW (Channel + Accordion)
                            rx.accordion.root(
                                rx.accordion.item(
                                    rx.accordion.trigger(
                                        rx.flex(
                                            rx.box(
                                                rx.hstack(
                                                    rx.icon("chevron-down", size=16, color="white"),
                                                    rx.text(row.channel, font_weight="bold", color="white", font_size="10px", white_space="nowrap", text_overflow="ellipsis", overflow="hidden", text_transform="capitalize"),
                                                    spacing="2",
                                                    align="center"
                                                ),
                                                width="150px", 
                                                min_width="150px",
                                                max_width="150px",
                                                padding_left="2",
                                                padding_y="2",
                                                border_right=f"1px solid {BORDER_COLOR}",
                                                overflow="hidden"
                                            ), 
                                            rx.foreach(
                                                row.monthly_values,
                                                lambda m, i: rx.flex(
                                                    rx.text(m.value, color="white", font_size="10px", text_align="center", width="100%", white_space="nowrap", text_overflow="ellipsis", overflow="hidden"),  
                                                    width="100%",
                                                    min_width=MONTH_COL_WIDTH,
                                                    flex="1",
                                                    padding_y="2", 
                                                    border_right=f"1px solid {BORDER_COLOR}", 
                                                    bg=rx.cond(i % 2 == 0, "transparent", "rgba(255,255,255,0.02)"),
                                                    justify="center",
                                                    align="center",
                                                    overflow="hidden"
                                                )
                                            ),
                                                rx.box(rx.text(row.total_value, font_weight="bold", color="white", font_size="10px", text_align="center"), width="140px", min_width="140px", max_width="140px", padding_y="2", overflow="hidden", bg="#000000"), 
                                            width="100%",
                                            min_width="max-content",
                                            align="center",
                                            bg="transparent",
                                            _hover={"bg": "rgba(255,255,255,0.03)"}
                                        ),
                                        padding="0",
                                        _hover={"bg": "transparent"},
                                    ),
                                    rx.accordion.content(
                                        rx.vstack(
                                            rx.foreach(
                                                row.children,
                                                lambda child: rx.flex(
                                                    rx.box(
                                                        rx.text(child.state, color="gray.400", font_size="10px", padding_left="8"),  
                                                        width="150px", 
                                                        min_width="150px",
                                                        max_width="150px",
                                                        padding_y="2", 
                                                        border_right=f"1px solid {BORDER_COLOR}",
                                                        overflow="hidden"
                                                    ),
                                                    rx.foreach(
                                                        child.monthly_values,
                                                        lambda m, i: rx.flex(
                                                            rx.text(m.value, color="gray.400", font_size="10px", text_align="center", width="100%", white_space="nowrap", text_overflow="ellipsis", overflow="hidden"),  
                                                            width="100%",
                                                            min_width=MONTH_COL_WIDTH,
                                                            flex="1", 
                                                            padding_y="2", 
                                                            border_right=f"1px solid {BORDER_COLOR}", 
                                                            bg=rx.cond(i % 2 == 0, "rgba(0,0,0,0.2)", "rgba(0,0,0,0.3)"), 
                                                            justify="center",
                                                            align="center",
                                                            overflow="hidden"
                                                        )
                                                    ),
                                                    rx.box(rx.text(child.total_value, color="gray.400", font_size="10px", text_align="center"), width="140px", min_width="140px", max_width="140px", padding_y="2", overflow="hidden", bg="#000000"),
                                                    bg="rgba(0,0,0,0.4)",
                                                    width="100%",
                                                    min_width="max-content",
                                                    align="center",
                                                    border_top=f"1px dotted {BORDER_COLOR}",
                                                )
                                            ),
                                            width="100%",
                                            min_width="max-content",
                                            spacing="0",
                                        ),
                                        padding="0",
                                    ),
                                    border_width="0",
                                    padding="0",
                                ),
                                type="multiple",
                                collapsible=True,
                                width="100%",
                                min_width="max-content",
                                variant="ghost",
                            )
                        ),
                        width="100%",
                        border_bottom=f"1px solid {BORDER_COLOR}",
                        bg="transparent"
                    )
                ),
                width="100%",
                spacing="0"
            ),
            width="100%",
            overflow="auto", 
        ),
        bg="#000000",
        border=f"1px solid {BORDER_COLOR}",
        border_radius="xl",
        width="100%",
        box_shadow="lg",
    )

def monthly_sales_return_table() -> rx.Component:
    return rx.box(
        # 1. Main Title Bar
        rx.flex(
            rx.box(
                rx.text(f"Monthly Sales Return (Channel wise) {State.table_date_range_title}", font_size="md", font_weight="900", color="white", letter_spacing="0.05em", text_align="center", width="100%"),
                width="100%",
            ),
            align="center",
            justify="center",
            padding="4",
            bg=CARD_BG,
            border_bottom=f"1px solid {BORDER_COLOR}",
            border_top_left_radius="xl",
            border_top_right_radius="xl",
        ),
        
        rx.box(
            # HEADER ROW
            rx.flex(
                rx.box(
                    rx.center(
                        rx.text("CHANNEL", font_weight="bold", color="white", font_size="10px", letter_spacing="0.1em"),
                        height="100%",
                        width="100%"
                    ),
                    width="150px", min_width="150px", max_width="150px", padding_left="0", padding_y="0", border_right=f"1px solid {BORDER_COLOR}"
                ),
                rx.foreach(
                    State.summary_table_columns,
                    lambda col: rx.flex(
                        rx.text(col, font_weight="bold", color="white", font_size="10px", text_align="center", width="100%", letter_spacing="0.1em"),
                        width="100%",
                        min_width=MONTH_COL_WIDTH,
                        flex="1", 
                        padding_y="3", 
                        border_right=f"1px solid {BORDER_COLOR}", 
                        justify="center", 
                        align="center",
                        overflow="hidden"
                    )
                ),

                rx.box(rx.text("TOTAL", font_weight="bold", color="white", font_size="10px", text_align="center", letter_spacing="0.1em"), width="140px", min_width="140px", max_width="140px", padding_y="3", overflow="hidden", bg="#064E3B"),
                bg="#064E3B",
                width="100%",
                min_width="max-content",
                align="center",
                border_bottom=f"1px solid {BORDER_COLOR}",
            ),
            
            # BODY ROWS
            rx.vstack(
                rx.foreach(
                    State.monthly_sales_return_data,
                    lambda row: rx.box(
                        rx.flex(
                            rx.box(rx.text(row.channel, font_weight="bold", color="white", font_size="10px", text_transform="capitalize"), width="150px", min_width="150px", max_width="150px", padding_left="4", padding_y="2", border_right=f"1px solid {BORDER_COLOR}", overflow="hidden"),
                            rx.foreach(
                                row.monthly_values,
                                lambda m, i: rx.flex(
                                    rx.text(m.value, color="white", font_size="10px", text_align="center", width="100%", white_space="nowrap", text_overflow="ellipsis", overflow="hidden"),  
                                    width="100%",
                                    min_width=MONTH_COL_WIDTH,
                                    flex="1", 
                                    padding_y="2", 
                                    border_right=f"1px solid {BORDER_COLOR}", 
                                    bg=rx.cond(
                                        row.is_total,
                                        rx.cond(i % 2 == 0, "rgba(255,255,255,0.05)", "rgba(255,255,255,0.02)"),
                                        rx.cond(i % 2 == 0, "transparent", "rgba(255,255,255,0.04)")
                                    ), 
                                    justify="center",
                                    align="center",
                                    overflow="hidden"
                                )
                            ),
                                rx.box(rx.text(row.total_value, font_weight="bold", color=rx.cond(row.is_total, "#22c55e", "white"), font_size=rx.cond(row.is_total, "sm", "10px"), text_align="center"), width="140px", min_width="140px", max_width="140px", padding_y="2", overflow="hidden", bg=rx.cond(row.is_total, "#000000", "#000000")),
                            bg=rx.cond(row.is_total, "#064E3B", "transparent"),
                            width="100%", # Added explicitly to inner flex
                            align="center",
                            border_top=rx.cond(row.is_total, f"1px solid {BORDER_COLOR}", "none"),
                            border_bottom=f"1px solid {BORDER_COLOR}"
                        ),
                        width="100%"
                    )
                ),
                width="100%",
                spacing="0"
            ),
            width="100%",
            overflow="auto", 
        ),
        bg="#000000",
        width="100%",
        border_radius="xl",
        border=f"1px solid {BORDER_COLOR}",
        box_shadow="lg",
    )

def invoice_vs_return_table() -> rx.Component:
    COL_WIDTH = "68px" # Smaller cols for Inv/Ret
    MONTH_COL_WIDTH_INV = "150px" 

    return rx.box(
        # 1. Main Title Bar
        rx.flex(
             rx.box(
                rx.hstack(
                     rx.icon("file-text", size=20, color="white"),
                    rx.text(f"Invoice vs Sales Return {State.table_date_range_title}", font_size="md", font_weight="900", color="white", letter_spacing="0.05em", text_align="center"),
                    justify="center",
                    align="center", 
                    spacing="2"
                ),
                width="100%",
             ),
            align="center",
            justify="center",
            padding="4",
            bg=CARD_BG,
            border_bottom=f"1px solid {BORDER_COLOR}",
            border_top_left_radius="xl",
            border_top_right_radius="xl",
        ),
        
        rx.box(
             # COMPLEX HEADER
             rx.flex(
                 # Column 1: Month (Merged Vertically)
                 rx.box(
                     rx.center(
                         rx.text("MONTH", font_weight="bold", color="white", font_size="10px", letter_spacing="0.1em"),
                         height="100%",
                         width="100%"
                     ),
                     width=MONTH_COL_WIDTH_INV, 
                     min_width=MONTH_COL_WIDTH_INV, 
                     border_right=f"1px solid {BORDER_COLOR}", 
                     height="auto", # Fill height of parent flex
                     flex_shrink=0
                 ),
                 
                 # Columns: Channels (Iterated as VStacks)
                 rx.foreach(
                     State.invoice_return_columns,
                     lambda col: rx.vstack(
                         # Row A: Title
                         rx.flex(
                             rx.text(col, font_weight="bold", color="white", font_size="10px", text_align="center", width="100%", letter_spacing="0.1em", text_transform="capitalize"),
                             width="100%",
                             padding_y="3",
                             justify="center",
                             align="center",
                             overflow="hidden",
                             border_bottom=f"1px solid {BORDER_COLOR}",
                             flex="1"
                         ),
                         # Row B: Inv / Ret
                         rx.flex(
                             rx.box(rx.text("Inv", color="white", font_size="10px", font_weight="bold", text_align="center"), width="50%", border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                             rx.box(rx.text("Ret", color="#FA5252", font_size="10px", font_weight="bold", text_align="center"), width="50%", padding_y="2"), 
                             width="100%",
                             justify="center",
                             align="center",
                             overflow="hidden",
                             spacing="0"
                         ),
                         width="100%",
                         min_width="136px",
                         flex="1",
                         border_right=f"1px solid {BORDER_COLOR}",
                         spacing="0"
                     )
                 ),
                # Grand Total Column Header
                rx.vstack(
                    rx.flex(
                        rx.text("Grand Total", font_weight="bold", color="white", font_size="10px", text_align="center", width="100%", letter_spacing="0.1em"),
                        width="100%", 
                        min_width="136px",
                        padding_y="3", 
                        border_right=f"1px solid {BORDER_COLOR}", 
                        justify="center", 
                        align="center",
                        overflow="hidden",
                        flex="1"
                    ),
                    rx.flex(
                        rx.box(rx.text("Inv", color="white", font_size="10px", font_weight="bold", text_align="center"), width="50%", border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                        rx.box(rx.text("Ret", color="#FA5252", font_size="10px", font_weight="bold", text_align="center"), width="50%", border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                        width="100%",
                        min_width="136px",
                        flex="1",
                        justify="center",
                        align="center",
                        overflow="hidden",
                        spacing="0",
                        border_top=f"1px solid {BORDER_COLOR}"
                    ),
                    bg="transparent",
                    width="100%",
                    min_width="136px",
                    flex="1",
                    spacing="0"
                ), 
                bg="#064E3B",
                width="100%",
                min_width="max-content",
                align="stretch"
            ),


             # BODY
            rx.vstack(
                rx.foreach(
                    State.invoice_vs_return_data,
                    lambda row, i: rx.box(
                        rx.flex(
                            rx.box(rx.text(row.month, font_weight="bold", color="white", font_size="10px"), width=MONTH_COL_WIDTH_INV, min_width=MONTH_COL_WIDTH_INV, padding_left="4", padding_y="3", border_right=f"1px solid {BORDER_COLOR}", overflow="hidden"),
                            
                            # Check if it has 'channels' list (Normal Rows)
                            rx.cond(
                               row.is_pct,
                                # PCT ROW
                                rx.foreach(
                                    row.channels, 
                                    lambda chan, j: rx.flex(
                                       rx.text(chan.val, color=chan.color, font_size="sm", font_weight="bold", text_align="center", width="100%"),
                                       width="100%",
                                       min_width="136px",
                                       flex="1",
                                       padding_y="2",
                                       bg=rx.cond(
                                           row.is_total,
                                           rx.cond(j % 2 == 0, "rgba(255,255,255,0.05)", "rgba(255,255,255,0.02)"),
                                           rx.cond(j % 2 == 0, "transparent", "rgba(255,255,255,0.04)")
                                       ), 
                                       border_right=f"1px solid {BORDER_COLOR}",
                                       justify="center",
                                       align="center"
                                   )
                                ),
                                # DATA ROW
                                rx.foreach(
                                    row.channels,
                                    lambda chan, j: rx.flex(
                                        rx.box(rx.text(chan.inv, color=rx.cond(chan.channel=="Grand Total", "#22c55e", "white"), font_size="10px", text_align="center"), width="50%", border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                                        rx.box(rx.text(chan.ret, color="#FA5252", font_size="10px", text_align="center"), width="50%", border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                                        width="100%",
                                        min_width="136px",
                                        flex="1",
                                        justify="center",
                                        align="center",
                                        overflow="hidden",
                                        spacing="0",
                                        bg=rx.cond(
                                           row.is_total,
                                           rx.cond(j % 2 == 0, "rgba(255,255,255,0.05)", "rgba(255,255,255,0.02)"),
                                           rx.cond(j % 2 == 0, "transparent", "rgba(255,255,255,0.04)")
                                       )
                                    )
                                )
                            ),
                            bg=rx.cond(
                                row.is_total, 
                                "#064E3B", 
                                rx.cond(i % 2 == 0, "transparent", "rgba(255,255,255,0.04)")
                            ), # Alternating colors
                            width="100%",
                            border_bottom=f"1px solid {BORDER_COLOR}",
                            align="center"
                        ),
                        width="100%"
                    )
                 ),
                 width="100%",
                 spacing="0"
             ),
             width="100%",
             overflow="auto", 
        ),
        bg="#000000",
        width="100%",
        border_radius="xl",
        border=f"1px solid {BORDER_COLOR}",
        box_shadow="lg",
    )
