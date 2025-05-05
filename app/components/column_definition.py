import reflex as rx
from app.states.file_prep_state import (
    FilePrepState,
    ExcelColumn,
)
from typing import Dict


def column_item(
    column: ExcelColumn, index: int
) -> rx.Component:
    """Displays a single column item with controls for reordering and editing."""
    is_editing = FilePrepState.editing_column_index == index
    is_first = index == 0
    is_last = (
        index == FilePrepState.excel_columns.length() - 1
    )
    return rx.el.li(
        rx.el.div(
            rx.cond(
                is_editing,
                rx.el.div(
                    rx.el.input(
                        default_value=FilePrepState.editing_column_name,
                        on_change=FilePrepState.set_editing_column_name,
                        on_blur=FilePrepState.save_column_name,
                        on_key_down=lambda key_pressed: rx.cond(
                            key_pressed == "Enter",
                            FilePrepState.save_column_name,
                            rx.cond(
                                key_pressed == "Escape",
                                FilePrepState.cancel_editing_column_name,
                                rx.noop(),
                            ),
                        ),
                        placeholder="Enter column name",
                        class_name="p-1 border border-blue-500 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 flex-grow",
                        auto_focus=True,
                    ),
                    rx.el.button(
                        rx.icon(tag="check"),
                        on_click=FilePrepState.save_column_name,
                        class_name="ml-1 px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600",
                    ),
                    rx.el.button(
                        rx.icon(tag="x"),
                        on_click=FilePrepState.cancel_editing_column_name,
                        class_name="ml-1 px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600",
                    ),
                    class_name="flex items-center w-full",
                ),
                rx.el.span(
                    column["name"],
                    class_name="font-medium text-gray-800 flex-grow",
                    on_double_click=lambda: FilePrepState.start_editing_column_name(
                        index
                    ),
                ),
            ),
            class_name="flex-1 min-w-0 mr-4",
        ),
        rx.el.div(
            rx.cond(
                ~is_editing,
                rx.fragment(
                    rx.el.button(
                        rx.icon(tag="chevron-up"),
                        on_click=lambda: FilePrepState.move_column(
                            index, "up"
                        ),
                        disabled=is_first,
                        class_name="p-1 text-gray-500 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed",
                    ),
                    rx.el.button(
                        rx.icon(tag="chevron-down"),
                        on_click=lambda: FilePrepState.move_column(
                            index, "down"
                        ),
                        disabled=is_last,
                        class_name="p-1 text-gray-500 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed",
                    ),
                    rx.cond(
                        column["editable"],
                        rx.el.button(
                            rx.icon(tag="pencil"),
                            on_click=lambda: FilePrepState.start_editing_column_name(
                                index
                            ),
                            class_name="ml-2 p-1 text-blue-500 hover:text-blue-700",
                        ),
                        rx.fragment(),
                    ),
                ),
                rx.fragment(),
            ),
            class_name="flex items-center",
        ),
        class_name="flex justify-between items-center p-3 border-b border-gray-200 last:border-b-0 bg-white hover:bg-gray-50",
    )


def column_definition_component() -> rx.Component:
    """Component for defining and ordering Excel columns."""
    return rx.el.div(
        rx.el.h4(
            "Define Excel Export Columns",
            class_name="text-xl font-medium mb-4 text-gray-700",
        ),
        rx.el.p(
            "Arrange and rename the columns for the evaluation Excel file. Double-click an editable name to change it.",
            class_name="text-sm text-gray-600 mb-6",
        ),
        rx.el.ul(
            rx.foreach(
                FilePrepState.excel_columns, column_item
            ),
            class_name="list-none p-0 mb-6 border border-gray-200 rounded shadow-sm max-h-96 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.button(
                "⬅ Edit Metrics & Weighting",
                on_click=lambda: FilePrepState.set_metrics_confirmed(
                    False
                ),
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
            ),
            rx.el.button(
                "Confirm Columns ➡",
                on_click=FilePrepState.confirm_columns,
                disabled=FilePrepState.is_confirm_columns_disabled,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150",
            ),
            class_name="flex justify-between items-center mt-6 border-t border-gray-200 pt-4",
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50 shadow",
    )