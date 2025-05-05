import reflex as rx
from app.states.file_prep_state import (
    FilePrepState,
    ExcelColumn,
)
from typing import Optional


def column_item(column: ExcelColumn) -> rx.Component:
    """Displays a single column item horizontally as a card."""
    is_editing = (
        FilePrepState.editing_column_id == column["id"]
    )
    original_index_var = column["original_index"]
    is_editable_with_index = column["editable"] & (
        original_index_var != None
    )
    is_first = is_editable_with_index & (
        original_index_var == 0
    )
    is_last = is_editable_with_index & (
        original_index_var
        == FilePrepState.excel_columns.length() - 1
    )
    can_trigger_edit = column["editable"]
    return rx.el.div(
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
                        class_name="p-1 border border-blue-500 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 flex-grow text-sm",
                        auto_focus=True,
                    ),
                    rx.el.button(
                        rx.icon(tag="check", size=16),
                        on_click=FilePrepState.save_column_name,
                        class_name="ml-1 px-1.5 py-1 bg-green-500 text-white rounded hover:bg-green-600",
                        size="1",
                    ),
                    rx.el.button(
                        rx.icon(tag="x", size=16),
                        on_click=FilePrepState.cancel_editing_column_name,
                        class_name="ml-1 px-1.5 py-1 bg-red-500 text-white rounded hover:bg-red-600",
                        size="1",
                    ),
                    class_name="flex items-center w-full",
                ),
                rx.el.span(
                    column["name"],
                    class_name=rx.cond(
                        can_trigger_edit,
                        "font-medium text-gray-800 text-sm cursor-pointer hover:text-blue-600",
                        "font-medium text-gray-600 text-sm italic",
                    ),
                    on_double_click=rx.cond(
                        can_trigger_edit,
                        FilePrepState.start_editing_column_name(
                            column["id"]
                        ),
                        rx.noop(),
                    ),
                ),
            ),
            class_name="flex-1 min-w-0 mb-2 pb-2 border-b border-gray-200",
        ),
        rx.el.div(
            rx.cond(
                ~is_editing & is_editable_with_index,
                rx.fragment(
                    rx.el.button(
                        rx.icon(
                            tag="chevron-left", size=16
                        ),
                        on_click=lambda: FilePrepState.move_column(
                            column["id"], "left"
                        ),
                        disabled=is_first,
                        class_name="p-1 text-gray-500 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed",
                        size="1",
                    ),
                    rx.el.button(
                        rx.icon(tag="pencil", size=16),
                        on_click=lambda: FilePrepState.start_editing_column_name(
                            column["id"]
                        ),
                        class_name="p-1 text-blue-500 hover:text-blue-700",
                        size="1",
                    ),
                    rx.el.button(
                        rx.icon(
                            tag="chevron-right", size=16
                        ),
                        on_click=lambda: FilePrepState.move_column(
                            column["id"], "right"
                        ),
                        disabled=is_last,
                        class_name="p-1 text-gray-500 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed",
                        size="1",
                    ),
                ),
                rx.fragment(),
            ),
            class_name="flex items-center justify-between h-8",
        ),
        class_name=rx.cond(
            column["metric_source"],
            "flex-shrink-0 w-40 h-24 p-3 border border-dashed border-green-400 rounded bg-green-50 shadow flex flex-col justify-between",
            "flex-shrink-0 w-40 h-24 p-3 border border-gray-300 rounded bg-white shadow flex flex-col justify-between",
        ),
    )


def column_definition_component() -> rx.Component:
    """Component for defining and ordering Excel columns horizontally."""
    return rx.el.div(
        rx.el.h4(
            "Define Excel Export Columns",
            class_name="text-xl font-medium mb-2 text-gray-700",
        ),
        rx.el.p(
            "Arrange the standard columns using arrows. Double-click a standard column name to edit it.",
            class_name="text-sm text-gray-600 mb-1",
        ),
        rx.el.p(
            "Metric columns (dashed green border) are added automatically based on the previous step and cannot be moved or edited here.",
            class_name="text-xs text-gray-500 mb-6 italic",
        ),
        rx.el.div(
            rx.el.div(
                rx.foreach(
                    FilePrepState.display_excel_columns,
                    column_item,
                ),
                class_name="flex space-x-4 p-2",
            ),
            class_name="mb-6 border border-gray-200 rounded shadow-sm bg-gray-100 overflow-x-auto",
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