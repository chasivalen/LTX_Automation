import reflex as rx
from app.states.file_prep_state import (
    FilePrepState,
    ExcelColumn,
    ColumnGroup,
    COLUMN_GROUPS_ORDER,
)
from typing import cast


def _icon_button(
    icon_name: str,
    on_click_event,
    tooltip: str,
    disabled: rx.Var[bool] | bool = False,
    extra_class_name: str = "",
) -> rx.Component:
    """Helper for creating small icon buttons."""
    return rx.el.button(
        rx.icon(tag=icon_name, class_name="w-4 h-4"),
        on_click=on_click_event,
        title=tooltip,
        disabled=disabled,
        class_name=f"p-1 text-gray-600 hover:text-blue-600 disabled:text-gray-300 disabled:cursor-not-allowed {extra_class_name}",
    )


def _column_item_component(
    col_data_tuple: tuple[ExcelColumn, ColumnGroup],
) -> rx.Component:
    """Renders a single column item within its group for editing."""
    col_data = col_data_tuple[0]
    is_editing_this_column_name = (
        FilePrepState.editing_column_id == col_data["id"]
    )
    return rx.el.div(
        rx.el.div(
            rx.cond(
                is_editing_this_column_name,
                rx.el.div(
                    rx.el.input(
                        default_value=FilePrepState.editing_column_name,
                        on_change=FilePrepState.set_editing_column_name,
                        placeholder="Column Name",
                        class_name="flex-grow p-1 border border-blue-400 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm",
                    ),
                    _icon_button(
                        "check",
                        FilePrepState.save_column_name,
                        "Save Name",
                        extra_class_name="ml-1 text-green-600 hover:text-green-700",
                    ),
                    _icon_button(
                        "x",
                        FilePrepState.cancel_editing_column_name,
                        "Cancel Edit",
                        extra_class_name="text-red-600 hover:text-red-700",
                    ),
                    class_name="flex items-center w-full",
                ),
                rx.el.span(
                    col_data["name"],
                    class_name="font-medium text-gray-800",
                ),
            ),
            class_name="flex-grow min-w-0 pr-2",
        ),
        rx.el.div(
            rx.cond(
                col_data.get("editable_name", False)
                & ~is_editing_this_column_name,
                _icon_button(
                    "pencil",
                    lambda: FilePrepState.start_editing_column_name(
                        cast(str, col_data["id"])
                    ),
                    "Edit Name",
                ),
                rx.fragment(),
            ),
            rx.cond(
                col_data.get("movable_within_group", False)
                & ~col_data.get(
                    "is_first_movable_in_group", False
                ),
                _icon_button(
                    "arrow-up",
                    lambda: FilePrepState.move_column(
                        cast(str, col_data["id"]), "left"
                    ),
                    "Move Up",
                ),
                rx.el.div(class_name="w-7 h-7"),
            ),
            rx.cond(
                col_data.get("movable_within_group", False)
                & ~col_data.get(
                    "is_last_movable_in_group", False
                ),
                _icon_button(
                    "arrow-down",
                    lambda: FilePrepState.move_column(
                        cast(str, col_data["id"]), "right"
                    ),
                    "Move Down",
                ),
                rx.el.div(class_name="w-7 h-7"),
            ),
            rx.cond(
                col_data.get("formula_description")
                | col_data.get("formula_excel_style"),
                _icon_button(
                    "square_sigma",
                    lambda: FilePrepState.show_formula_info(
                        cast(str, col_data["id"])
                    ),
                    "View Formula",
                ),
                rx.fragment(),
            ),
            rx.cond(
                col_data.get("removable", False),
                _icon_button(
                    "square-x",
                    lambda: FilePrepState.remove_column_by_id(
                        cast(str, col_data["id"])
                    ),
                    "Remove Column",
                    extra_class_name="text-red-500 hover:text-red-700",
                ),
                rx.fragment(),
            ),
            class_name="flex items-center space-x-1 flex-shrink-0",
        ),
        class_name="flex justify-between items-center p-2 border-b border-gray-200 last:border-b-0 hover:bg-gray-50 text-sm",
    )


def _column_group_component(
    group_data_tuple: tuple[ColumnGroup, list[ExcelColumn]],
) -> rx.Component:
    """Renders a group of columns with an option to add a new column."""
    group_name = group_data_tuple[0]
    columns_in_group = group_data_tuple[1]
    return rx.el.div(
        rx.el.h6(
            group_name,
            class_name="text-md font-semibold mb-2 text-gray-700 px-2 pt-2",
        ),
        rx.el.div(
            rx.foreach(
                columns_in_group,
                lambda col: _column_item_component(
                    (col, group_name)
                ),
            ),
            class_name="border border-gray-200 rounded bg-white shadow-sm",
        ),
        rx.cond(
            group_name != "Metric",
            rx.el.div(
                rx.el.input(
                    placeholder=f"Add new column to {group_name}",
                    default_value=FilePrepState.new_column_inputs.get(
                        group_name, ""
                    ),
                    on_change=lambda val: FilePrepState.set_new_column_input_for_group(
                        group_name, val
                    ),
                    class_name="flex-grow p-2 border border-gray-300 rounded-l focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm",
                ),
                rx.el.button(
                    "Add",
                    on_click=lambda: FilePrepState.add_new_column_to_group(
                        group_name
                    ),
                    class_name="px-3 py-2 bg-green-500 text-white rounded-r hover:bg-green-600 text-sm",
                ),
                class_name="flex mt-2 mb-4 px-1",
            ),
            rx.fragment(),
        ),
        class_name="mb-4",
    )


