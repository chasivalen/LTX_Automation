import reflex as rx
from typing import Optional, Literal, TypedDict
import uuid
import re

Language = Literal[
    "English",
    "Spanish",
    "French",
    "German",
    "Korean",
    "Japanese",
    "Chinese",
]
ReadmeChoice = Literal["default", "customize", "new"]
ColumnGroup = Literal[
    "Input",
    "Pre-Evaluation",
    "Metric",
    "Calculated Score",
    "Freeform",
]
DEFAULT_README_TEXT = "1. Please read through READ ME tab before you kick off the Evaluation Task:\na. Check out the Metrics and their corresponding Definitions & Notes to understand what aspects of the language performance you are evaluating against;\nb. Check out the Scoring Definition section to understand how you should be scoring each segment from a range of 1 to 5;\nc. The Weights/Percentage section is for your reference as to how much each metric is valued for this specific project.\n\n2. Once you are done reading through the READ ME tab, please move on to the Part 1 tabs to start the actual evaluation task. \n\n3. Pre-Eval: Before you start evaluating a segment, please take a quick look at both the SOURCE and TARGET columns, and:\na.If you find the source quality of a segment in SOURCE Column too terrible to understand, please choose Incomprehensible Input from the dropdown list of Pre-Eval column and skip the evaluation of this segment;\nb. If you find that the content in TARGET Column is not the translation of source, please choose Irrelevant Target from the dropdown list and score 0.9 under every metric for this segment.\n\n4. If you don't see a big issue with either the SOURCE or TARGET, please start evaluating the segment from TARGET column\na. First give an overall score (1 to 5) for the whole segment under the \"Overall\" Column;\nb. Then evaluate per metric with a scoring range from 1 to 5;\nc. Metrics are divided into “Evergreen” and “Customized”, so please make sure to score all of them;\nd. Please score each metric based on the overall performance in this aspect according to the scoring definition; \ne. If a translation issue has an impact on more than one metric, please penalize it accordingly in multiple metrics as needed.\n\n5. Overall Rating will be automatically calculated with pre-filled formulas in both non-weighted and weighted forms, so please don’t touch any of the RATING Columns.\n\n6. If you have any comments for the segment, you could leave them under the Additional Notes Column\n\n7. After completing the rating work for Part 1, please review the entire section again to check for any cells with a yellow background. If a cell has a yellow background, it's possible that you have either forgotten to add a rating or entered an invalid rating value.\n\n8. With the evaluation done, all relevant data will be automatically pulled to Part 2 - Data Analysis tab for data analysis in both numbers and visuals formats, and comparison will be available if evaluation is done on multiple tools.\n\n9. Based on data displayed in Part 2 - Data Analysis tab, please provide your take on the performance of each tool included in the Data Analysis Summary at the top of the tab, and make sure to answer all questions listed to be thorough.\n\n10. In Part 3 - Criteria Based Assess tab, please provide comments to questions regarding criteria specific to the project and your overall summary for you locale, so that the Project Lead can incorporate your opinions into the final Report.\n\n11. Once you are done with the whole process, please rename your file by adding the Completion Date and Your name.\n"
EVERGREEN_METRICS: dict[str, str] = {
    "Accuracy": "Source information is misinterpreted for the target translation, Numbers mismatch, Acronym mismatch.",
    "Omission/Addition": "Part of a segment missing or left in English, unnecessary/irrelevant information added to the target translation.",
    "Compliance": "Company Style & Terminology, Country standards, CompanyCare Style & Terminology; Product/accessory/feature names, DNT, commonly used expressions within Company; Date and time formats, format of the numbers not converting; Consistency with Terminology, Jargons and within the same article; Could be less important at the stage where the engine hasn't been trained with CompanyCare content.",
    "Fluency": "Doesn't conform to grammar and syntactic rules of the target language, collocation issues, punctuation & spelling issues, wrong punctuations, missing spacing, typos; unidiomatic or unnatural translation, uneasy to understand.",
}


class CustomMetric(TypedDict):
    name: str
    definition: str


class ExcelColumn(TypedDict, total=False):
    name: str
    id: str
    group: ColumnGroup
    description: Optional[str]
    editable_name: bool
    movable_within_group: bool
    required: bool
    metric_source: bool
    is_first_movable_in_group: bool
    is_last_movable_in_group: bool
    formula_description: Optional[str]
    formula_excel_style: Optional[str]


class MetricInfo(TypedDict):
    name: str
    definition: str


