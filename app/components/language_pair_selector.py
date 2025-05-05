import reflex as rx
from app.states.file_prep_state import FilePrepState
from typing import Optional


def language_select(
    placeholder: str,
    value_var: rx.Var[Optional[str]],
    on_change_handler: rx.EventHandler,
) -> rx.Component:
    """Creates a language selection dropdown."""
    return rx.el.select(
        rx.el.option(placeholder, value="", disabled=True),
        rx.foreach(
            FilePrepState.available_languages,
            lambda lang: rx.el.option(lang, value=lang),
        ),
        value=rx.cond(value_var, value_var, ""),
        on_change=on_change_handler,
        class_name="w-full p-2 border border-gray-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-blue-500",
    )


def language_pair_selector() -> rx.Component:
    """Component for selecting source and target language pairs."""
    return rx.el.div(
        rx.el.h4(
            "Select Language Pairs",
            class_name="text-xl font-medium mb-4 text-gray-700",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Source Language",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                language_select(
                    "Select Source...",
                    FilePrepState.current_source_language,
                    FilePrepState.set_current_source_language,
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Target Language",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                language_select(
                    "Select Target...",
                    FilePrepState.current_target_language,
                    FilePrepState.set_current_target_language,
                ),
                class_name="flex-1",
            ),
            rx.el.button(
                "Add Pair",
                on_click=FilePrepState.add_language_pair,
                disabled=FilePrepState.is_add_pair_disabled,
                class_name="mt-6 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            class_name="flex items-end space-x-4 mb-6",
        ),
        rx.el.h5(
            "Selected Pairs:",
            class_name="text-lg font-medium mb-2 text-gray-600",
        ),
        rx.el.ul(
            rx.foreach(
                FilePrepState.selected_pairs_for_session,
                lambda pair: rx.el.li(
                    rx.el.span(
                        f"{pair[0]} -> {pair[1]}",
                        class_name="flex-grow",
                    ),
                    rx.el.button(
                        "Remove",
                        on_click=lambda: FilePrepState.remove_language_pair(
                            pair
                        ),
                        class_name="ml-4 px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600",
                    ),
                    class_name="flex justify-between items-center p-2 border-b border-gray-200",
                ),
            ),
            rx.cond(
                FilePrepState.selected_pairs_for_session.length()
                == 0,
                rx.el.li(
                    "No pairs added yet.",
                    class_name="text-gray-500 italic p-2",
                ),
                rx.fragment(),
            ),
            class_name="list-none p-0 mb-6 max-h-60 overflow-y-auto border border-gray-200 rounded",
        ),
        rx.el.button(
            "Confirm Language Pairs",
            on_click=FilePrepState.confirm_language_pairs,
            disabled=FilePrepState.is_confirm_pairs_disabled,
            class_name="w-full px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed",
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50",
    )