def _column_editor_view() -> rx.Component:
    """View for editing the main column structure."""
    return rx.el.div(
        rx.el.p(
            "Arrange, rename, add, or remove columns for your evaluation template. Metric columns are automatically added based on your selections in the previous step.",
            class_name="text-sm text-gray-600 mb-4",
        ),
        rx.foreach(
            FilePrepState.final_excel_columns_for_display,
            _column_group_component,
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
                rx.cond(
                    FilePrepState.columns_with_formulas.length()
                    > 0,
                    "Review Formulas & Pre-load Template ➡",
                    "Pre-load Template ➡",
                ),
                on_click=FilePrepState.proceed_from_column_editor,
                disabled=FilePrepState.is_proceed_from_column_editor_disabled,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150",
            ),
            class_name="flex justify-between items-center mt-6 border-t border-gray-200 pt-4",
        ),
    )


def _formula_review_item_component(
    col_data: ExcelColumn,
) -> rx.Component:
    """Displays a column with its formula for review and editing."""
    is_editing_this_formula = (
        FilePrepState.editing_formula_column_id
        == col_data["id"]
    )
    return rx.el.div(
        rx.el.h6(
            col_data["name"],
            class_name="text-md font-semibold mb-2 text-gray-800",
        ),
        rx.cond(
            is_editing_this_formula,
            rx.el.div(
                rx.el.label(
                    "Formula Description:",
                    class_name="text-xs font-medium text-gray-600 block mb-1",
                ),
                rx.el.textarea(
                    default_value=FilePrepState.editing_formula_description_input,
                    on_change=FilePrepState.set_editing_formula_description_input,
                    class_name="w-full p-2 border border-blue-400 rounded mb-2 text-sm min-h-[60px] focus:ring-1 focus:ring-blue-500",
                    placeholder="Human-readable description of the formula",
                ),
                rx.el.label(
                    "Excel-Style Formula:",
                    class_name="text-xs font-medium text-gray-600 block mb-1",
                ),
                rx.el.textarea(
                    default_value=FilePrepState.editing_formula_excel_style_input,
                    on_change=FilePrepState.set_editing_formula_excel_style_input,
                    class_name="w-full p-2 border border-blue-400 rounded mb-2 text-sm min-h-[60px] font-mono focus:ring-1 focus:ring-blue-500",
                    placeholder='e.g., =IF(A1>B1, "Yes", "No")',
                ),
                rx.el.div(
                    _icon_button(
                        "check",
                        FilePrepState.save_formula_edits,
                        "Save Formula",
                        extra_class_name="text-green-600 hover:text-green-700",
                    ),
                    _icon_button(
                        "x",
                        FilePrepState.cancel_formula_edits,
                        "Cancel Edit",
                        extra_class_name="text-red-600 hover:text-red-700",
                    ),
                    class_name="flex space-x-2 mt-1",
                ),
                class_name="mb-2",
            ),
            rx.el.div(
                rx.el.p(
                    rx.el.strong("Description: "),
                    rx.cond(
                        col_data.get(
                            "formula_description", ""
                        ).length()
                        > 0,
                        cast(
                            rx.Var[str],
                            col_data.get(
                                "formula_description", ""
                            ),
                        ),
                        rx.el.em(
                            "Not set",
                            class_name="text-gray-400",
                        ),
                    ),
                    class_name="text-sm text-gray-700 mb-1",
                ),
                rx.el.p(
                    rx.el.strong("Excel Formula: "),
                    rx.cond(
                        col_data.get(
                            "formula_excel_style", ""
                        ).length()
                        > 0,
                        rx.el.code(
                            cast(
                                rx.Var[str],
                                col_data.get(
                                    "formula_excel_style",
                                    "",
                                ),
                            )
                        ),
                        rx.el.em(
                            "Not set",
                            class_name="text-gray-400",
                        ),
                    ),
                    class_name="text-sm text-gray-700 font-mono",
                ),
                _icon_button(
                    "pencil",
                    lambda: FilePrepState.start_editing_formula(
                        cast(str, col_data["id"])
                    ),
                    "Edit Formula",
                    extra_class_name="mt-1",
                ),
                class_name="mb-2",
            ),
        ),
        class_name="p-3 border border-gray-200 rounded bg-white shadow-sm mb-3",
    )