DEFAULT_EXCEL_COLUMNS_DATA: list[ExcelColumn] = [
    {
        "name": "File Name",
        "id": "file_name",
        "group": "Input",
        "description": "Source-driven input from uploaded files.",
        "editable_name": False,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
    },
    {
        "name": "Source",
        "id": "source",
        "group": "Input",
        "description": "Source text segment.",
        "editable_name": False,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
    },
    {
        "name": "Target",
        "id": "target",
        "group": "Input",
        "description": "Translated text segment.",
        "editable_name": False,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
    },
    {
        "name": "Word Count",
        "id": "word_count",
        "group": "Pre-Evaluation",
        "description": "Source word count (formula driven).",
        "editable_name": True,
        "movable_within_group": True,
        "required": False,
        "metric_source": False,
        "formula_description": "Calculates the number of words in the 'Source' column for the current row.",
        "formula_excel_style": '=IF(ISBLANK(SourceCell),0,LEN(TRIM(SourceCell))-LEN(SUBSTITUTE(TRIM(SourceCell)," ",""))+1)',
    },
    {
        "name": "Pre-Eval",
        "id": "pre_eval",
        "group": "Pre-Evaluation",
        "description": "Contextual filter (drop-down selection).",
        "editable_name": True,
        "movable_within_group": True,
        "required": True,
        "metric_source": False,
    },
    {
        "name": "Applicable Word Count",
        "id": "applicable_word_count",
        "group": "Pre-Evaluation",
        "description": "Word count after pre-evaluation (formula driven).",
        "editable_name": True,
        "movable_within_group": True,
        "required": False,
        "metric_source": False,
        "formula_description": "If 'Pre-Eval' is 'Incomprehensible Input' or 'Irrelevant Target', this is 0. Otherwise, it's the 'Word Count'.",
        "formula_excel_style": '=IF(OR(PreEvalCell="Incomprehensible Input", PreEvalCell="Irrelevant Target"),0,WordCountCell)',
    },
    {
        "name": "Overall",
        "id": "overall",
        "group": "Pre-Evaluation",
        "description": "Overall segment score (user input).",
        "editable_name": True,
        "movable_within_group": True,
        "required": True,
        "metric_source": False,
    },
    {
        "name": "Rating (Not Weighted)",
        "id": "rating_not_weighted",
        "group": "Calculated Score",
        "description": "Calculated score (formula driven). Averages all metric scores.",
        "editable_name": False,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
        "formula_description": "Calculates the simple average of all included metric scores for the current row.",
        "formula_excel_style": "=AVERAGE(MetricRange)",
    },
    {
        "name": "Rating (Weighted)",
        "id": "rating_weighted",
        "group": "Calculated Score",
        "description": "Weighted calculated score (formula driven). Uses defined metric weights.",
        "editable_name": False,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
        "formula_description": "Calculates the weighted average of metric scores based on their assigned weights.",
        "formula_excel_style": "=SUMPRODUCT(MetricScoreRange, MetricWeightRange) / SUM(MetricWeightRange)",
    },
    {
        "name": "Additional Notes",
        "id": "additional_notes",
        "group": "Freeform",
        "description": "Evaluator's freeform comments.",
        "editable_name": True,
        "movable_within_group": False,
        "required": False,
        "metric_source": False,
    },
]
COLUMN_GROUPS_ORDER: list[ColumnGroup] = [
    "Input",
    "Pre-Evaluation",
    "Metric",
    "Calculated Score",
    "Freeform",
]


