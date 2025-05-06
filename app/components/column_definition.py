import reflex as rx
from app.states.file_prep_state import (
    FilePrepState,
    ExcelColumn,
    ColumnGroup,
)
from typing import List, Tuple


def column_card_item(
    column: rx.Var[ExcelColumn],
) -> rx.Component:
    """Displays a single column item as a card within its group."""
    is_editing = (
        FilePrepState.editing_column_id == column["id"]
    )
    is_first_in_movable_group = column[
        "is_first_movable_in_group"
    ]
    is_last_in_movable_group = column[
        "is_last_movable_in_group"
    ]
    has_formula = rx.cond(
        column["formula_description"],
        column["formula_description"].length() > 0,
        False,
    )
    is_removable = column.get("removable", False)
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
                    ),
                    rx.el.button(
                        rx.icon(tag="x", size=16),
                        on_click=FilePrepState.cancel_editing_column_name,
                        class_name="ml-1 px-1.5 py-1 bg-red-500 text-white rounded hover:bg-red-600",
                    ),
                    class_name="flex items-center w-full mb-1",
                ),
                rx.el.div(
                    rx.el.h6(
                        column["name"],
                        class_name=rx.cond(
                            column["editable_name"],
                            "font-semibold text-gray-800 text-md cursor-pointer hover:text-blue-600",
                            "font-semibold text-gray-700 text-md italic",
                        ),
                        on_double_click=rx.cond(
                            column["editable_name"],
                            FilePrepState.start_editing_column_name(
                                column["id"]
                            ),
                            rx.noop(),
                        ),
                    ),
                    rx.cond(
                        has_formula,
                        rx.el.button(
                            rx.icon(
                                tag="info",
                                size=14,
                                class_name="text-blue-500",
                            ),
                            on_click=lambda: FilePrepState.show_formula_info(
                                column["id"]
                            ),
                            class_name="ml-2 p-1 hover:bg-blue-100 rounded-full",
                            title="View Formula Info",
                        ),
                        rx.fragment(),
                    ),
                    class_name="flex items-center",
                ),
            ),
            rx.el.p(
                column["description"],
                class_name="text-xs text-gray-500 mt-1",
            ),
            class_name="flex-grow",
        ),
        rx.el.div(
            rx.cond(
                ~is_editing,
                rx.el.div(
                    rx.cond(
                        column["editable_name"],
                        rx.el.button(
                            rx.icon(tag="pencil", size=14),
                            on_click=lambda: FilePrepState.start_editing_column_name(
                                column["id"]
                            ),
                            class_name="p-1 text-blue-500 hover:text-blue-700",
                            title="Edit Name",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        column["movable_within_group"],
                        rx.fragment(
                            rx.el.button(
                                rx.icon(
                                    tag="chevron-up",
                                    size=14,
                                ),
                                on_click=lambda: FilePrepState.move_column(
                                    column["id"], "left"
                                ),
                                disabled=is_first_in_movable_group,
                                class_name="p-1 text-gray-500 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed",
                                title="Move Up",
                            ),
                            rx.el.button(
                                rx.icon(
                                    tag="chevron-down",
                                    size=14,
                                ),
                                on_click=lambda: FilePrepState.move_column(
                                    column["id"], "right"
                                ),
                                disabled=is_last_in_movable_group,
                                class_name="p-1 text-gray-500 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed",
                                title="Move Down",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        is_removable,
                        rx.el.button(
                            rx.icon(tag="trash-2", size=14),
                            on_click=lambda: FilePrepState.remove_column_by_id(
                                column["id"]
                            ),
                            class_name="p-1 text-red-500 hover:text-red-700",
                            title="Remove Column",
                        ),
                        rx.fragment(),
                    ),
                    class_name="flex items-center space-x-1",
                ),
                rx.fragment(),
            ),
            class_name="mt-2 flex justify-end",
        ),
        class_name=rx.cond(
            column["metric_source"],
            "p-3 border border-dashed border-green-400 rounded bg-green-50 shadow-sm mb-2 flex flex-col justify-between",
            rx.cond(
                column["custom_user_added"],
                "p-3 border border-dashed border-purple-400 rounded bg-purple-50 shadow-sm mb-2 flex flex-col justify-between",
                "p-3 border border-gray-300 rounded bg-white shadow-sm mb-2 flex flex-col justify-between",
            ),
        ),
    )


def column_group_section(
    group_data: rx.Var[
        Tuple[ColumnGroup, List[ExcelColumn]]
    ],
) -> rx.Component:
    group_name: rx.Var[ColumnGroup] = group_data[0]
    columns_in_group: rx.Var[List[ExcelColumn]] = (
        group_data[1]
    )
    can_add_to_group = group_name != "Metric"
    return rx.el.div(
        rx.el.h5(
            group_name,
            class_name="text-lg font-semibold mb-3 text-gray-700 capitalize p-2 bg-gray-100 rounded-t-md border-b border-gray-200",
        ),
        rx.el.div(
            rx.cond(
                columns_in_group.length() > 0,
                rx.foreach(
                    columns_in_group, column_card_item
                ),
                rx.el.p(
                    "No columns in this group.",
                    class_name="text-sm text-gray-500 p-3 italic",
                ),
            ),
            rx.cond(
                can_add_to_group,
                rx.el.div(
                    rx.el.input(
                        placeholder=f"New column name for {group_name}",
                        default_value=FilePrepState.new_column_inputs[
                            group_name
                        ],
                        on_change=lambda val: FilePrepState.set_new_column_input_for_group(
                            group_name, val
                        ),
                        class_name="flex-grow p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm mr-2",
                    ),
                    rx.el.button(
                        "Add Column",
                        on_click=lambda: FilePrepState.add_new_column_to_group(
                            group_name
                        ),
                        class_name="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm",
                        disabled=FilePrepState.new_column_inputs[
                            group_name
                        ].length()
                        == 0,
                    ),
                    class_name="mt-3 p-3 border-t border-gray-200 flex items-center",
                ),
                rx.fragment(),
            ),
            class_name="p-3",
        ),
        class_name="mb-6 border border-gray-200 rounded-md shadow",
    )


def formula_info_dialog() -> rx.Component:
    """Dialog to display formula information for a selected column."""
    return rx.el.dialog(
        rx.cond(
            FilePrepState.selected_column_for_formula,
            rx.el.div(
                rx.el.h3(
                    "Formula Information: ",
                    rx.el.span(
                        FilePrepState.selected_column_for_formula[
                            "name"
                        ],
                        class_name="font-bold",
                    ),
                    class_name="text-xl font-semibold text-gray-800 mb-4",
                ),
                rx.el.div(
                    rx.el.h4(
                        "Description:",
                        class_name="text-md font-medium text-gray-700 mb-1",
                    ),
                    rx.el.p(
                        FilePrepState.selected_column_for_formula[
                            "formula_description"
                        ],
                        class_name="text-sm text-gray-600 bg-gray-50 p-2 rounded border",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.h4(
                        "Excel-style Formula:",
                        class_name="text-md font-medium text-gray-700 mb-1",
                    ),
                    rx.el.code(
                        FilePrepState.selected_column_for_formula[
                            "formula_excel_style"
                        ],
                        class_name="text-sm text-purple-700 bg-purple-50 p-2 rounded border border-purple-200 block whitespace-pre-wrap",
                    ),
                    class_name="mb-6",
                ),
                rx.el.button(
                    "Close",
                    on_click=FilePrepState.hide_formula_info,
                    class_name="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400",
                ),
                class_name="flex flex-col",
            ),
            rx.el.p(
                "No column selected for formula information.",
                class_name="text-gray-500",
            ),
        ),
        open=FilePrepState.show_formula_modal,
        class_name="bg-white shadow-xl rounded-lg border border-slate-200 p-6 max-w-lg mx-auto transform transition-all duration-300 ease-in-out z-50",
    )


def formula_review_view() -> rx.Component:
    """Component for reviewing columns with formulas before final confirmation."""
    return rx.el.div(
        rx.el.h4(
            "Review Column Formulas",
            class_name="text-xl font-medium mb-2 text-gray-700",
        ),
        rx.el.p(
            "Please review the formulas for the following columns. Ensure they are correct based on their definitions.",
            class_name="text-sm text-gray-600 mb-6",
        ),
        rx.cond(
            FilePrepState.columns_with_formulas.length()
            > 0,
            rx.el.div(
                rx.foreach(
                    FilePrepState.columns_with_formulas,
                    lambda col: rx.el.div(
                        rx.el.h5(
                            col["name"],
                            class_name="text-lg font-semibold text-gray-800 mb-1",
                        ),
                        rx.el.div(
                            rx.el.strong(
                                "Definition: ",
                                class_name="text-gray-600",
                            ),
                            rx.el.p(
                                rx.cond(
                                    col[
                                        "formula_description"
                                    ],
                                    col[
                                        "formula_description"
                                    ],
                                    "N/A",
                                ),
                                class_name="text-sm text-gray-500 italic",
                            ),
                            class_name="mb-2",
                        ),
                        rx.el.div(
                            rx.el.strong(
                                "Excel Formula: ",
                                class_name="text-gray-600",
                            ),
                            rx.el.code(
                                rx.cond(
                                    col[
                                        "formula_excel_style"
                                    ],
                                    col[
                                        "formula_excel_style"
                                    ],
                                    "N/A",
                                ),
                                class_name="text-sm text-purple-600 bg-purple-50 p-1 rounded border border-purple-100 block whitespace-pre",
                            ),
                        ),
                        class_name="p-4 border border-gray-200 rounded-md bg-white shadow-sm mb-4",
                    ),
                ),
                class_name="space-y-4",
            ),
            rx.el.p(
                "No columns with formulas to review.",
                class_name="text-gray-500 italic",
            ),
        ),
        rx.el.div(
            rx.el.button(
                "⬅ Back to Edit Columns",
                on_click=FilePrepState.back_to_edit_columns_from_review,
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
            ),
            rx.el.button(
                "Finalize Column Configuration ➡",
                on_click=FilePrepState.finalize_column_configuration,
                class_name="px-6 py-3 bg-green-600 text-white rounded-lg shadow font-medium hover:bg-green-700 transition duration-150",
            ),
            class_name="flex justify-between items-center mt-8 border-t border-gray-200 pt-6",
        ),
        class_name="p-6 border border-gray-200 rounded-lg bg-gray-50 shadow-lg",
    )


def main_column_definition_ui() -> rx.Component:
    """The main UI for defining columns, shown when not in formula review."""
    return rx.el.div(
        rx.el.h4(
            "Define Excel Export Columns",
            class_name="text-xl font-medium mb-2 text-gray-700",
        ),
        rx.el.p(
            "Columns are grouped by functionality. You can rename editable columns by double-clicking their name.",
            class_name="text-sm text-gray-600 mb-1",
        ),
        rx.el.p(
            "Use the up/down arrows to reorder movable columns within their respective groups.",
            class_name="text-sm text-gray-600 mb-1",
        ),
        rx.el.p(
            "Click the ",
            rx.icon(
                tag="trash-2",
                size=12,
                class_name="inline-block mx-0.5",
            ),
            " icon to remove a column (if removable). User-added columns are highlighted in purple.",
            class_name="text-sm text-gray-600 mb-1",
        ),
        rx.el.p(
            "Click the ",
            rx.icon(
                tag="info",
                size=12,
                class_name="inline-block mx-0.5",
            ),
            " icon next to a column name to view its formula logic (if applicable).",
            class_name="text-sm text-gray-600 mb-1",
        ),
        rx.el.p(
            "Metric columns (green dashed border) are added based on prior selections and cannot be edited, moved, or removed here.",
            class_name="text-xs text-gray-500 mb-6 italic",
        ),
        rx.foreach(
            FilePrepState.final_excel_columns_for_display,
            column_group_section,
        ),
        formula_info_dialog(),
        rx.el.div(
            rx.el.button(
                "⬅ Edit Metrics & Weighting",
                on_click=lambda: FilePrepState.set_metrics_confirmed(
                    False
                ),
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
            ),
            rx.el.button(
                "Proceed to Formula Review ➡",
                on_click=FilePrepState.proceed_to_formula_review,
                disabled=FilePrepState.is_proceed_to_review_disabled,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150",
            ),
            class_name="flex justify-between items-center mt-6 border-t border-gray-200 pt-4",
        ),
    )


def column_definition_component() -> rx.Component:
    """Component for defining Excel columns, grouped by functionality, and reviewing formulas."""
    return rx.el.div(
        rx.cond(
            FilePrepState.formula_review_active,
            formula_review_view(),
            main_column_definition_ui(),
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50 shadow",
    )