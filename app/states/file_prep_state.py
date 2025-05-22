import reflex as rx
from typing import (
    Literal,
    TypedDict,
    TYPE_CHECKING,
    Optional,
    Union,
    List,
    Dict,
    cast,
    Any,
)
import uuid
import re
import io
import csv
import logging
import html

if TYPE_CHECKING:
    from app.states.project_state import ProjectState
logger = logging.getLogger(__name__)
MAX_PREVIEW_ROWS = 10
Language = Literal[
    "Arabic",
    "English",
    "Spanish",
    "French",
    "German",
    "Korean",
    "Japanese",
    "Chinese",
]
AVAILABLE_LANGUAGES: List[Language] = [
    "English",
    "Spanish",
    "French",
    "German",
    "Korean",
    "Japanese",
    "Chinese",
    "Arabic",
]
DEFAULT_MT_ENGINES: List[str] = [
    "Google Translate",
    "DeepL",
    "Microsoft Translator",
    "Amazon Translate",
]
EVERGREEN_METRICS: Dict[str, str] = {
    "Fluency": "How natural and easy to read the translation is.",
    "Accuracy": "How well the translation conveys the meaning of the source text.",
    "Style": "Appropriateness of the translation's tone and register for the intended audience and purpose.",
    "Terminology": "Correct and consistent use of domain-specific terms.",
    "Locale Conventions": "Correct use of formatting for dates, numbers, currency, etc., appropriate for the target locale.",
}
ReadmeChoice = Literal["default", "customize", "new"]
ColumnGroup = Literal[
    "Input",
    "Pre-Evaluation",
    "Scoring",
    "Calculated Score",
    "Freeform",
]
COLUMN_GROUPS_ORDER: List[ColumnGroup] = [
    "Input",
    "Pre-Evaluation",
    "Scoring",
    "Calculated Score",
    "Freeform",
]


class CustomMetric(TypedDict):
    name: str
    definition: str


class ExcelColumn(TypedDict, total=False):
    id: str
    name: str
    group: ColumnGroup
    editable_name: bool
    removable: bool
    movable_within_group: bool
    is_default: bool
    formula_description: Optional[str]
    formula_excel_style: Optional[str]
    metric_type: Optional[
        Literal["evergreen", "custom", "overall"]
    ]
    requires_upload: Optional[bool]
    is_word_count_column: Optional[bool]
    is_first_movable_in_group: Optional[bool]
    is_last_movable_in_group: Optional[bool]


DEFAULT_README_HTML = ""
DEFAULT_EXCEL_COLUMNS_DATA: List[ExcelColumn] = [
    {
        "id": str(uuid.uuid4()),
        "name": "File Name",
        "group": "Input",
        "editable_name": False,
        "removable": False,
        "movable_within_group": False,
        "is_default": True,
        "requires_upload": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Source",
        "group": "Input",
        "editable_name": False,
        "removable": False,
        "movable_within_group": False,
        "is_default": True,
        "requires_upload": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Target",
        "group": "Input",
        "editable_name": False,
        "removable": False,
        "movable_within_group": False,
        "is_default": True,
        "requires_upload": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Word Count (Source)",
        "group": "Pre-Evaluation",
        "editable_name": False,
        "removable": False,
        "movable_within_group": True,
        "is_default": True,
        "formula_description": "Calculates the word count of the 'Source' column.",
        "formula_excel_style": '=IF(ISBLANK(INDIRECT(ADDRESS(ROW(),COLUMN()-2))),"",LEN(TRIM(INDIRECT(ADDRESS(ROW(),COLUMN()-2))))-LEN(SUBSTITUTE(TRIM(INDIRECT(ADDRESS(ROW(),COLUMN()-2)))," ",""))+1)',
        "is_word_count_column": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Word Count (Target)",
        "group": "Pre-Evaluation",
        "editable_name": False,
        "removable": False,
        "movable_within_group": True,
        "is_default": True,
        "formula_description": "Calculates the word count of the 'Target' column.",
        "formula_excel_style": '=IF(ISBLANK(INDIRECT(ADDRESS(ROW(),COLUMN()-1))),"",LEN(TRIM(INDIRECT(ADDRESS(ROW(),COLUMN()-1))))-LEN(SUBSTITUTE(TRIM(INDIRECT(ADDRESS(ROW(),COLUMN()-1)))," ",""))+1)',
        "is_word_count_column": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Overall Score",
        "group": "Calculated Score",
        "editable_name": False,
        "removable": False,
        "movable_within_group": False,
        "is_default": True,
        "formula_description": "Calculates the weighted average of all scoring columns.",
        "formula_excel_style": "",
        "metric_type": "overall",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Pass/Fail",
        "group": "Calculated Score",
        "editable_name": False,
        "removable": False,
        "movable_within_group": False,
        "is_default": True,
        "formula_description": "Determines Pass/Fail based on the Overall Score and the defined threshold.",
        "formula_excel_style": "",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Comments",
        "group": "Freeform",
        "editable_name": False,
        "removable": False,
        "movable_within_group": True,
        "is_default": True,
    },
]


