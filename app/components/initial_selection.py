import reflex as rx
from app.states.app_state import AppState


def initial_selection_component() -> rx.Component:
    """Component for the initial selection between SEO and LTX Bench."""
    return rx.el.div(
        rx.el.h2(
            "Choose Automation",
            class_name="text-3xl font-bold text-center mb-8 text-gray-800",
        ),
        rx.el.div(
            rx.el.button(
                "SEO Automation",
                on_click=lambda: AppState.set_initial_choice(
                    "SEO"
                ),
                class_name="w-full px-8 py-4 bg-violet-600 text-white rounded-lg shadow-md hover:bg-green-700 text-xl font-semibold transition duration-150 ease-in-out",
            ),
            rx.el.button(
                "LTX Bench",
                on_click=lambda: AppState.set_initial_choice(
                    "LTX Bench"
                ),
                class_name="w-full px-8 py-4 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 text-xl font-semibold transition duration-150 ease-in-out",
            ),
            class_name="flex flex-col space-y-6",
        ),
        class_name="max-w-sm mx-auto p-8 bg-white rounded-xl shadow-lg",
    )