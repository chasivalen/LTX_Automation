import reflex as rx
from app.states.app_state import AppState
from app.states.project_state import ProjectState


def header_component() -> rx.Component:
    """The dynamic header component."""
    return rx.el.div(
        rx.el.h1(
            "LTX Automation",
            class_name="text-2xl font-bold text-gray-900",
        ),
        rx.el.div(
            rx.match(
                AppState.initial_choice,
                (
                    "SEO",
                    rx.el.span(
                        "Mode: SEO",
                        class_name="text-sm font-medium text-green-700 bg-green-100 px-2 py-1 rounded",
                    ),
                ),
                (
                    "LTX Bench",
                    rx.cond(
                        AppState.project_selected,
                        rx.el.span(
                            f"Project: {ProjectState.selected_project}",
                            class_name="text-sm font-medium text-blue-700 bg-blue-100 px-2 py-1 rounded",
                        ),
                        rx.el.span(
                            "Mode: LTX Bench (No Project)",
                            class_name="text-sm font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded",
                        ),
                    ),
                ),
                rx.el.span(
                    "Select Automation",
                    class_name="text-sm font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded",
                ),
            ),
            class_name="flex items-center space-x-4",
        ),
        rx.cond(
            AppState.initial_choice != None,
            rx.el.button(
                "⬅ Back / Change Mode",
                on_click=AppState.reset_initial_choice,
                class_name="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300",
            ),
            rx.fragment(),
        ),
        class_name="fixed top-0 left-0 right-0 h-16 px-6 flex items-center justify-between bg-white border-b border-gray-200 z-10",
    )