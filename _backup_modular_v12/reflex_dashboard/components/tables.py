import reflex as rx
from ..state.ai import AIState as State
from ..constants import CARD_BG, BORDER_COLOR, TEXT_COLOR, TEXT_SECONDARY, ACCENT_BLUE, ACCENT_INDIGO
from .common import table_container

def product_sales_table():
    return table_container(
        "Product Sales Distribution",
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Rank", text_align="center", color="white", font_weight="bold"),
                    rx.table.column_header_cell("Product Name", text_align="center", color="white", font_weight="bold"),
                    rx.table.column_header_cell("Sales", text_align="center", color="white", font_weight="bold"),
                    rx.table.column_header_cell("Contribution", text_align="center", color="white", font_weight="bold"),
                    bg="slate.800"
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.product_data,
                    lambda row: rx.table.row(
                        rx.table.cell(
                            rx.center(
                                rx.text(row["rank"], font_weight="bold", color="white", font_size="xs"),
                                bg=row["rank_bg"],
                                width="20px", height="20px", border_radius="full", margin_x="auto"
                            ),
                            text_align="center"
                        ),
                        rx.table.cell(rx.text(row["label"], font_size="xs", font_weight="bold", color=TEXT_COLOR)),
                        rx.table.cell(rx.text(row["formatted_value"], font_size="xs", font_weight="black", color=ACCENT_INDIGO), text_align="center"),
                        rx.table.cell(rx.text(row["formatted_pct"], font_size="xs", font_weight="bold", color=TEXT_SECONDARY), text_align="center"),
                        border_bottom=f"1px solid {BORDER_COLOR}"
                    )
                )
            ),
            width="100%"
        )
    )

def b2c_aov_table():
    return table_container(
        "B2C Average Order Value",
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Channel", text_align="center", color="white", font_weight="bold"),
                    rx.table.column_header_cell("Sales", text_align="center", color="white", font_weight="bold"),
                    rx.table.column_header_cell("Orders", text_align="center", color="white", font_weight="bold"),
                    rx.table.column_header_cell("AOV", text_align="center", color="white", font_weight="bold"),
                    bg="slate.800"
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.b2c_data,
                    lambda row: rx.table.row(
                        rx.table.cell(rx.text(row["channel"], color=row["channel_color"], font_weight="black", font_size="xs")),
                        rx.table.cell(rx.text(row["formatted_sales"], font_size="xs", font_weight="bold", color=TEXT_COLOR), text_align="center"),
                        rx.table.cell(rx.text(row["orders"], font_size="xs", color=TEXT_SECONDARY), text_align="center"),
                        rx.table.cell(rx.text(row["formatted_aov"], font_size="xs", font_weight="black", color="emerald.600"), text_align="center"),
                        border_bottom=f"1px solid {BORDER_COLOR}"
                    )
                )
            ),
            width="100%"
        )
    )

def state_wise_product_table():
    return table_container(
        "State-wise Top Selling B2C Product",
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("State", color="white", font_weight="bold"),
                    rx.table.column_header_cell("Top Product", color="white", font_weight="bold"),
                    rx.table.column_header_cell("Sales", text_align="right", color="white", font_weight="bold"),
                    rx.table.column_header_cell("% Sales", text_align="center", color="white", font_weight="bold"),
                    rx.table.column_header_cell("Total Sale", text_align="center", color="white", font_weight="bold"),
                    bg="slate.800"
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.state_data,
                    lambda row: rx.table.row(
                        rx.table.cell(rx.text(row["state"], font_weight="black", font_size="xs", color=TEXT_COLOR)),
                        rx.table.cell(rx.text(row["product"], font_size="xs", font_weight="medium", color=TEXT_SECONDARY)),
                        rx.table.cell(rx.text(row["formatted_sales"], color="blue.600", font_weight="bold", font_size="xs"), text_align="right"),
                        rx.table.cell(rx.text(row["formatted_pct"], color=TEXT_SECONDARY, font_size="xs", font_weight="bold"), text_align="center"),
                        rx.table.cell(rx.text(row["formatted_total_sales"], color=ACCENT_INDIGO, font_weight="black", font_size="xs"), text_align="center"),
                        border_bottom=f"1px solid {BORDER_COLOR}"
                    )
                )
            ),
            width="100%"
        )
    )

