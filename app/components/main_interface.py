import reflex as rx
from app.states.project_state import ProjectState
from app.states.app_state import AppState


def main_interface_component() -> rx.Component:
    """Component displayed after project selection."""
    return rx.el.div(
        rx.el.h3(
            f"Project: {ProjectState.selected_project}",
            class_name="text-2xl font-semibold mb-6 text-gray-800",
        ),
        rx.el.div(
            rx.el.h4(
                "LTX Bench",
                class_name="text-xl font-medium mb-3 text-gray-700",
            ),
            rx.el.ul(
                rx.el.li(
                    rx.el.button(
                        "File Prep",
                        on_click=rx.toast(
                            "File Prep selected (placeholder)"
                        ),
                        class_name="w-full text-left px-4 py-2 mb-2 bg-gray-100 hover:bg-gray-200 rounded border border-gray-300",
                    )
                ),
                rx.el.li(
                    rx.el.button(
                        "Final File Prep",
                        on_click=rx.toast(
                            "Final File Prep selected (placeholder)"
                        ),
                        class_name="w-full text-left px-4 py-2 mb-2 bg-gray-100 hover:bg-gray-200 rounded border border-gray-300",
                    )
                ),
                rx.el.li(
                    rx.el.button(
                        "Update Tableau",
                        on_click=rx.toast(
                            "Update Tableau selected (placeholder)"
                        ),
                        class_name="w-full text-left px-4 py-2 mb-2 bg-gray-100 hover:bg-gray-200 rounded border border-gray-300",
                    )
                ),
                class_name="list-none p-0",
            ),
            class_name="mb-6 p-4 bg-white rounded-lg shadow",
        ),
        rx.el.div(
            rx.el.h4(
                "SEO Automation",
                class_name="text-xl font-medium mb-3 text-gray-700",
            ),
            rx.el.p(
                "Placeholder for SEO Automation features.",
                class_name="text-gray-600",
            ),
            class_name="p-4 bg-white rounded-lg shadow",
        ),
        rx.el.button(
            "Change Project",
            on_click=lambda: AppState.set_project_selected(
                False
            ),
            class_name="mt-6 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600",
        ),
        class_name="p-6 max-w-2xl mx-auto",
    )