class FilePrepState(rx.State):
    """Manages the state for the file preparation workflow."""

    current_source_language: Language | None = None
    current_target_language: Language | None = None
    selected_pairs_for_session: list[
        tuple[Language, Language]
    ] = []
    pairs_confirmed: bool = False

    @rx.var
    def available_languages(self) -> list[Language]:
        return AVAILABLE_LANGUAGES

    @rx.event
    def set_current_source_language(self, lang: Language):
        self.current_source_language = lang

    @rx.event
    def set_current_target_language(self, lang: Language):
        self.current_target_language = lang

    @rx.event
    def add_language_pair(self):
        if (
            self.current_source_language
            and self.current_target_language
        ):
            if (
                self.current_source_language
                == self.current_target_language
            ):
                yield rx.toast(
                    "Source and Target languages cannot be the same.",
                    duration=3000,
                )
                return
            pair = (
                self.current_source_language,
                self.current_target_language,
            )
            if pair not in self.selected_pairs_for_session:
                self.selected_pairs_for_session.append(pair)
                self.current_source_language = None
                self.current_target_language = None
            else:
                yield rx.toast(
                    "This language pair already exists.",
                    duration=3000,
                )

    @rx.event
    def remove_language_pair(
        self, pair: tuple[Language, Language]
    ):
        if pair in self.selected_pairs_for_session:
            self.selected_pairs_for_session.remove(pair)

    @rx.event
    async def confirm_language_pairs(self):
        from app.states.project_state import ProjectState

        project_s = await self.get_state(ProjectState)
        if project_s.selected_project:
            project_s.project_language_pairs[
                project_s.selected_project
            ] = [
                (p[0], p[1])
                for p in self.selected_pairs_for_session
            ]
            self.pairs_confirmed = True
            yield rx.toast(
                "Language pairs confirmed.", duration=2000
            )

    @rx.var
    def is_add_pair_disabled(self) -> bool:
        return not (
            self.current_source_language
            and self.current_target_language
        )

    @rx.var
    def is_confirm_pairs_disabled(self) -> bool:
        return len(self.selected_pairs_for_session) == 0

    @rx.event
    def set_pairs_confirmed(self, status: bool):
        self.pairs_confirmed = status
        if not status:
            self.engines_confirmed = False
            self.readme_confirmed = False
            self.stakeholder_confirmed = False
            self.metrics_confirmed = False
            self.column_structure_finalized = False
            self.template_preview_ready = False

    new_engine_name: str = ""
    selected_engines: list[str] = []
    engines_confirmed: bool = False

    @rx.var
    def available_engines(self) -> list[str]:
        return DEFAULT_MT_ENGINES

    @rx.event
    def set_new_engine_name(self, name: str):
        self.new_engine_name = name

    @rx.event
    def add_custom_engine(self):
        name = self.new_engine_name.strip()
        if (
            name
            and name not in self.selected_engines
            and (name not in self.available_engines)
        ):
            self.selected_engines.append(name)
            self.new_engine_name = ""
        elif not name:
            yield rx.toast(
                "Engine name cannot be empty.",
                duration=3000,
            )
        else:
            yield rx.toast(
                "This engine name already exists or is a default engine.",
                duration=3000,
            )

    @rx.event
    def toggle_engine(self, engine_name: str):
        if engine_name in self.selected_engines:
            self.selected_engines.remove(engine_name)
        else:
            self.selected_engines.append(engine_name)

    @rx.event
    def remove_engine(self, engine_name: str):
        if engine_name in self.selected_engines:
            self.selected_engines.remove(engine_name)

    @rx.event
    async def confirm_engines(self):
        from app.states.project_state import ProjectState

        project_s = await self.get_state(ProjectState)
        if project_s.selected_project:
            project_s.project_mt_engines[
                project_s.selected_project
            ] = self.selected_engines.copy()
            self.engines_confirmed = True
            yield rx.toast(
                "MT engines confirmed.", duration=2000
            )
            self._update_scoring_columns_from_engines()

    @rx.var
    def is_add_engine_disabled(self) -> bool:
        return not self.new_engine_name.strip()

    @rx.var
    def is_confirm_engines_disabled(self) -> bool:
        return len(self.selected_engines) == 0

    @rx.event
    def set_engines_confirmed(self, status: bool):
        self.engines_confirmed = status
        if not status:
            self.readme_confirmed = False
            self.stakeholder_confirmed = False
            self.metrics_confirmed = False
            self.column_structure_finalized = False
            self.template_preview_ready = False

    default_readme: str = DEFAULT_README_HTML
    readme_choice: ReadmeChoice | None = "default"
    custom_readme_content: str = ""
    readme_confirmed: bool = False

    @rx.event
    def set_readme_choice(self, choice: ReadmeChoice):
        self.readme_choice = choice
        if choice == "default":
            self.custom_readme_content = ""
        elif choice == "customize":
            self.custom_readme_content = self.default_readme
        elif choice == "new":
            self.custom_readme_content = "<p><br></p>"

    @rx.var
    def final_readme_content(self) -> str:
        if self.readme_choice == "default":
            return self.default_readme
        return self.custom_readme_content

    @rx.event
    def set_custom_readme_content(self, content: str):
        self.custom_readme_content = content

    @rx.event
    async def confirm_readme(self):
        from app.states.project_state import ProjectState

        project_s = await self.get_state(ProjectState)
        if project_s.selected_project:
            project_s.project_readme_content[
                project_s.selected_project
            ] = self.final_readme_content
            self.readme_confirmed = True
            yield rx.toast(
                "Read Me instructions confirmed.",
                duration=2000,
            )

    @rx.var
    def is_confirm_readme_disabled(self) -> bool:
        return self.readme_choice is None or (
            self.readme_choice != "default"
            and (not self.custom_readme_content.strip())
        )

    @rx.event
    def set_readme_confirmed(self, status: bool):
        self.readme_confirmed = status
        if not status:
            self.stakeholder_confirmed = False
            self.metrics_confirmed = False
            self.column_structure_finalized = False
            self.template_preview_ready = False

    stakeholder_comments: str = ""
    stakeholder_confirmed: bool = False

    @rx.event
    def set_stakeholder_comments(self, comments: str):
        self.stakeholder_comments = comments

    @rx.event
    async def confirm_stakeholder_perspective(self):
        from app.states.project_state import ProjectState

        project_s = await self.get_state(ProjectState)
        if project_s.selected_project:
            project_s.project_stakeholder_comments[
                project_s.selected_project
            ] = self.stakeholder_comments
            self.stakeholder_confirmed = True
            yield rx.toast(
                "Stakeholder perspective confirmed.",
                duration=2000,
            )

    @rx.var
    def is_confirm_stakeholder_disabled(self) -> bool:
        return False

    @rx.event
    def set_stakeholder_confirmed(self, status: bool):
        self.stakeholder_confirmed = status
        if not status:
            self.metrics_confirmed = False
            self.column_structure_finalized = False
            self.template_preview_ready = False

    included_evergreen_metrics: list[str] = list(
        EVERGREEN_METRICS.keys()
    )
    custom_metrics: list[CustomMetric] = []
    new_custom_metric_name: str = ""
    new_custom_metric_definition: str = ""
    metric_weights: dict[str, int] = {
        metric: 5 for metric in EVERGREEN_METRICS
    }
    pass_threshold: float | None = None
    pass_definition: str = ""
    metrics_confirmed: bool = False

    @rx.var
    def evergreen_metrics_definitions(
        self,
    ) -> dict[str, str]:
        return EVERGREEN_METRICS

    @rx.event
    def toggle_evergreen_metric(self, metric_name: str):
        if metric_name in self.included_evergreen_metrics:
            self.included_evergreen_metrics.remove(
                metric_name
            )
            if metric_name in self.metric_weights:
                del self.metric_weights[metric_name]
        else:
            self.included_evergreen_metrics.append(
                metric_name
            )
            self.metric_weights[metric_name] = 5
        self._update_scoring_columns_from_metrics()

    @rx.event
    def set_new_custom_metric_name(self, name: str):
        self.new_custom_metric_name = name

    @rx.event
    def set_new_custom_metric_definition(
        self, definition: str
    ):
        self.new_custom_metric_definition = definition

    @rx.event
    def add_custom_metric(self):
        name = self.new_custom_metric_name.strip()
        definition = (
            self.new_custom_metric_definition.strip()
        )
        if name and definition:
            if (
                not any(
                    (
                        m.name == name
                        for m in self.custom_metrics
                    )
                )
                and name
                not in self.included_evergreen_metrics
            ):
                self.custom_metrics.append(
                    CustomMetric(
                        name=name, definition=definition
                    )
                )
                self.metric_weights[name] = 5
                self.new_custom_metric_name = ""
                self.new_custom_metric_definition = ""
                self._update_scoring_columns_from_metrics()
            else:
                yield rx.toast(
                    "Custom metric name already exists.",
                    duration=3000,
                )
        else:
            yield rx.toast(
                "Both name and definition are required for custom metrics.",
                duration=3000,
            )

    @rx.event
    def remove_custom_metric(self, metric_name: str):
        self.custom_metrics = [
            m
            for m in self.custom_metrics
            if m.name != metric_name
        ]
        if metric_name in self.metric_weights:
            del self.metric_weights[metric_name]
        self._update_scoring_columns_from_metrics()

    @rx.event
    def set_metric_weight(
        self, metric_name: str, weight_str: str
    ):
        try:
            weight = int(weight_str)
            if 1 <= weight <= 10:
                self.metric_weights[metric_name] = weight
            else:
                self.metric_weights[metric_name] = max(
                    1, min(10, weight)
                )
                yield rx.toast(
                    "Weight must be between 1 and 10.",
                    duration=3000,
                )
        except ValueError:
            if metric_name in self.metric_weights:
                del self.metric_weights[metric_name]
            yield rx.toast(
                "Invalid weight. Please enter a number.",
                duration=3000,
            )

    @rx.var
    def all_included_metrics(self) -> list[dict[str, str]]:
        metrics = []
        for name in self.included_evergreen_metrics:
            metrics.append(
                {
                    "name": name,
                    "definition": self.evergreen_metrics_definitions[
                        name
                    ],
                }
            )
        for cm in self.custom_metrics:
            metrics.append(
                {
                    "name": cm.name,
                    "definition": cm.definition,
                }
            )
        return metrics

    @rx.var
    def total_metric_weight(self) -> int:
        return sum(
            (
                self.metric_weights.get(m["name"], 0)
                for m in self.all_included_metrics
            )
        )

    @rx.event
    def set_pass_threshold(self, threshold_str: str):
        try:
            if threshold_str:
                self.pass_threshold = float(threshold_str)
            else:
                self.pass_threshold = None
        except ValueError:
            self.pass_threshold = None
            yield rx.toast(
                "Invalid threshold. Please enter a number or leave blank.",
                duration=3000,
            )

    @rx.event
    def set_pass_definition(self, definition: str):
        self.pass_definition = definition

    @rx.event
    async def confirm_metrics(self):
        if not self.all_included_metrics:
            yield rx.toast(
                "Please select or add at least one metric.",
                duration=3000,
            )
            return
        if any(
            (
                m["name"] not in self.metric_weights
                for m in self.all_included_metrics
            )
        ):
            yield rx.toast(
                "Please assign weights to all selected metrics.",
                duration=3000,
            )
            return
        from app.states.project_state import ProjectState

        project_s = await self.get_state(ProjectState)
        if project_s.selected_project:
            project_s.project_included_metrics[
                project_s.selected_project
            ] = {
                "evergreen": self.included_evergreen_metrics.copy(),
                "custom": self.custom_metrics.copy(),
            }
            project_s.project_metric_weights[
                project_s.selected_project
            ] = self.metric_weights.copy()
            project_s.project_pass_threshold[
                project_s.selected_project
            ] = self.pass_threshold
            project_s.project_pass_definition[
                project_s.selected_project
            ] = self.pass_definition
            self.metrics_confirmed = True
            self._update_excel_formulas()
            yield rx.toast(
                "Metrics, weights, and pass criteria confirmed.",
                duration=2000,
            )

    @rx.var
    def is_add_custom_metric_disabled(self) -> bool:
        return not (
            self.new_custom_metric_name.strip()
            and self.new_custom_metric_definition.strip()
        )

    @rx.var
    def is_confirm_metrics_disabled(self) -> bool:
        return not self.all_included_metrics or any(
            (
                m["name"] not in self.metric_weights
                for m in self.all_included_metrics
            )
        )

    @rx.event
    def set_metrics_confirmed(self, status: bool):
        self.metrics_confirmed = status
        if not status:
            self.column_structure_finalized = False
            self.template_preview_ready = False
        else:
            self._update_scoring_columns_from_metrics()
            self._update_excel_formulas()

    excel_columns_for_session: list[ExcelColumn] = (
        DEFAULT_EXCEL_COLUMNS_DATA.copy()
    )
    column_structure_finalized: bool = False
    editing_column_id: str | None = None
    editing_column_name: str = ""
    new_column_inputs: dict[ColumnGroup, str] = {
        group: ""
        for group in COLUMN_GROUPS_ORDER
        if group != "Scoring"
    }
    selected_column_for_formula: ExcelColumn = {}
    show_formula_modal: bool = False
    formula_review_active: bool = False
    editing_formula_column_id: str | None = None
    editing_formula_description_input: str = ""
    editing_formula_excel_style_input: str = ""
    show_formula_wizard_modal: bool = False

    def _get_default_excel_columns_copy(
        self,
    ) -> list[ExcelColumn]:
        return [
            col.copy() for col in DEFAULT_EXCEL_COLUMNS_DATA
        ]

    def _update_scoring_columns_from_metrics(self):
        """Dynamically adds/removes scoring columns based on selected metrics."""
        current_columns = [
            col
            for col in self.excel_columns_for_session
            if not (
                col.get("group") == "Scoring"
                and (not col.get("is_default"))
            )
        ]
        for metric_info in self.all_included_metrics:
            metric_name = metric_info["name"]
            metric_type: Literal["evergreen", "custom"] = (
                "evergreen"
                if metric_name
                in self.evergreen_metrics_definitions
                else "custom"
            )
            if not any(
                (
                    col.get("name") == metric_name
                    and col.get("group") == "Scoring"
                    for col in current_columns
                )
            ):
                new_col_id = str(uuid.uuid4())
                current_columns.append(
                    {
                        "id": new_col_id,
                        "name": metric_name,
                        "group": "Scoring",
                        "editable_name": False,
                        "removable": False,
                        "movable_within_group": True,
                        "is_default": False,
                        "metric_type": metric_type,
                    }
                )
        self.excel_columns_for_session = current_columns

    def _update_scoring_columns_from_engines(self):
        """Dynamically adds scoring columns for each selected engine."""
        current_columns = [
            col
            for col in self.excel_columns_for_session
            if not (
                col.get("group") == "Scoring"
                and col.get("name")
                in DEFAULT_MT_ENGINES
                + [
                    eng
                    for eng in self.selected_engines
                    if eng not in DEFAULT_MT_ENGINES
                ]
                and (not col.get("is_default"))
            )
        ]
        for engine_name in self.selected_engines:
            if not any(
                (
                    col.get("name") == engine_name
                    and col.get("group") == "Scoring"
                    for col in current_columns
                )
            ):
                new_col_id = str(uuid.uuid4())
                current_columns.append(
                    {
                        "id": new_col_id,
                        "name": engine_name,
                        "group": "Scoring",
                        "editable_name": False,
                        "removable": False,
                        "movable_within_group": True,
                        "is_default": False,
                        "metric_type": "custom",
                    }
                )
        self.excel_columns_for_session = current_columns

    def _update_excel_formulas(self):
        """Updates formulas for 'Overall Score' and 'Pass/Fail' based on current metrics and weights."""
        overall_score_col_index = -1
        pass_fail_col_index = -1
        scoring_column_indices: list[int] = []
        for i, col_data in enumerate(
            self.excel_columns_for_session
        ):
            if (
                col_data.get("name") == "Overall Score"
                and col_data.get("group")
                == "Calculated Score"
            ):
                overall_score_col_index = i
            elif (
                col_data.get("name") == "Pass/Fail"
                and col_data.get("group")
                == "Calculated Score"
            ):
                pass_fail_col_index = i
            elif col_data.get("group") == "Scoring":
                scoring_column_indices.append(i)
        if (
            overall_score_col_index != -1
            and scoring_column_indices
        ):
            self.excel_columns_for_session[
                overall_score_col_index
            ][
                "formula_excel_style"
            ] = "Dynamic: Weighted average of Scoring columns"
        if (
            pass_fail_col_index != -1
            and overall_score_col_index != -1
            and (self.pass_threshold is not None)
        ):
            self.excel_columns_for_session[
                pass_fail_col_index
            ][
                "formula_excel_style"
            ] = f'Dynamic: IF(OverallScore >= {self.pass_threshold}, "Pass", "Fail")'
        elif pass_fail_col_index != -1:
            self.excel_columns_for_session[
                pass_fail_col_index
            ][
                "formula_excel_style"
            ] = "Dynamic: Pass/Fail (threshold not set)"

    @rx.var
    def final_excel_columns_for_display(
        self,
    ) -> list[tuple[ColumnGroup, list[ExcelColumn]]]:
        """Groups columns by their 'group' attribute for display, respecting COLUMN_GROUPS_ORDER."""
        grouped: dict[ColumnGroup, list[ExcelColumn]] = {
            group_name: []
            for group_name in COLUMN_GROUPS_ORDER
        }
        for col in self.excel_columns_for_session:
            group = col.get("group")
            if group and group in grouped:
                grouped[group].append(col.copy())
        ordered_grouped_list = []
        for group_name in COLUMN_GROUPS_ORDER:
            cols_in_group = grouped.get(group_name, [])
            if not cols_in_group:
                if (
                    group_name == "Scoring"
                    and (not self.all_included_metrics)
                    and (not self.selected_engines)
                ):
                    continue
                elif group_name != "Scoring":
                    continue
            movable_cols = [
                c
                for c in cols_in_group
                if c.get("movable_within_group")
            ]
            for i, col in enumerate(cols_in_group):
                if col.get("movable_within_group"):
                    col["is_first_movable_in_group"] = (
                        col == movable_cols[0]
                        if movable_cols
                        else False
                    )
                    col["is_last_movable_in_group"] = (
                        col == movable_cols[-1]
                        if movable_cols
                        else False
                    )
                else:
                    col["is_first_movable_in_group"] = False
                    col["is_last_movable_in_group"] = False
            ordered_grouped_list.append(
                (group_name, cols_in_group)
            )
        return ordered_grouped_list

    @rx.event
    def start_editing_column_name(self, col_id: str):
        for (
            group_data
        ) in self.final_excel_columns_for_display:
            for col in group_data[1]:
                if col["id"] == col_id and col.get(
                    "editable_name"
                ):
                    self.editing_column_id = col_id
                    self.editing_column_name = col["name"]
                    return
        yield rx.toast(
            "This column name cannot be edited.",
            duration=3000,
        )

    @rx.event
    def set_editing_column_name(self, name: str):
        self.editing_column_name = name

    @rx.event
    def save_column_name(self):
        if (
            self.editing_column_id
            and self.editing_column_name.strip()
        ):
            for i, col_data in enumerate(
                self.excel_columns_for_session
            ):
                if col_data["id"] == self.editing_column_id:
                    self.excel_columns_for_session[i][
                        "name"
                    ] = self.editing_column_name.strip()
                    self.cancel_editing_column_name()
                    return
        elif not self.editing_column_name.strip():
            yield rx.toast(
                "Column name cannot be empty.",
                duration=3000,
            )

    @rx.event
    def cancel_editing_column_name(self):
        self.editing_column_id = None
        self.editing_column_name = ""

    @rx.event
    def set_new_column_input_for_group(
        self, group: ColumnGroup, value: str
    ):
        if group in self.new_column_inputs:
            self.new_column_inputs[group] = value

    @rx.event
    def add_new_column_to_group(
        self, group_name: ColumnGroup
    ):
        col_name = self.new_column_inputs.get(
            group_name, ""
        ).strip()
        if not col_name:
            yield rx.toast(
                "Column name cannot be empty.",
                duration=3000,
            )
            return
        if any(
            (
                c["name"] == col_name
                for c in self.excel_columns_for_session
            )
        ):
            yield rx.toast(
                f"Column name '{col_name}' already exists.",
                duration=3000,
            )
            return
        if group_name != "Scoring":
            new_col_id = str(uuid.uuid4())
            new_column: ExcelColumn = {
                "id": new_col_id,
                "name": col_name,
                "group": group_name,
                "editable_name": True,
                "removable": True,
                "movable_within_group": True,
                "is_default": False,
            }
            self.excel_columns_for_session.append(
                new_column
            )
            self.new_column_inputs[group_name] = ""
        else:
            yield rx.toast(
                "Scoring columns are managed via the Metrics & Engines steps.",
                duration=4000,
            )

    @rx.event
    def remove_column_by_id(self, col_id: str):
        self.excel_columns_for_session = [
            col
            for col in self.excel_columns_for_session
            if not (
                col["id"] == col_id and col.get("removable")
            )
        ]

    @rx.event
    def move_column(
        self,
        col_id: str,
        direction: Literal["left", "right"],
    ):
        col_to_move_index = -1
        for i, col in enumerate(
            self.excel_columns_for_session
        ):
            if col["id"] == col_id and col.get(
                "movable_within_group"
            ):
                col_to_move_index = i
                break
        if col_to_move_index == -1:
            return
        col_data = self.excel_columns_for_session.pop(
            col_to_move_index
        )
        target_group = col_data["group"]
        current_group_indices = [
            i
            for i, c in enumerate(
                self.excel_columns_for_session
            )
            if c["group"] == target_group
            and c.get("movable_within_group")
        ]
        original_relative_idx = -1
        temp_group_cols = [
            c
            for c in DEFAULT_EXCEL_COLUMNS_DATA
            + self.excel_columns_for_session
            if c["group"] == target_group
            and c.get("movable_within_group")
        ]
        if direction == "left" and col_to_move_index > 0:
            prev_idx = col_to_move_index - 1
            group_cols = [
                c
                for c in self.excel_columns_for_session
                if c["group"] == target_group
                and c.get("movable_within_group")
            ]
            try:
                current_pos_in_group = group_cols.index(
                    next(
                        (
                            c
                            for c in group_cols
                            if c["id"] == col_id
                        )
                    )
                )
            except StopIteration:
                self.excel_columns_for_session.insert(
                    col_to_move_index, col_data
                )
                return
            if current_pos_in_group > 0:
                item_to_swap_with = group_cols[
                    current_pos_in_group - 1
                ]
                swap_with_global_idx = (
                    self.excel_columns_for_session.index(
                        item_to_swap_with
                    )
                )
                self.excel_columns_for_session.insert(
                    swap_with_global_idx, col_data
                )
            else:
                self.excel_columns_for_session.insert(
                    col_to_move_index, col_data
                )
        elif direction == "right":
            group_cols = [
                c
                for c in self.excel_columns_for_session
                if c["group"] == target_group
                and c.get("movable_within_group")
            ]
            try:
                current_pos_in_group = group_cols.index(
                    next(
                        (
                            c
                            for c in group_cols
                            if c["id"] == col_id
                        )
                    )
                )
            except StopIteration:
                self.excel_columns_for_session.insert(
                    col_to_move_index, col_data
                )
                return
            if current_pos_in_group < len(group_cols) - 1:
                item_to_swap_with = group_cols[
                    current_pos_in_group + 1
                ]
                swap_with_global_idx = (
                    self.excel_columns_for_session.index(
                        item_to_swap_with
                    )
                )
                self.excel_columns_for_session.insert(
                    swap_with_global_idx + 1, col_data
                )
            else:
                self.excel_columns_for_session.insert(
                    col_to_move_index, col_data
                )
        else:
            self.excel_columns_for_session.insert(
                col_to_move_index, col_data
            )

    @rx.event
    def show_formula_info(self, col_id: str):
        for (
            group_data
        ) in self.final_excel_columns_for_display:
            for col in group_data[1]:
                if col["id"] == col_id and (
                    col.get("formula_description")
                    or col.get("formula_excel_style")
                ):
                    self.selected_column_for_formula = (
                        col.copy()
                    )
                    self.show_formula_modal = True
                    return

    @rx.event
    def hide_formula_info(
        self, open_state: bool | None = None
    ):
        if open_state is False or open_state is None:
            self.show_formula_modal = False
            self.selected_column_for_formula = {}

    @rx.var
    def columns_with_formulas(self) -> list[ExcelColumn]:
        return [
            col.copy()
            for col in self.excel_columns_for_session
            if col.get("formula_description")
            or col.get("formula_excel_style")
        ]

    @rx.event
    def proceed_from_column_editor(self):
        if self.columns_with_formulas:
            self.formula_review_active = True
        else:
            self._finalize_column_structure_and_proceed()

    @rx.event
    def back_to_edit_columns_from_review(self):
        self.formula_review_active = False
        self.editing_formula_column_id = None
        self.editing_formula_description_input = ""
        self.editing_formula_excel_style_input = ""

    @rx.event
    def start_editing_formula(self, col_id: str):
        col_data = next(
            (
                c
                for c in self.excel_columns_for_session
                if c["id"] == col_id
            ),
            None,
        )
        if col_data:
            self.editing_formula_column_id = col_id
            self.editing_formula_description_input = (
                col_data.get("formula_description", "")
            )
            self.editing_formula_excel_style_input = (
                col_data.get("formula_excel_style", "")
            )

    @rx.event
    def set_editing_formula_description_input(
        self, value: str
    ):
        self.editing_formula_description_input = value

    @rx.event
    def set_editing_formula_excel_style_input(
        self, value: str
    ):
        self.editing_formula_excel_style_input = value

    @rx.event
    def save_formula_edits(self):
        if self.editing_formula_column_id:
            for i, col_data in enumerate(
                self.excel_columns_for_session
            ):
                if (
                    col_data["id"]
                    == self.editing_formula_column_id
                ):
                    self.excel_columns_for_session[i][
                        "formula_description"
                    ] = (
                        self.editing_formula_description_input.strip()
                    )
                    self.excel_columns_for_session[i][
                        "formula_excel_style"
                    ] = (
                        self.editing_formula_excel_style_input.strip()
                    )
                    self.cancel_formula_edits()
                    return

    @rx.event
    def cancel_formula_edits(self):
        self.editing_formula_column_id = None
        self.editing_formula_description_input = ""
        self.editing_formula_excel_style_input = ""

    @rx.event
    def open_formula_wizard(self):
        self.show_formula_wizard_modal = True

    @rx.event
    def close_formula_wizard(
        self, open_state: bool | None = None
    ):
        if open_state is False or open_state is None:
            self.show_formula_wizard_modal = False

    def _finalize_column_structure_and_proceed(self):
        """Common logic after column editing or formula review."""
        self.column_structure_finalized = True
        self.formula_review_active = False

    @rx.event
    async def confirm_formulas_and_proceed_to_uploads(self):
        from app.states.project_state import ProjectState

        project_s = await self.get_state(ProjectState)
        if project_s.selected_project:
            project_s.project_excel_columns[
                project_s.selected_project
            ] = self.excel_columns_for_session.copy()
        self._finalize_column_structure_and_proceed()
        yield rx.toast(
            "Column formulas confirmed.", duration=2000
        )

    @rx.var
    def is_proceed_from_column_editor_disabled(
        self,
    ) -> bool:
        has_input_group = any(
            (
                gd[0] == "Input" and gd[1]
                for gd in self.final_excel_columns_for_display
            )
        )
        return not has_input_group

    @rx.var
    def is_confirm_formulas_and_proceed_disabled(
        self,
    ) -> bool:
        return self.editing_formula_column_id is not None

    @rx.event
    def set_column_structure_finalized(self, status: bool):
        self.column_structure_finalized = status
        if not status:
            self.template_preview_ready = False
            self.formula_review_active = False
        else:
            self._update_excel_formulas()

    uploaded_files_data: dict[str, list[list[str]]] = {}
    uploaded_file_info: dict[str, str] = {}
    template_preview_ready: bool = False

    @rx.var
    def template_input_columns_for_upload(
        self,
    ) -> list[ExcelColumn]:
        """Returns columns from 'Input' group that require uploads."""
        return [
            col.copy()
            for col in self.excel_columns_for_session
            if col.get("group") == "Input"
            and col.get("requires_upload")
        ]

    @rx.event
    async def handle_file_upload(
        self, files: list[rx.UploadFile], column_id_str: str
    ):
        if not files:
            return
        upload_file = files[0]
        file_content_bytes = await upload_file.read()
        filename = upload_file.filename
        try:
            file_content_str = file_content_bytes.decode(
                "utf-8"
            )
        except UnicodeDecodeError:
            try:
                file_content_str = (
                    file_content_bytes.decode("latin-1")
                )
            except UnicodeDecodeError:
                yield rx.toast(
                    f"Error decoding file {filename}. Please ensure it's UTF-8 or Latin-1 encoded.",
                    duration=4000,
                )
                return
        data_rows: list[list[str]] = []
        if filename.lower().endswith(".txt"):
            lines = file_content_str.splitlines()
            data_rows = [
                [line.strip()]
                for line in lines
                if line.strip()
            ]
        elif filename.lower().endswith((".csv", ".tsv")):
            delimiter = (
                ","
                if filename.lower().endswith(".csv")
                else "\t"
            )
            file_like_object = io.StringIO(file_content_str)
            reader = csv.reader(
                file_like_object, delimiter=delimiter
            )
            try:
                for row in reader:
                    if row:
                        data_rows.append([row[0].strip()])
            except csv.Error as e:
                yield rx.toast(
                    f"Error parsing CSV/TSV {filename}: {e}",
                    duration=4000,
                )
                return
        if data_rows:
            self.uploaded_files_data[column_id_str] = (
                data_rows
            )
            self.uploaded_file_info[column_id_str] = (
                f"{filename} ({len(data_rows)} rows)"
            )
            yield rx.toast(
                f"Uploaded {filename} for column ID {column_id_str}.",
                duration=2000,
            )
        else:
            yield rx.toast(
                f"No data extracted from {filename}.",
                duration=3000,
            )
            if column_id_str in self.uploaded_files_data:
                del self.uploaded_files_data[column_id_str]
            if column_id_str in self.uploaded_file_info:
                del self.uploaded_file_info[column_id_str]

    @rx.event
    def clear_uploaded_file(self, column_id_str: str):
        if column_id_str in self.uploaded_files_data:
            del self.uploaded_files_data[column_id_str]
        if column_id_str in self.uploaded_file_info:
            del self.uploaded_file_info[column_id_str]

    @rx.event
    def proceed_to_generate_template_preview(self):
        required_input_cols = (
            self.template_input_columns_for_upload
        )
        if not required_input_cols:
            yield rx.toast(
                "Error: No input columns defined for upload.",
                duration=3000,
            )
            return
        missing_uploads = [
            col["name"]
            for col in required_input_cols
            if str(col["id"])
            not in self.uploaded_files_data
        ]
        if missing_uploads:
            yield rx.toast(
                f"Please upload files for: {', '.join(missing_uploads)}.",
                duration=4000,
            )
            return
        self.template_preview_ready = True
        yield rx.toast(
            "All required files uploaded. Preview generated.",
            duration=2000,
        )

    @rx.var
    def preview_table_headers(self) -> list[str]:
        return [
            col["name"]
            for col_group in self.final_excel_columns_for_display
            for col in col_group[1]
        ]

    @rx.var
    def preview_table_data(self) -> list[dict[str, str]]:
        if (
            not self.template_preview_ready
            or not self.uploaded_files_data
        ):
            return []
        num_rows = 0
        input_col_ids_with_data = [
            cid
            for cid in self.uploaded_files_data
            if any(
                (
                    str(col_meta["id"]) == cid
                    and col_meta["group"] == "Input"
                    for col_meta in self.template_input_columns_for_upload
                )
            )
        ]
        if input_col_ids_with_data:
            num_rows = min(
                (
                    len(self.uploaded_files_data[cid])
                    for cid in input_col_ids_with_data
                )
            )
        num_rows = min(num_rows, MAX_PREVIEW_ROWS)
        table_data: list[dict[str, str]] = []
        all_display_columns_flat = (
            self.display_excel_columns
        )
        for i in range(num_rows):
            row_dict: dict[str, str] = {}
            for col_meta in all_display_columns_flat:
                col_id_str = str(col_meta["id"])
                col_name = col_meta["name"]
                if (
                    col_meta.get("group") == "Input"
                    and col_id_str
                    in self.uploaded_files_data
                ):
                    if i < len(
                        self.uploaded_files_data[col_id_str]
                    ):
                        row_dict[col_name] = (
                            self.uploaded_files_data[
                                col_id_str
                            ][i][0]
                        )
                    else:
                        row_dict[col_name] = ""
                elif col_meta.get("formula_excel_style"):
                    row_dict[col_name] = "[Formula]"
                else:
                    row_dict[col_name] = ""
            table_data.append(row_dict)
        return table_data

    @rx.event
    def set_template_preview_ready(self, status: bool):
        self.template_preview_ready = status

    @rx.var
    def display_excel_columns(self) -> list[ExcelColumn]:
        """A flat list of all columns in their final display order."""
        flat_list = []
        for (
            _,
            cols_in_group,
        ) in self.final_excel_columns_for_display:
            flat_list.extend(cols_in_group)
        return flat_list

    @rx.event
    async def reset_state(self):
        """Resets the state to initial values, preparing for a new File Prep session."""
        logger.info("FilePrepState: Resetting state.")
        self.current_source_language = None
        self.current_target_language = None
        self.selected_pairs_for_session = []
        self.pairs_confirmed = False
        self.new_engine_name = ""
        self.selected_engines = []
        self.engines_confirmed = False
        self.readme_choice = "default"
        self.custom_readme_content = self.default_readme
        self.readme_confirmed = False
        self.stakeholder_comments = ""
        self.stakeholder_confirmed = False
        self.included_evergreen_metrics = list(
            EVERGREEN_METRICS.keys()
        )
        self.custom_metrics = []
        self.new_custom_metric_name = ""
        self.new_custom_metric_definition = ""
        self.metric_weights = {
            metric: 5 for metric in EVERGREEN_METRICS
        }
        self.pass_threshold = None
        self.pass_definition = ""
        self.metrics_confirmed = False
        self.excel_columns_for_session = (
            self._get_default_excel_columns_copy()
        )
        self.column_structure_finalized = False
        self.editing_column_id = None
        self.editing_column_name = ""
        self.new_column_inputs = {
            group: ""
            for group in COLUMN_GROUPS_ORDER
            if group != "Scoring"
        }
        self.selected_column_for_formula = {}
        self.show_formula_modal = False
        self.formula_review_active = False
        self.editing_formula_column_id = None
        self.editing_formula_description_input = ""
        self.editing_formula_excel_style_input = ""
        self.show_formula_wizard_modal = False
        self.uploaded_files_data = {}
        self.uploaded_file_info = {}
        self.template_preview_ready = False
        from app.states.project_state import ProjectState

        project_s = await self.get_state(ProjectState)
        if project_s.selected_project:
            logger.info(
                f"FilePrepState: Loading data for project '{project_s.selected_project}' after reset."
            )
            self.selected_pairs_for_session = [
                cast(Tuple[Language, Language], tuple(p))
                for p in project_s.current_project_pairs
            ]
            self.selected_engines = (
                project_s.current_project_engines.copy()
            )
            self.custom_readme_content = (
                project_s.current_project_readme
            )
            if (
                self.custom_readme_content
                == DEFAULT_README_HTML
            ):
                self.readme_choice = "default"
            else:
                self.readme_choice = "customize"
            self.stakeholder_comments = (
                project_s.current_project_stakeholder_comments
            )
            metrics_config = (
                project_s.current_project_metrics_config
            )
            if metrics_config:
                self.included_evergreen_metrics = (
                    metrics_config["evergreen"]
                )
                self.custom_metrics = metrics_config[
                    "custom"
                ]
            metric_weights_proj = (
                project_s.current_project_metric_weights
            )
            if metric_weights_proj:
                self.metric_weights = (
                    metric_weights_proj.copy()
                )
            self.pass_threshold = (
                project_s.current_project_pass_threshold
            )
            self.pass_definition = (
                project_s.current_project_pass_definition
            )
            self.excel_columns_for_session = (
                project_s.current_project_excel_columns.copy()
            )
            self._update_scoring_columns_from_metrics()
            self._update_scoring_columns_from_engines()
            self._update_excel_formulas()
        else:
            logger.info(
                "FilePrepState: No project selected, using default initial values."
            )
            self._update_scoring_columns_from_metrics()
            self._update_scoring_columns_from_engines()
            self._update_excel_formulas()
        logger.info("FilePrepState: Reset complete.")