def monthly_summary_table_v2():
    MONTH_COL_WIDTH = "120px"
    return table_container(
        "Monthly Channel Performance Summary",
        rx.vstack(
            # Sub-header
            rx.flex(
                rx.box(rx.text("CHANNEL / STATE", font_weight="black", color="white", font_size="9px", letter_spacing="tight", text_transform="uppercase"), width="240px", min_width="240px", padding_left="4", padding_y="4", border_right="1px solid #334155"),
                rx.foreach(State.summary_table_columns, lambda col: rx.flex(rx.text(col, font_weight="black", color="white", font_size="9px", text_align="right", width="100%"), width=MONTH_COL_WIDTH, min_width=MONTH_COL_WIDTH, flex="none", padding_y="4", padding_right="4", border_right="1px solid #334155", justify="center", align="center")),
                rx.box(rx.text("TOTAL", font_weight="black", color="white", font_size="9px", text_align="right", width="140px", padding_right="4"), width="140px", min_width="140px", padding_y="4", bg="slate.900"),
                bg="slate.800", width="100%", align="center", border_bottom=f"1px solid {BORDER_COLOR}", spacing="0"
            ),
            # Rows
            rx.vstack(
                rx.foreach(
                    State.monthly_summary_data,
                    lambda row: rx.box(
                        rx.cond(
                            row.is_total,
                            rx.flex(
                                rx.box(rx.text(row.channel, font_weight="black", color="white", font_size="sm", text_transform="uppercase"), width="240px", padding_left="4", padding_y="4", border_right="1px solid #334155"),
                                rx.foreach(row.monthly_values, lambda m: rx.flex(rx.text(m.value, color="white", font_size="9px", font_weight="black", text_align="right", width="100%"), width=MONTH_COL_WIDTH, padding_y="4", padding_right="4", border_right="1px solid #334155", justify="center", align="center")),
                                rx.box(rx.text(row.total_value, font_weight="black", color="indigo.300", font_size="sm", text_align="right", width="100%", padding_right="4"), width="140px", padding_y="4", bg="slate.900"),
                                bg="slate.800", width="100%", align="center", border_top=f"1px solid {BORDER_COLOR}",
                            ),
                            rx.accordion.root(
                                rx.accordion.item(
                                    rx.accordion.trigger(
                                        rx.flex(
                                            rx.box(rx.hstack(rx.icon("chevron-down", size=14), rx.text(row.channel, font_weight="black", color=TEXT_COLOR, font_size="sm"), spacing="2", align="center"), width="240px", padding_left="2", padding_y="4", border_right=f"1px solid {BORDER_COLOR}"),
                                            rx.foreach(row.monthly_values, lambda m: rx.flex(rx.text(m.value, color=TEXT_COLOR, font_size="xs", font_weight="bold", text_align="right", width="100%"), width=MONTH_COL_WIDTH, padding_y="4", padding_right="4", border_right=f"1px solid {BORDER_COLOR}", justify="center", align="center")),
                                            rx.box(rx.text(row.total_value, font_weight="black", color=ACCENT_INDIGO, font_size="xs", text_align="right", width="100%", padding_right="4"), width="140px", padding_y="4", bg="slate.50"),
                                            width="100%", align="center", bg="white", _hover={"bg": "slate.50"}
                                        ),
                                        padding="0"
                                    ),
                                    rx.accordion.content(
                                        rx.vstack(
                                            rx.foreach(row.children, lambda child: rx.flex(
                                                rx.box(rx.text(f"• {child.state}", color=TEXT_SECONDARY, font_size="xs", padding_left="10", italic=True), width="240px", padding_y="3", border_right=f"1px solid {BORDER_COLOR}"),
                                                rx.foreach(child.monthly_values, lambda m: rx.flex(rx.text(m.value, color=TEXT_SECONDARY, font_size="xs", text_align="right", width="100%"), width=MONTH_COL_WIDTH, padding_y="3", padding_right="4", border_right=f"1px solid {BORDER_COLOR}")),
                                                rx.box(rx.text(child.total_value, color=TEXT_SECONDARY, font_size="xs", font_weight="bold", text_align="right", width="100%", padding_right="4"), width="140px", padding_y="3"),
                                                bg="slate.50", width="100%", align="center", border_top=f"1px solid {BORDER_COLOR}"
                                            )),
                                            width="100%", spacing="0"
                                        ),
                                        padding="0"
                                    ),
                                    style={"border": "none"}
                                ),
                                type="multiple", collapsible=True, width="100%", variant="ghost"
                            )
                        ),
                        width="100%", border_bottom=f"1px solid {BORDER_COLOR}"
                    )
                ),
                width="100%", spacing="0"
            ),
            width="100%", spacing="0"
        )
    )

