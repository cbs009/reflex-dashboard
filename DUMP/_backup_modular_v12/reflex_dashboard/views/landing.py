import reflex as rx
from ..state.metrics import MetricsState as State

def no_data_view() -> rx.Component:
    """The empty state view shown when no data is loaded."""
    return rx.center(
        rx.vstack(
            rx.heading("Upload Your Data", size="8", color="#1A202C", margin_bottom="8px"),
            rx.text(
                "Follow the steps to upload Sales and Courier data.",
                color="#718096",
                font_size="16px",
                margin_bottom="32px",
            ),
            
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("file-spreadsheet", size=24), 
                            rx.text("1. Sales Data", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="sales", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("truck", size=24), 
                            rx.text("2. Courier Data", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="courier", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("bar-chart-2", size=24), 
                            rx.text("3. Analyze", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="analyze", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    justify="center",
                    spacing="8",
                    margin_bottom="32px",
                ),
                
                rx.tabs.content(
                    rx.vstack(
                        rx.box(
                            rx.vstack(
                                rx.icon("file-spreadsheet", size=32, color="#5B45FF"),
                                rx.text("Upload Sales Data Excel File", weight="bold", size="4", color="#1A202C"),
                                rx.text("Required for dashboard visualization", size="2", color="#718096"),
                                rx.cond(
                                    State.sales_data_uploaded,
                                    rx.badge("✅ File Uploaded Successfully", color_scheme="green", variant="solid", size="3"),
                                    rx.fragment()
                                ),
                                rx.upload(
                                     rx.button(
                                        "Select Sales File",
                                        size="3",
                                        variant="solid",
                                        color_scheme="indigo",
                                        width="100%",
                                    ),
                                    id="sales_tab_upload",
                                    accept={
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"], 
                                        "application/vnd.ms-excel": [".xls"]
                                    },
                                    max_files=1,
                                    on_drop=State.handle_sales_upload,
                                    border="1px dashed #CBD5E0",
                                    padding="32px",
                                    border_radius="lg",
                                    width="100%",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            padding="32px",
                            bg="#F7FAFC",
                            border_radius="xl",
                            width="100%",
                            border="1px solid #E2E8F0",
                        ),
                    ),
                    value="sales",
                    padding="24px",
                ),
                
                rx.tabs.content(
                    rx.vstack(
                        rx.box(
                            rx.vstack(
                                rx.icon("truck", size=32, color="#3182CE"),
                                rx.text("Upload Courier Data Excel File", weight="bold", size="4", color="#1A202C"),
                                rx.text("Required for courier performance metrics", size="2", color="#718096"),
                                rx.cond(
                                    State.courier_data_uploaded,
                                    rx.badge("✅ File Uploaded Successfully", color_scheme="green", variant="solid", size="3"),
                                    rx.fragment()
                                ),
                                rx.upload(
                                     rx.button(
                                        "Select Courier File",
                                        size="3",
                                        variant="solid",
                                        color_scheme="blue",
                                        width="100%",
                                    ),
                                    id="courier_tab_upload",
                                    accept={
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"], 
                                        "application/vnd.ms-excel": [".xls"]
                                    },
                                    max_files=1,
                                    on_drop=State.handle_courier_upload,
                                    border="1px dashed #CBD5E0",
                                    padding="32px",
                                    border_radius="lg",
                                    width="100%",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            padding="32px",
                            bg="#F7FAFC",
                            border_radius="xl",
                            width="100%",
                            border="1px solid #E2E8F0",
                        ),
                    ),
                    value="courier",
                    padding="24px",
                ),

                rx.tabs.content(
                     rx.vstack(
                        rx.heading("Ready to Analyze?", size="6", color="#1A202C"),
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Sales Data Status:", weight="bold", color="#1A202C"),
                                    rx.cond(
                                        State.sales_data_uploaded,
                                        rx.badge("Ready", color_scheme="green", variant="solid"),
                                        rx.badge("Missing", color_scheme="red", variant="solid"),
                                    ),
                                    justify="between",
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text("Courier Data Status:", weight="bold", color="#1A202C"),
                                    rx.cond(
                                        State.courier_data_uploaded,
                                        rx.badge("Ready", color_scheme="green", variant="solid"),
                                        rx.badge("Optional", color_scheme="gray", variant="solid"),
                                    ),
                                    justify="between",
                                    width="100%",
                                ),
                                width="100%",
                                spacing="4",
                            ),
                            padding="24px",
                            bg="#F7FAFC",
                            border_radius="lg",
                            width="100%",
                            border="1px solid #E2E8F0",
                        ),
                        rx.button(
                            "Launch Dashboard 🚀", 
                            on_click=State.start_analysis,
                            size="4",
                            width="100%",
                            color_scheme="purple",
                            variant="solid",
                            opacity=rx.cond(State.sales_data_uploaded, "1", "0.5"),
                            cursor=rx.cond(State.sales_data_uploaded, "pointer", "not-allowed"),
                        ),
                        spacing="6",
                        align="center",
                        width="100%",
                    ),
                    value="analyze",
                    padding="24px",
                ),
                
                defaultValue="sales",
                width="100%",
            ),

            rx.cond(
                State.deployment_status != "",
                rx.center(
                    rx.callout.root(
                        rx.callout.text(State.deployment_status),
                        color_scheme="red",
                        role="alert",
                        margin_top="16px",
                    ),
                    width="100%",
                ),
            ),
            align="center",
            width="100%",
            max_width="1000px",
        ),
        width="100%",
        height="100vh",
        background_color="white",
    )
