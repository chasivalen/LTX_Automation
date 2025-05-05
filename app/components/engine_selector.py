import reflex as rx
from app.states.file_prep_state import FilePrepState


def engine_checkbox(engine_name: str) -> rx.Component:
    """Creates a checkbox-like button for selecting predefined engines."""
    is_selected = FilePrepState.selected_engines.contains(
        engine_name
    )
    return rx.el.button(
        engine_name,
        on_click=lambda: FilePrepState.toggle_engine(
            engine_name
        ),
        class_name=rx.cond(
            is_selected,
            "px-4 py-2 bg-blue-200 text-blue-800 border border-blue-400 rounded font-medium",
            "px-4 py-2 bg-gray-100 text-gray-700 border border-gray-300 rounded hover:bg-gray-200",
        ),
    )


def engine_selector_component() -> rx.Component:
    """Component for selecting and confirming MT engines."""
    return rx.el.div(
        rx.el.h4(
            "Select MT Engines",
            class_name="text-xl font-medium mb-4 text-gray-700",
        ),
        rx.el.div(
            rx.el.h5(
                "Available Engines:",
                class_name="text-lg font-medium mb-2 text-gray-600",
            ),
            rx.el.div(
                rx.foreach(
                    FilePrepState.available_engines,
                    engine_checkbox,
                ),
                class_name="flex flex-wrap gap-2 mb-6",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.h5(
                "Add Custom Engine:",
                class_name="text-lg font-medium mb-2 text-gray-600",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Enter custom engine name",
                    default_value=FilePrepState.new_engine_name,
                    on_change=FilePrepState.set_new_engine_name,
                    class_name="flex-grow p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                rx.el.button(
                    "Add Engine",
                    on_click=FilePrepState.add_custom_engine,
                    disabled=FilePrepState.is_add_engine_disabled,
                    class_name="ml-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed",
                ),
                class_name="flex items-center",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.h5(
                "Selected Engines:",
                class_name="text-lg font-medium mb-2 text-gray-600",
            ),
            rx.el.ul(
                rx.foreach(
                    FilePrepState.selected_engines,
                    lambda engine: rx.el.li(
                        rx.el.span(
                            engine, class_name="flex-grow"
                        ),
                        rx.el.button(
                            "Remove",
                            on_click=lambda: FilePrepState.remove_engine(
                                engine
                            ),
                            class_name="ml-4 px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600",
                        ),
                        class_name="flex justify-between items-center p-2 border-b border-gray-200",
                    ),
                ),
                rx.cond(
                    FilePrepState.selected_engines.length()
                    == 0,
                    rx.el.li(
                        "No engines selected yet.",
                        class_name="text-gray-500 italic p-2",
                    ),
                    rx.fragment(),
                ),
                class_name="list-none p-0 mb-6 max-h-60 overflow-y-auto border border-gray-200 rounded",
            ),
        ),
        rx.el.div(
            rx.el.button(
                "⬅ Edit Language Pairs",
                on_click=lambda: FilePrepState.set_pairs_confirmed(
                    False
                ),
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600",
            ),
            rx.el.button(
                "Confirm Engines",
                on_click=FilePrepState.confirm_engines,
                disabled=FilePrepState.is_confirm_engines_disabled,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            class_name="flex justify-between items-center mt-6",
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50",
    )