def monthly_sales_return_table():
    MONTH_COL_WIDTH = "120px"
    return table_container(
        "Monthly Sales Return (Channel wise)",
        rx.vstack(
             rx.flex(
                rx.box(rx.text("CHANNEL", font_weight="bold", color="white", font_size="9px", letter_spacing="tight"), width="240px", padding_left="4", padding_y="4", border_right="1px solid #334155"),
                rx.foreach(State.summary_table_columns, lambda col: rx.flex(rx.text(col, font_weight="bold", color="white", font_size="9px", text_align="right", width="100%"), width=MONTH_COL_WIDTH, padding_y="4", padding_right="4", border_right="1px solid #334155")),
                rx.box(rx.text("TOTAL", font_weight="bold", color="white", font_size="9px", text_align="right", width="140px", padding_right="4"), width="140px", bg="slate.900", padding_y="4"),
                bg="slate.800", width="100%", align="center", border_bottom=f"1px solid {BORDER_COLOR}"
            ),
            rx.vstack(
                rx.foreach(State.monthly_sales_return_data, lambda row: rx.flex(
                    rx.box(rx.text(row.channel, font_weight="black", color=rx.cond(row.is_total, "white", TEXT_COLOR), font_size="xs", text_transform="uppercase"), width="240px", padding_left="4", padding_y="4", border_right=f"1px solid {BORDER_COLOR}"),
                    rx.foreach(row.monthly_values, lambda m: rx.flex(rx.text(m.value, color=rx.cond(row.is_total, "white", TEXT_SECONDARY), font_size="xs", text_align="right", width="100%"), width=MONTH_COL_WIDTH, padding_y="4", padding_right="4", border_right=f"1px solid {BORDER_COLOR}")),
                    rx.box(rx.text(row.total_value, font_weight="black", color=rx.cond(row.is_total, "indigo.300", ACCENT_INDIGO), font_size="xs", text_align="right", width="100%", padding_right="4"), width="140px", padding_y="4", bg=rx.cond(row.is_total, "slate.900", "slate.50")),
                    bg=rx.cond(row.is_total, "slate.800", "white"), width="100%", align="center", border_bottom=f"1px solid {BORDER_COLOR}"
                )),
                width="100%", spacing="0"
            ),
            width="100%", spacing="0"
        )
    )

