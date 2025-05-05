import reflex as rx
from app.states.file_prep_state import (
    FilePrepState,
    CustomMetric,
)


def evergreen_metric_checkbox(
    metric_name: str,
) -> rx.Component:
    """Creates a checkbox for an evergreen metric with its definition."""
    is_included = (
        FilePrepState.included_evergreen_metrics.contains(
            metric_name
        )
    )
    definition = (
        FilePrepState.evergreen_metrics_definitions[
            metric_name
        ]
    )
    return rx.el.div(
        rx.el.label(
            rx.el.input(
                type="checkbox",
                checked=is_included,
                on_change=lambda: FilePrepState.toggle_evergreen_metric(
                    metric_name
                ),
                class_name="mr-2 accent-blue-600",
            ),
            rx.el.span(
                metric_name,
                class_name="font-medium text-gray-800",
            ),
            class_name="flex items-center cursor-pointer",
        ),
        rx.el.details(
            rx.el.summary(
                "Definition",
                class_name="text-xs text-blue-600 hover:text-blue-800 cursor-pointer list-none outline-none focus:ring-1 focus:ring-blue-300 rounded px-1 ml-6",
            ),
            rx.el.p(
                definition,
                class_name="text-sm text-gray-600 mt-1 ml-6 pl-2 border-l border-gray-200",
            ),
            class_name="mt-1",
        ),
        class_name="mb-4 p-3 border border-gray-200 rounded bg-white shadow-sm",
    )


def custom_metric_item(
    metric: CustomMetric,
) -> rx.Component:
    """Displays an added custom metric with a remove button."""
    return rx.el.li(
        rx.el.div(
            rx.el.strong(
                metric.name, class_name="text-gray-800"
            ),
            rx.el.p(
                metric.definition,
                class_name="text-sm text-gray-600 mt-1",
            ),
            class_name="flex-grow pr-4",
        ),
        rx.el.button(
            "Remove",
            on_click=lambda: FilePrepState.remove_custom_metric(
                metric.name
            ),
            class_name="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600",
        ),
        class_name="flex justify-between items-start p-3 border-b border-gray-200 last:border-b-0",
    )


def metric_weight_input(metric_info: dict) -> rx.Component:
    """Creates an input field for setting the weight of an included metric."""
    metric_name = metric_info["name"]
    current_weight = FilePrepState.metric_weights.get(
        metric_name, 5
    ).to_string()
    return rx.el.div(
        rx.el.label(
            metric_name,
            html_for=f"weight-{metric_name}",
            class_name="block text-sm font-medium text-gray-700 mb-1",
        ),
        rx.el.input(
            id=f"weight-{metric_name}",
            type="number",
            min=1,
            max=10,
            step=1,
            default_value=current_weight,
            on_change=lambda val: FilePrepState.set_metric_weight(
                metric_name, val
            ),
            class_name="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
        ),
        rx.el.details(
            rx.el.summary(
                "Definition",
                class_name="text-xs text-blue-600 hover:text-blue-800 cursor-pointer list-none outline-none focus:ring-1 focus:ring-blue-300 rounded px-1 mt-1",
            ),
            rx.el.p(
                metric_info["definition"],
                class_name="text-sm text-gray-600 mt-1",
            ),
            class_name="mt-1",
        ),
        class_name="mb-4 p-3 border border-gray-200 rounded bg-white shadow-sm",
    )


def metric_definition_component() -> rx.Component:
    """Component for defining and weighting evaluation metrics."""
    return rx.el.div(
        rx.el.h4(
            "Define Evaluation Metrics & Weights",
            class_name="text-xl font-medium mb-6 text-gray-700",
        ),
        rx.el.div(
            rx.el.h5(
                "Evergreen Metrics",
                class_name="text-lg font-medium mb-3 text-gray-600",
            ),
            rx.el.p(
                "Select the standard metrics to include in the evaluation.",
                class_name="text-sm text-gray-500 mb-4",
            ),
            rx.foreach(
                FilePrepState.evergreen_metrics_definitions.keys(),
                evergreen_metric_checkbox,
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            rx.el.h5(
                "Custom Metrics",
                class_name="text-lg font-medium mb-3 text-gray-600",
            ),
            rx.el.p(
                "Add project-specific metrics if needed.",
                class_name="text-sm text-gray-500 mb-4",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Custom Metric Name",
                    default_value=FilePrepState.new_custom_metric_name,
                    on_change=FilePrepState.set_new_custom_metric_name,
                    class_name="flex-grow p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 mr-2",
                ),
                rx.el.input(
                    placeholder="Custom Metric Definition",
                    default_value=FilePrepState.new_custom_metric_definition,
                    on_change=FilePrepState.set_new_custom_metric_definition,
                    class_name="flex-grow p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 mr-2",
                ),
                rx.el.button(
                    "Add Custom",
                    on_click=FilePrepState.add_custom_metric,
                    disabled=FilePrepState.is_add_custom_metric_disabled,
                    class_name="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed",
                ),
                class_name="flex items-center mb-4 p-3 border border-gray-200 rounded bg-white",
            ),
            rx.el.ul(
                rx.foreach(
                    FilePrepState.custom_metrics,
                    custom_metric_item,
                ),
                rx.cond(
                    FilePrepState.custom_metrics.length()
                    == 0,
                    rx.el.li(
                        "No custom metrics added yet.",
                        class_name="text-gray-500 italic p-3",
                    ),
                    rx.fragment(),
                ),
                class_name="list-none p-0 mb-6 border border-gray-200 rounded bg-white max-h-60 overflow-y-auto",
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            rx.el.h5(
                "Metric Weights (1-10)",
                class_name="text-lg font-medium mb-3 text-gray-600",
            ),
            rx.el.p(
                "Assign a weight to each included metric (1 = least important, 10 = most important).",
                class_name="text-sm text-gray-500 mb-4",
            ),
            rx.cond(
                FilePrepState.all_included_metrics.length()
                > 0,
                rx.el.div(
                    rx.foreach(
                        FilePrepState.all_included_metrics,
                        metric_weight_input,
                    )
                ),
                rx.el.p(
                    "No metrics selected to assign weights.",
                    class_name="text-gray-500 italic",
                ),
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            rx.el.button(
                "⬅ Edit Stakeholder Perspective",
                on_click=lambda: FilePrepState.set_stakeholder_confirmed(
                    False
                ),
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
            ),
            rx.el.button(
                "Confirm Metrics & Weights ➡",
                on_click=FilePrepState.confirm_metrics,
                disabled=FilePrepState.is_confirm_metrics_disabled,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150",
            ),
            class_name="flex justify-between items-center mt-6 border-t border-gray-200 pt-4",
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50 shadow",
    )