class FilePrepState(rx.State):
    """Manages state specific to the File Prep view."""

    available_languages: list[Language] = [
        "English",
        "Spanish",
        "French",
        "German",
        "Korean",
        "Japanese",
        "Chinese",
    ]
    current_source_language: Language | None = None
    current_target_language: Language | None = None
    selected_pairs_for_session: list[tuple[str, str]] = []
    pairs_confirmed: bool = False
    available_engines: list[str] = [
        "Banana MT",
        "Banana FM",
    ]
    selected_engines: list[str] = []
    new_engine_name: str = ""
    engines_confirmed: bool = False
    readme_choice: ReadmeChoice | None = None
    custom_readme_content: str = DEFAULT_README_TEXT
    readme_confirmed: bool = False
    default_readme: str = DEFAULT_README_TEXT
    stakeholder_comments: str = ""
    stakeholder_confirmed: bool = False
    evergreen_metrics_definitions: dict[str, str] = (
        EVERGREEN_METRICS
    )
    included_evergreen_metrics: list[str] = list(
        EVERGREEN_METRICS.keys()
    )
    custom_metrics: list[CustomMetric] = []
    new_custom_metric_name: str = ""
    new_custom_metric_definition: str = ""
    metric_weights: dict[str, int] = {
        metric: 5 for metric in EVERGREEN_METRICS
    }
    metrics_confirmed: bool = False
    pass_threshold: float | None = None
    pass_definition: str = ""
    excel_columns: list[ExcelColumn] = [
        ExcelColumn(**col_data)
        for col_data in DEFAULT_EXCEL_COLUMNS_DATA
    ]
    columns_confirmed: bool = False
    editing_column_id: Optional[str] = None
    editing_column_name: str = ""
    show_formula_modal: bool = False
    selected_column_for_formula: Optional[ExcelColumn] = (
        None
    )

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
            and (
                self.current_source_language
                != self.current_target_language
            )
        ):
            new_pair = (
                self.current_source_language,
                self.current_target_language,
            )
            if (
                new_pair
                not in self.selected_pairs_for_session
            ):
                self.selected_pairs_for_session.append(
                    new_pair
                )
                self.current_source_language = None
                self.current_target_language = None
            else:
                yield rx.toast(
                    "This language pair has already been added.",
                    duration=3000,
                )
        elif (
            self.current_source_language
            and self.current_target_language
            and (
                self.current_source_language
                == self.current_target_language
            )
        ):
            yield rx.toast(
                "Source and Target languages cannot be the same.",
                duration=3000,
            )
        else:
            yield rx.toast(
                "Please select both a Source and Target language.",
                duration=3000,
            )

    @rx.event
    def remove_language_pair(
        self, pair_to_remove: tuple[str, str]
    ):
        self.selected_pairs_for_session = [
            pair
            for pair in self.selected_pairs_for_session
            if pair != pair_to_remove
        ]

    @rx.event
    async def confirm_language_pairs(self):
        from app.states.project_state import ProjectState

        if not self.selected_pairs_for_session:
            yield rx.toast(
                "Please add at least one language pair.",
                duration=3000,
            )
            return
        project_state = await self.get_state(ProjectState)
        if project_state.selected_project:
            project_state.project_language_pairs[
                project_state.selected_project
            ] = list(self.selected_pairs_for_session)
            self.selected_engines = list(
                project_state.project_mt_engines.get(
                    project_state.selected_project, []
                )
            )
            self.pairs_confirmed = True
            self._reset_downstream_of_pairs()
            yield rx.toast(
                "Language pairs confirmed! Select MT engines next.",
                duration=3000,
            )
        else:
            yield rx.toast(
                "Error: No project selected. Cannot confirm pairs.",
                duration=4000,
            )

    @rx.event
    def set_new_engine_name(self, name: str):
        self.new_engine_name = name

    @rx.event
    def toggle_engine(self, engine_name: str):
        if engine_name in self.selected_engines:
            self.selected_engines = [
                eng
                for eng in self.selected_engines
                if eng != engine_name
            ]
        else:
            self.selected_engines.append(engine_name)

    @rx.event
    def add_custom_engine(self):
        name = self.new_engine_name.strip()
        if name and name not in self.selected_engines:
            self.selected_engines.append(name)
            if name not in self.available_engines:
                self.available_engines.append(name)
            self.new_engine_name = ""
        elif not name:
            yield rx.toast(
                "Please enter an engine name.",
                duration=3000,
            )
        else:
            yield rx.toast(
                f"Engine '{name}' is already selected.",
                duration=3000,
            )

    @rx.event
    def remove_engine(self, engine_name: str):
        self.selected_engines = [
            eng
            for eng in self.selected_engines
            if eng != engine_name
        ]

    @rx.event
    async def confirm_engines(self):
        from app.states.project_state import ProjectState

        if not self.selected_engines:
            yield rx.toast(
                "Please select or add at least one MT engine.",
                duration=3000,
            )
            return
        project_state = await self.get_state(ProjectState)
        if project_state.selected_project:
            project_state.project_mt_engines[
                project_state.selected_project
            ] = list(self.selected_engines)
            self._load_project_data_after_engines(
                project_state
            )
            self.engines_confirmed = True
            self._reset_downstream_of_engines()
            yield rx.toast(
                "MT Engines confirmed! Customize Read Me instructions next.",
                duration=3000,
            )
        else:
            yield rx.toast(
                "Error: No project selected. Cannot confirm engines.",
                duration=4000,
            )

    @rx.event
    async def set_readme_choice(self, choice: ReadmeChoice):
        from app.states.project_state import ProjectState

        self.readme_choice = choice
        project_state = await self.get_state(ProjectState)
        saved_readme = (
            project_state.project_readme_content.get(
                project_state.selected_project,
                self.default_readme,
            )
            if project_state
            and project_state.selected_project
            else self.default_readme
        )
        if choice == "default":
            self.custom_readme_content = self.default_readme
        elif choice == "customize":
            if (
                self.custom_readme_content
                == self.default_readme
                or not self.custom_readme_content.strip()
            ):
                self.custom_readme_content = (
                    self.default_readme
                )
        elif choice == "new":
            if (
                self.custom_readme_content
                == self.default_readme
            ):
                self.custom_readme_content = ""

    @rx.event
    def set_custom_readme_content(self, content: str):
        self.custom_readme_content = content

    @rx.event
    async def confirm_readme(self):
        from app.states.project_state import ProjectState

        project_state = await self.get_state(ProjectState)
        if not project_state.selected_project:
            yield rx.toast(
                "Error: No project selected. Cannot confirm Read Me.",
                duration=4000,
            )
            return
        final_content = self.final_readme_content
        if self.readme_choice in ["customize", "new"] and (
            not final_content.strip()
        ):
            yield rx.toast(
                "Custom/New Read Me cannot be empty. Please provide instructions or choose 'Use Default'.",
                duration=4000,
            )
            return
        project_state.project_readme_content[
            project_state.selected_project
        ] = final_content
        self.readme_confirmed = True
        self._reset_downstream_of_readme()
        self.stakeholder_comments = (
            project_state.project_stakeholder_comments.get(
                project_state.selected_project, ""
            )
        )
        yield rx.toast(
            "Read Me Instructions Confirmed! Add Stakeholder Perspective next.",
            duration=3000,
        )

    @rx.event
    def set_stakeholder_comments(self, comments: str):
        self.stakeholder_comments = comments

    @rx.event
    async def confirm_stakeholder_perspective(self):
        from app.states.project_state import ProjectState

        project_state = await self.get_state(ProjectState)
        if not project_state.selected_project:
            yield rx.toast(
                "Error: No project selected. Cannot confirm Stakeholder Perspective.",
                duration=4000,
            )
            return
        project_state.project_stakeholder_comments[
            project_state.selected_project
        ] = self.stakeholder_comments
        self.stakeholder_confirmed = True
        self._reset_downstream_of_stakeholder()
        self._load_metric_pass_column_data(project_state)
        yield rx.toast(
            "Stakeholder Perspective Confirmed! Define Metrics next.",
            duration=3000,
        )

    @rx.event
    def toggle_evergreen_metric(self, metric_name: str):
        temp_metrics = list(self.included_evergreen_metrics)
        temp_weights = self.metric_weights.copy()
        if metric_name in temp_metrics:
            temp_metrics.remove(metric_name)
            if metric_name in temp_weights:
                del temp_weights[metric_name]
        else:
            temp_metrics.append(metric_name)
            if metric_name not in temp_weights:
                temp_weights[metric_name] = 5
        self.included_evergreen_metrics = temp_metrics
        self.metric_weights = temp_weights

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
        if not name or not definition:
            yield rx.toast(
                "Please enter both name and definition for the custom metric.",
                duration=3000,
            )
            return
        all_existing_names_lower = [
            m["name"].lower() for m in self.custom_metrics
        ] + [
            eg.lower()
            for eg in self.evergreen_metrics_definitions
        ]
        if name.lower() in all_existing_names_lower:
            yield rx.toast(
                f"A metric with the name '{name}' already exists.",
                duration=3000,
            )
            return
        self.custom_metrics.append(
            CustomMetric(name=name, definition=definition)
        )
        temp_weights = self.metric_weights.copy()
        if name not in temp_weights:
            temp_weights[name] = 5
        self.metric_weights = temp_weights
        self.new_custom_metric_name = ""
        self.new_custom_metric_definition = ""

    @rx.event
    def remove_custom_metric(self, metric_name: str):
        self.custom_metrics = [
            m
            for m in self.custom_metrics
            if m["name"] != metric_name
        ]
        temp_weights = self.metric_weights.copy()
        if metric_name in temp_weights:
            del temp_weights[metric_name]
        self.metric_weights = temp_weights

    @rx.event
    def set_metric_weight(
        self, metric_name: str, weight_str: str
    ):
        temp_weights = self.metric_weights.copy()
        try:
            if weight_str == "":
                if metric_name in temp_weights:
                    del temp_weights[metric_name]
                self.metric_weights = temp_weights
                return
            weight = int(weight_str)
            if 1 <= weight <= 10:
                temp_weights[metric_name] = weight
            else:
                if metric_name in temp_weights:
                    del temp_weights[metric_name]
                yield rx.toast(
                    f"Weight for '{metric_name}' must be between 1 and 10. Weight cleared.",
                    duration=4000,
                )
        except ValueError:
            if metric_name in temp_weights:
                del temp_weights[metric_name]
            yield rx.toast(
                f"Invalid weight for '{metric_name}'. Please enter a number 1-10. Weight cleared.",
                duration=4000,
            )
        self.metric_weights = temp_weights

    @rx.event
    def set_pass_threshold(self, threshold_str: str):
        try:
            if threshold_str == "":
                self.pass_threshold = None
            else:
                threshold = float(threshold_str)
                self.pass_threshold = threshold
        except ValueError:
            self.pass_threshold = None
            yield rx.toast(
                "Invalid number for Pass Threshold. Please enter a valid number or leave blank.",
                duration=3000,
            )

    @rx.event
    def set_pass_definition(self, definition: str):
        self.pass_definition = definition

    @rx.event
    async def confirm_metrics(self):
        from app.states.project_state import ProjectState

        missing_weights = []
        for metric in self.all_included_metrics:
            metric_name = metric["name"]
            if metric_name not in self.metric_weights:
                missing_weights.append(metric_name)
            elif (
                not 1
                <= self.metric_weights[metric_name]
                <= 10
            ):
                missing_weights.append(metric_name)
        if not self.all_included_metrics:
            yield rx.toast(
                "Please include at least one metric.",
                duration=3000,
            )
            return
        if missing_weights:
            yield rx.toast(
                f"Missing or invalid weight (1-10) for: {', '.join(missing_weights)}. Please assign weights.",
                duration=5000,
            )
            return
        threshold_set = self.pass_threshold is not None
        definition_set = self.pass_definition.strip() != ""
        if threshold_set != definition_set:
            yield rx.toast(
                "Both Pass Threshold and Pass Definition must be set, or neither.",
                duration=4000,
            )
            return
        project_state = await self.get_state(ProjectState)
        if not project_state.selected_project:
            yield rx.toast(
                "Error: No project selected. Cannot confirm Metrics.",
                duration=4000,
            )
            return
        project_name = project_state.selected_project
        project_state.project_included_metrics[
            project_name
        ] = {
            "evergreen": list(
                self.included_evergreen_metrics
            ),
            "custom": list(self.custom_metrics),
        }
        project_state.project_metric_weights[
            project_name
        ] = dict(self.metric_weights)
        project_state.project_pass_threshold[
            project_name
        ] = self.pass_threshold
        project_state.project_pass_definition[
            project_name
        ] = self.pass_definition
        self.metrics_confirmed = True
        self._reset_downstream_of_metrics()
        saved_cols_raw = (
            project_state.project_excel_columns.get(
                project_name
            )
        )
        if saved_cols_raw:
            self.excel_columns = [
                ExcelColumn(**col) for col in saved_cols_raw
            ]
        else:
            self.excel_columns = [
                ExcelColumn(**col)
                for col in DEFAULT_EXCEL_COLUMNS_DATA
            ]
        self.editing_column_id = None
        self.editing_column_name = ""
        yield rx.toast(
            "Metrics, Weights & Pass Criteria Confirmed! Define Excel Columns next.",
            duration=3000,
        )

    @rx.event
    def move_column(
        self,
        column_id: str,
        direction: Literal["left", "right"],
    ):
        cols = list(self.excel_columns)
        idx_target = -1
        for i, col_data in enumerate(cols):
            if col_data["id"] == column_id:
                idx_target = i
                break
        if idx_target == -1:
            yield rx.toast(
                "Column not found.", duration=3000
            )
            return
        target_column_data = cols[idx_target]
        if not target_column_data.get(
            "movable_within_group"
        ):
            yield rx.toast(
                "This column is not movable.", duration=3000
            )
            return
        target_group = target_column_data["group"]
        idx_swap = -1
        if direction == "left":
            for i in range(idx_target - 1, -1, -1):
                if cols[i][
                    "group"
                ] == target_group and cols[i].get(
                    "movable_within_group"
                ):
                    idx_swap = i
                    break
        elif direction == "right":
            for i in range(idx_target + 1, len(cols)):
                if cols[i][
                    "group"
                ] == target_group and cols[i].get(
                    "movable_within_group"
                ):
                    idx_swap = i
                    break
        if idx_swap != -1:
            cols[idx_target], cols[idx_swap] = (
                cols[idx_swap],
                cols[idx_target],
            )
            self.excel_columns = cols
            if self.editing_column_id == column_id:
                self.editing_column_id = None
                self.editing_column_name = ""
        else:
            yield rx.toast(
                "Cannot move column further in this direction.",
                duration=2000,
            )

    @rx.event
    def start_editing_column_name(self, column_id: str):
        try:
            column_to_edit = next(
                (
                    col
                    for col in self.excel_columns
                    if col["id"] == column_id
                )
            )
            if column_to_edit.get("editable_name"):
                self.editing_column_id = column_id
                self.editing_column_name = column_to_edit[
                    "name"
                ]
            else:
                yield rx.toast(
                    "This column name cannot be edited.",
                    duration=2000,
                )
        except StopIteration:
            yield rx.toast(
                f"Invalid column ID '{column_id}' for editing.",
                duration=3000,
            )

    @rx.event
    def set_editing_column_name(self, name: str):
        self.editing_column_name = name

    @rx.event
    def save_column_name(self):
        if self.editing_column_id is None:
            return
        idx_to_edit = -1
        for i, col in enumerate(self.excel_columns):
            if col["id"] == self.editing_column_id:
                idx_to_edit = i
                break
        if idx_to_edit == -1:
            yield rx.toast(
                f"Error saving: Column ID '{self.editing_column_id}' not found.",
                duration=3000,
            )
            self.editing_column_id = None
            self.editing_column_name = ""
            return
        new_name = self.editing_column_name.strip()
        original_name = self.excel_columns[idx_to_edit][
            "name"
        ]
        if not new_name:
            yield rx.toast(
                "Column name cannot be empty.",
                duration=3000,
            )
            return
        if new_name != original_name:
            if any(
                (
                    col["name"] == new_name
                    and col["id"] != self.editing_column_id
                    for col in self.excel_columns
                    if not col.get("metric_source")
                )
            ):
                yield rx.toast(
                    f"Column name '{new_name}' already exists among base columns.",
                    duration=3000,
                )
                return
            if any(
                (
                    metric_info["name"] == new_name
                    for metric_info in self.all_included_metrics
                )
            ):
                yield rx.toast(
                    f"Column name '{new_name}' conflicts with an active metric name.",
                    duration=3000,
                )
                return
        temp_cols = [
            col.copy() for col in self.excel_columns
        ]
        temp_cols[idx_to_edit]["name"] = new_name
        self.excel_columns = temp_cols
        self.editing_column_id = None
        self.editing_column_name = ""

    @rx.event
    def cancel_editing_column_name(self):
        self.editing_column_id = None
        self.editing_column_name = ""

    @rx.event
    async def confirm_columns(self):
        from app.states.project_state import ProjectState

        if self.editing_column_id is not None:
            yield rx.toast(
                "Please finish editing the column name first (Save or Cancel).",
                duration=3000,
            )
            return
        project_state = await self.get_state(ProjectState)
        if not project_state.selected_project:
            yield rx.toast(
                "Error: No project selected. Cannot confirm Columns.",
                duration=4000,
            )
            return
        project_name = project_state.selected_project
        base_columns_to_save = [
            ExcelColumn(**col)
            for col in self.excel_columns
            if not col.get("metric_source")
        ]
        project_state.project_excel_columns[
            project_name
        ] = base_columns_to_save
        self.columns_confirmed = True
        self.show_formula_modal = False
        self.selected_column_for_formula = None
        yield rx.toast(
            "Excel Columns Confirmed! Configuration complete.",
            duration=3000,
        )

    def _reset_downstream_of_pairs(self):
        self.engines_confirmed = False
        self.selected_engines = []
        self.new_engine_name = ""
        self._reset_downstream_of_engines()

    def _reset_downstream_of_engines(self):
        self.readme_confirmed = False
        self.readme_choice = None
        self.custom_readme_content = self.default_readme
        self._reset_downstream_of_readme()

    def _reset_downstream_of_readme(self):
        self.stakeholder_confirmed = False
        self.stakeholder_comments = ""
        self._reset_downstream_of_stakeholder()

    def _reset_downstream_of_stakeholder(self):
        self.metrics_confirmed = False
        self._reset_metric_and_pass_state()
        self._reset_downstream_of_metrics()

    def _reset_downstream_of_metrics(self):
        self.columns_confirmed = False
        self._reset_column_state()

    def _reset_metric_and_pass_state(self):
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

    def _reset_column_state(self):
        self.excel_columns = [
            ExcelColumn(**col_data)
            for col_data in DEFAULT_EXCEL_COLUMNS_DATA
        ]
        self.editing_column_id = None
        self.editing_column_name = ""
        self.show_formula_modal = False
        self.selected_column_for_formula = None

    def _load_project_data_after_engines(
        self, project_state
    ):
        if not project_state.selected_project:
            self._reset_downstream_of_engines()
            return
        project_name = project_state.selected_project
        saved_readme = (
            project_state.project_readme_content.get(
                project_name, self.default_readme
            )
        )
        self.custom_readme_content = saved_readme
        if saved_readme == self.default_readme:
            self.readme_choice = "default"
        elif not saved_readme.strip():
            self.readme_choice = "new"
        else:
            default_cleaned = re.sub(
                "\\s+", " ", self.default_readme
            ).strip()
            saved_cleaned = re.sub(
                "\\s+", " ", saved_readme
            ).strip()
            if saved_cleaned == default_cleaned:
                self.readme_choice = "default"
            else:
                self.readme_choice = "customize"
        self.stakeholder_comments = (
            project_state.project_stakeholder_comments.get(
                project_name, ""
            )
        )
        self._load_metric_pass_column_data(project_state)

    def _load_metric_pass_column_data(self, project_state):
        if not project_state.selected_project:
            self._reset_metric_and_pass_state()
            self._reset_column_state()
            return
        project_name = project_state.selected_project
        saved_metrics_config = (
            project_state.project_included_metrics.get(
                project_name, None
            )
        )
        saved_weights = (
            project_state.project_metric_weights.get(
                project_name, None
            )
        )
        if (
            saved_metrics_config
            and saved_weights is not None
        ):
            self.included_evergreen_metrics = list(
                saved_metrics_config.get(
                    "evergreen",
                    list(EVERGREEN_METRICS.keys()),
                )
            )
            saved_custom_raw = saved_metrics_config.get(
                "custom", []
            )
            self.custom_metrics = [
                CustomMetric(
                    name=cm["name"],
                    definition=cm["definition"],
                )
                for cm in saved_custom_raw
            ]
            loaded_weights = dict(saved_weights)
            current_weights: dict[str, int] = {}
            all_metric_names_to_load = (
                self.included_evergreen_metrics
                + [cm["name"] for cm in self.custom_metrics]
            )
            for name in all_metric_names_to_load:
                weight = loaded_weights.get(name, 5)
                try:
                    weight_int = int(weight)
                    if not 1 <= weight_int <= 10:
                        weight_int = 5
                except (ValueError, TypeError):
                    weight_int = 5
                current_weights[name] = weight_int
            self.metric_weights = current_weights
        else:
            self._reset_metric_and_pass_state()
        self.pass_threshold = (
            project_state.project_pass_threshold.get(
                project_name, None
            )
        )
        self.pass_definition = (
            project_state.project_pass_definition.get(
                project_name, ""
            )
        )
        saved_base_columns_raw = (
            project_state.project_excel_columns.get(
                project_name
            )
        )
        if saved_base_columns_raw is not None:
            self.excel_columns = [
                ExcelColumn(**col_data)
                for col_data in saved_base_columns_raw
            ]
        else:
            self.excel_columns = [
                ExcelColumn(**col_data)
                for col_data in DEFAULT_EXCEL_COLUMNS_DATA
            ]
        self.editing_column_id = None
        self.editing_column_name = ""

    @rx.event
    def reset_state(self):
        self.current_source_language = None
        self.current_target_language = None
        self.selected_pairs_for_session = []
        self.pairs_confirmed = False
        self.available_engines = ["Banana MT", "Banana FM"]
        self.selected_engines = []
        self.new_engine_name = ""
        self.engines_confirmed = False
        self.readme_choice = None
        self.custom_readme_content = self.default_readme
        self.readme_confirmed = False
        self.stakeholder_comments = ""
        self.stakeholder_confirmed = False
        self._reset_metric_and_pass_state()
        self.metrics_confirmed = False
        self._reset_column_state()
        self.columns_confirmed = False

    @rx.event
    def set_pairs_confirmed(self, confirmed: bool):
        self.pairs_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_pairs()

    @rx.event
    def set_engines_confirmed(self, confirmed: bool):
        self.engines_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_engines()

    @rx.event
    def set_readme_confirmed(self, confirmed: bool):
        self.readme_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_readme()

    @rx.event
    def set_stakeholder_confirmed(self, confirmed: bool):
        self.stakeholder_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_stakeholder()

    @rx.event
    def set_metrics_confirmed(self, confirmed: bool):
        self.metrics_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_metrics()

    @rx.event
    def set_columns_confirmed(self, confirmed: bool):
        self.columns_confirmed = confirmed
        if confirmed:
            self.show_formula_modal = False
            self.selected_column_for_formula = None

    @rx.event
    def show_formula_info(self, column_id: str):
        all_display_cols = self.display_excel_columns
        found_column: Optional[ExcelColumn] = None
        for col in all_display_cols:
            if col["id"] == column_id:
                found_column = col
                break
        if found_column and (
            found_column.get("formula_description")
            or found_column.get("formula_excel_style")
        ):
            self.selected_column_for_formula = found_column
            self.show_formula_modal = True
        else:
            yield rx.toast(
                "No formula information available for this column.",
                duration=3000,
            )

    @rx.event
    def hide_formula_info(self):
        self.show_formula_modal = False
        self.selected_column_for_formula = None

    @rx.var
    def is_add_pair_disabled(self) -> bool:
        return (
            not self.current_source_language
            or not self.current_target_language
            or self.current_source_language
            == self.current_target_language
        )

    @rx.var
    def is_confirm_pairs_disabled(self) -> bool:
        return not self.selected_pairs_for_session

    @rx.var
    def is_add_engine_disabled(self) -> bool:
        return not self.new_engine_name.strip()

    @rx.var
    def is_confirm_engines_disabled(self) -> bool:
        return not self.selected_engines

    @rx.var
    def is_confirm_readme_disabled(self) -> bool:
        if self.readme_choice is None:
            return True
        if self.readme_choice in ["customize", "new"] and (
            not self.custom_readme_content.strip()
        ):
            return True
        return False

    @rx.var
    def is_confirm_stakeholder_disabled(self) -> bool:
        return False

    @rx.var
    def is_add_custom_metric_disabled(self) -> bool:
        return (
            not self.new_custom_metric_name.strip()
            or not self.new_custom_metric_definition.strip()
        )

    @rx.var
    def is_confirm_metrics_disabled(self) -> bool:
        if not self.all_included_metrics:
            return True
        for metric in self.all_included_metrics:
            metric_name = metric["name"]
            if metric_name not in self.metric_weights:
                return True
            weight = self.metric_weights[metric_name]
            if not (
                isinstance(weight, int)
                and 1 <= weight <= 10
            ):
                return True
        threshold_set = self.pass_threshold is not None
        definition_set = self.pass_definition.strip() != ""
        if threshold_set != definition_set:
            return True
        return False

    @rx.var
    def is_confirm_columns_disabled(self) -> bool:
        return self.editing_column_id is not None

    @rx.var
    def final_readme_content(self) -> str:
        if self.readme_choice == "default":
            return self.default_readme
        elif self.readme_choice in ["customize", "new"]:
            return self.custom_readme_content
        return self.default_readme

    @rx.var
    def all_included_metrics(self) -> list[MetricInfo]:
        metrics: list[MetricInfo] = []
        for name in self.included_evergreen_metrics:
            metrics.append(
                MetricInfo(
                    name=name,
                    definition=self.evergreen_metrics_definitions.get(
                        name, "Definition not found."
                    ),
                )
            )
        for custom_metric in self.custom_metrics:
            metrics.append(
                MetricInfo(
                    name=custom_metric["name"],
                    definition=custom_metric["definition"],
                )
            )
        return metrics

    @rx.var
    def total_metric_weight(self) -> int:
        total = 0
        all_included_metric_names = [
            m["name"] for m in self.all_included_metrics
        ]
        for name in all_included_metric_names:
            weight = self.metric_weights.get(name)
            if (
                isinstance(weight, int)
                and 1 <= weight <= 10
            ):
                total += weight
        return total

    @rx.var
    def final_excel_columns_for_display(
        self,
    ) -> list[tuple[ColumnGroup, list[ExcelColumn]]]:
        grouped_display_columns: dict[
            ColumnGroup, list[ExcelColumn]
        ] = {group: [] for group in COLUMN_GROUPS_ORDER}
        for col_data_orig in self.excel_columns:
            if col_data_orig.get("metric_source"):
                continue
            col_data = col_data_orig.copy()
            group = col_data.get("group")
            if group and group in grouped_display_columns:
                full_col_data: ExcelColumn = {
                    "name": col_data.get(
                        "name", "Unknown Column"
                    ),
                    "id": col_data.get(
                        "id",
                        f"unknown_id_{uuid.uuid4().hex[:6]}",
                    ),
                    "group": group,
                    "description": col_data.get(
                        "description"
                    ),
                    "editable_name": col_data.get(
                        "editable_name", False
                    ),
                    "movable_within_group": col_data.get(
                        "movable_within_group", False
                    ),
                    "required": col_data.get(
                        "required", False
                    ),
                    "metric_source": False,
                    "formula_description": col_data.get(
                        "formula_description"
                    ),
                    "formula_excel_style": col_data.get(
                        "formula_excel_style"
                    ),
                    "is_first_movable_in_group": False,
                    "is_last_movable_in_group": False,
                }
                grouped_display_columns[group].append(
                    full_col_data
                )
        metric_display_cols: list[ExcelColumn] = []
        for metric_info in self.all_included_metrics:
            metric_name = metric_info["name"]
            metric_col_id = f"metric_{metric_name.lower().replace(' ', '_').replace('/', '_')}"
            metric_display_cols.append(
                ExcelColumn(
                    name=metric_name,
                    id=metric_col_id,
                    group="Metric",
                    description=metric_info["definition"],
                    editable_name=False,
                    movable_within_group=False,
                    required=True,
                    metric_source=True,
                    is_first_movable_in_group=False,
                    is_last_movable_in_group=False,
                )
            )
        if "Metric" not in grouped_display_columns:
            grouped_display_columns["Metric"] = []
        grouped_display_columns["Metric"].extend(
            metric_display_cols
        )
        result_with_flags: list[
            tuple[ColumnGroup, list[ExcelColumn]]
        ] = []
        for group_name_val in COLUMN_GROUPS_ORDER:
            cols_in_group_val = grouped_display_columns.get(
                group_name_val, []
            )
            processed_cols_in_group: list[ExcelColumn] = []
            movable_indices_in_this_group = [
                i
                for i, c in enumerate(cols_in_group_val)
                if c.get("movable_within_group")
            ]
            first_movable_idx = (
                movable_indices_in_this_group[0]
                if movable_indices_in_this_group
                else -1
            )
            last_movable_idx = (
                movable_indices_in_this_group[-1]
                if movable_indices_in_this_group
                else -1
            )
            for i, col_data_item_orig in enumerate(
                cols_in_group_val
            ):
                col_data_item = col_data_item_orig.copy()
                is_movable = col_data_item.get(
                    "movable_within_group", False
                )
                if is_movable:
                    col_data_item[
                        "is_first_movable_in_group"
                    ] = (i == first_movable_idx)
                    col_data_item[
                        "is_last_movable_in_group"
                    ] = (i == last_movable_idx)
                else:
                    col_data_item[
                        "is_first_movable_in_group"
                    ] = False
                    col_data_item[
                        "is_last_movable_in_group"
                    ] = False
                processed_cols_in_group.append(
                    col_data_item
                )
            result_with_flags.append(
                (group_name_val, processed_cols_in_group)
            )
        return result_with_flags

    @rx.var
    def display_excel_columns(self) -> list[ExcelColumn]:
        """Flattens final_excel_columns_for_display for older summary views and formula modal."""
        flat_list: list[ExcelColumn] = []
        for (
            _,
            cols_in_group,
        ) in self.final_excel_columns_for_display:
            flat_list.extend(cols_in_group)
        return flat_list