def invoice_vs_return_table():
    COL_WIDTH = "68px"
    MONTH_COL_WIDTH = "150px"
    return table_container(
        "Invoice vs Sales Return",
        rx.box(
            rx.flex(
                rx.box(rx.center(rx.text("MONTH", font_weight="bold", color="white", font_size="9px"), height="100%", width="100%"), width=MONTH_COL_WIDTH, min_width=MONTH_COL_WIDTH, border_right="1px solid #334155", height="auto", flex_shrink=0),
                rx.vstack(
                    rx.flex(
                        rx.foreach(State.invoice_return_columns, lambda col: rx.flex(rx.text(col, font_weight="bold", color="white", font_size="9px", text_align="center", width="100%"), width="136px", min_width="136px", flex="none", padding_y="3", border_right="1px solid #334155", justify="center", align="center")), 
                        width="fit-content", spacing="0", flex="1"
                    ), 
                    rx.flex(
                        rx.foreach(State.invoice_return_columns, lambda col: rx.flex(rx.box(rx.text("Inv", color="gray.300", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right="1px solid #334155", padding_y="2"), rx.box(rx.text("Ret", color="#FA5252", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right="1px solid #334155", padding_y="2"), width="136px", min_width="136px", flex="none", justify="center", align="center", spacing="0")), 
                        width="fit-content", border_top="1px solid #334155", spacing="0"
                    ), 
                    spacing="0", width="fit-content"
                ),
                rx.vstack(
                    rx.flex(rx.text("Grand Total", font_weight="bold", color="white", font_size="9px", text_align="center", width="100%"), width="136px", min_width="136px", padding_y="3", border_right="1px solid #334155", justify="center", align="center", flex="1"), 
                    rx.flex(rx.box(rx.text("Inv", color="gray.300", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right="1px solid #334155", padding_y="2"), rx.box(rx.text("Ret", color="#FA5252", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right="1px solid #334155", padding_y="2"), width="136px", min_width="136px", flex="none", justify="center", align="center", spacing="0", border_top="1px solid #334155"), 
                    bg="slate.900", width="fit-content", spacing="0"
                ), 
                bg="slate.800", width="fit-content", align="stretch"
            ),
            rx.vstack(
                rx.foreach(State.invoice_vs_return_data, lambda row: rx.flex(
                    rx.box(rx.text(row.month, font_weight="bold", color=rx.cond(row.is_total, "white", TEXT_COLOR), font_size="9px"), width=MONTH_COL_WIDTH, min_width=MONTH_COL_WIDTH, padding_left="4", padding_y="3", border_right=f"1px solid {BORDER_COLOR}"), 
                    rx.cond(
                        row.is_pct, 
                        rx.foreach(row.channels, lambda chan: rx.flex(rx.text(chan.val, color=chan.color, font_size="9px", font_weight="bold", text_align="center", width="100%"), width="136px", min_width="136px", flex="none", padding_y="2", border_right=f"1px solid {BORDER_COLOR}", justify="center", align="center")), 
                        rx.foreach(row.channels, lambda chan: rx.flex(rx.box(rx.text(chan.inv, color="gray.500", font_size="9px", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"), rx.box(rx.text(chan.ret, color="#FA5252", font_size="9px", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"), width="136px", min_width="136px", flex="none", justify="center", align="center", spacing="0"))
                    ), 
                    rx.flex(
                        rx.cond(
                            row.is_pct,
                            rx.text("-", color="gray.500", font_size="9px", text_align="center", width="100%"),
                            rx.flex(rx.box(rx.text(row.grand_total_inv, color=rx.cond(row.is_total, "white", "gray.500"), font_weight="bold", font_size="9px", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"), rx.box(rx.text(row.grand_total_ret, color="#FA5252", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"), width="136px", min_width="136px", flex="none", justify="center", align="center", spacing="0")
                        ),
                        bg=rx.cond(row.is_total, "slate.900", "slate.50"), width="136px", min_width="136px"
                    ),
                    bg=rx.cond(row.is_total, "slate.800", "white"), width="fit-content", border_bottom=f"1px solid {BORDER_COLOR}", align="center"
                )), 
                width="fit-content", spacing="0"
            ),
            width="100%", overflow="auto"
        )
    )