def _formula_review_view() -> rx.Component:
    """View for reviewing and editing column formulas."""
    return rx.el.div(
        rx.el.p(
            "Review and optionally edit the formulas for calculated columns. These will be embedded in the generated Excel template.",
            class_name="text-sm text-gray-600 mb-4",
        ),
        rx.el.button(
            "Formula Building Wizard (Coming Soon)",
            on_click=FilePrepState.open_formula_wizard,
            class_name="mb-4 px-3 py-1.5 bg-purple-500 text-white text-xs rounded hover:bg-purple-600",
        ),
        rx.foreach(
            FilePrepState.columns_with_formulas,
            _formula_review_item_component,
        ),
        rx.el.div(
            rx.el.button(
                "⬅ Back to Edit Columns",
                on_click=FilePrepState.back_to_edit_columns_from_review,
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
            ),
            rx.el.button(
                "Pre-load Template ➡",
                on_click=FilePrepState.confirm_formulas_and_proceed_to_uploads,
                disabled=FilePrepState.is_confirm_formulas_and_proceed_disabled,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150",
            ),
            class_name="flex justify-between items-center mt-6 border-t border-gray-200 pt-4",
        ),
    )


def _formula_modal_component() -> rx.Component:
    """Modal to display formula information."""
    return rx.dialog.root(
        rx.dialog.trigger(rx.fragment()),
        rx.dialog.content(
            rx.dialog.title(
                "Formula Information for: ",
                rx.el.strong(
                    FilePrepState.selected_column_for_formula.get(
                        "name", "Column"
                    )
                ),
                class_name="text-lg font-semibold text-gray-800",
            ),
            rx.dialog.description(
                rx.el.div(
                    rx.el.p(
                        rx.el.strong("Description:"),
                        class_name="mt-2 mb-1 text-sm font-medium text-gray-600",
                    ),
                    rx.el.p(
                        FilePrepState.selected_column_for_formula.get(
                            "formula_description", "N/A"
                        ),
                        class_name="text-sm text-gray-700 bg-gray-100 p-2 rounded",
                    ),
                    rx.el.p(
                        rx.el.strong(
                            "Excel-Style Formula:"
                        ),
                        class_name="mt-3 mb-1 text-sm font-medium text-gray-600",
                    ),
                    rx.el.pre(
                        rx.el.code(
                            FilePrepState.selected_column_for_formula.get(
                                "formula_excel_style", "N/A"
                            ),
                            class_name="text-sm text-gray-700",
                        ),
                        class_name="bg-gray-100 p-2 rounded font-mono text-xs overflow-x-auto",
                    ),
                    class_name="mt-2 mb-4 max-h-80 overflow-y-auto",
                )
            ),
            rx.el.div(
                rx.dialog.close(
                    rx.el.button(
                        "Close",
                        class_name="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300",
                    )
                ),
                class_name="flex justify-end mt-4",
            ),
            style={"maxWidth": "500px"},
            class_name="bg-white p-6 rounded-lg shadow-xl border border-gray-200",
        ),
        open=FilePrepState.show_formula_modal,
        on_open_change=lambda open_state: rx.cond(
            ~open_state,
            FilePrepState.hide_formula_info,
            rx.console_log(""),
        ),
    )


def _formula_wizard_modal_component() -> rx.Component:
    """Placeholder modal for the formula wizard."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Formula Building Wizard",
                class_name="text-lg font-semibold text-gray-800",
            ),
            rx.dialog.description(
                rx.el.p(
                    "This feature is coming soon!",
                    class_name="text-gray-600 my-4",
                ),
                rx.el.p(
                    "It will help you build complex Excel formulas by selecting columns and operations.",
                    class_name="text-sm text-gray-500",
                ),
            ),
            rx.el.div(
                rx.dialog.close(
                    rx.el.button(
                        "Close",
                        class_name="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300",
                    )
                ),
                class_name="flex justify-end mt-4",
            ),
            style={"maxWidth": "450px"},
            class_name="bg-white p-6 rounded-lg shadow-xl border border-gray-200",
        ),
        open=FilePrepState.show_formula_wizard_modal,
        on_open_change=lambda open_state: rx.cond(
            ~open_state,
            FilePrepState.close_formula_wizard,
            rx.console_log(""),
        ),
    )


def column_definition_component() -> rx.Component:
    """Main component for defining Excel output columns and their formulas."""
    return rx.el.div(
        rx.el.h4(
            "Step 6: Define Excel Output Columns & Formulas",
            class_name="text-xl font-medium mb-6 text-gray-700",
        ),
        rx.cond(
            FilePrepState.formula_review_active,
            _formula_review_view(),
            _column_editor_view(),
        ),
        _formula_modal_component(),
        _formula_wizard_modal_component(),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50 shadow",
    )