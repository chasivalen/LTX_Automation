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
)
import uuid
import re
import io
import csv

if TYPE_CHECKING:
    from app.states.project_state import ProjectState
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
    custom_user_added: bool
    removable: bool
    allow_file_upload: Optional[bool]


class MetricInfo(TypedDict):
    name: str
    definition: str


CJK_LANGUAGES: set[Language] = {
    "Chinese",
    "Japanese",
    "Korean",
}
SOURCE_CELL_DYNAMIC_FORMULA_PART = (
    'INDIRECT(ADDRESS(ROW(),MATCH("*Source*",1:1,0)))'
)
CJK_WORD_COUNT_EXCEL_FORMULA = f"=IF(ISBLANK({SOURCE_CELL_DYNAMIC_FORMULA_PART}),0,LEN(TRIM({SOURCE_CELL_DYNAMIC_FORMULA_PART})))"
GENERIC_WORD_COUNT_EXCEL_FORMULA = f'=IF(ISBLANK({SOURCE_CELL_DYNAMIC_FORMULA_PART}), 0, COUNTA(FILTERXML("<t><s>" & SUBSTITUTE(TRIM({SOURCE_CELL_DYNAMIC_FORMULA_PART})," ","</s><s>") & "</s></t>","//s")))'
DEFAULT_EXCEL_COLUMNS_DATA: list[ExcelColumn] = [
    {
        "name": "File Name",
        "id": "file_name",
        "group": "Input",
        "description": "Source-driven input from uploaded files.",
        "editable_name": True,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
        "custom_user_added": False,
        "removable": False,
        "allow_file_upload": True,
    },
    {
        "name": "Source",
        "id": "source",
        "group": "Input",
        "description": "Source text segment.",
        "editable_name": True,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
        "custom_user_added": False,
        "removable": False,
        "allow_file_upload": True,
    },
    {
        "name": "Target",
        "id": "target",
        "group": "Input",
        "description": "Translated text segment.",
        "editable_name": True,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
        "custom_user_added": False,
        "removable": False,
        "allow_file_upload": True,
    },
    {
        "name": "Word Count",
        "id": "word_count",
        "group": "Pre-Evaluation",
        "description": "Source word count (formula driven). Dynamically finds the 'Source' column. Formula adapts to CJK/Generic languages.",
        "editable_name": True,
        "movable_within_group": True,
        "required": False,
        "metric_source": False,
        "formula_description": "Calculates the number of words in the 'Source' column for the current row. The 'Source' column is identified by finding a header in row 1 containing the word 'Source'. The formula attempts to use character count for CJK languages and word count for others.",
        "formula_excel_style": GENERIC_WORD_COUNT_EXCEL_FORMULA,
        "custom_user_added": False,
        "removable": True,
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
        "custom_user_added": False,
        "removable": False,
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
        "formula_description": "If 'Pre-Eval' is 'Incomprehensible Input' or 'Irrelevant Target', this is 0. Otherwise, it's the 'Word Count'. This formula assumes 'Pre-Eval' and 'Word Count' columns exist and their exact cell references will be substituted by backend logic (e.g. PreEvalCell, WordCountCell).",
        "formula_excel_style": '=IF(OR(PreEvalCell="Incomprehensible Input", PreEvalCell="Irrelevant Target"),0,WordCountCell)',
        "custom_user_added": False,
        "removable": True,
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
        "custom_user_added": False,
        "removable": False,
    },
    {
        "name": "Rating (Not Weighted)",
        "id": "rating_not_weighted",
        "group": "Calculated Score",
        "description": "Calculated score (formula driven). Averages all metric scores. This formula assumes metric scores are in a contiguous range (MetricRange) that will be substituted by backend logic.",
        "editable_name": False,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
        "formula_description": "Calculates the simple average of all included metric scores for the current row.",
        "formula_excel_style": "=AVERAGE(MetricRange)",
        "custom_user_added": False,
        "removable": False,
    },
    {
        "name": "Rating (Weighted)",
        "id": "rating_weighted",
        "group": "Calculated Score",
        "description": "Weighted calculated score (formula driven). Uses defined metric weights. This formula assumes metric scores (MetricScoreRange) and their corresponding weights (MetricWeightRange) are in contiguous ranges that will be substituted by backend logic.",
        "editable_name": False,
        "movable_within_group": False,
        "required": True,
        "metric_source": False,
        "formula_description": "Calculates the weighted average of metric scores based on their assigned weights.",
        "formula_excel_style": "=SUMPRODUCT(MetricScoreRange, MetricWeightRange) / SUM(MetricWeightRange)",
        "custom_user_added": False,
        "removable": False,
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
        "custom_user_added": False,
        "removable": True,
    },
]
COLUMN_GROUPS_ORDER: list[ColumnGroup] = [
    "Input",
    "Pre-Evaluation",
    "Metric",
    "Calculated Score",
    "Freeform",
]
ColumnsInGroupList = list[ExcelColumn]
GroupWithColumnsTuple = tuple[
    ColumnGroup, ColumnsInGroupList
]
FinalExcelDisplayType = list[GroupWithColumnsTuple]
MAX_PREVIEW_ROWS = 10


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
    current_source_language: Optional[Language] = None
    current_target_language: Optional[Language] = None
    selected_pairs_for_session: list[tuple[str, str]] = []
    pairs_confirmed: bool = False
    available_engines: list[str] = ["\uf8ffMT", "\uf8ffFM"]
    selected_engines: list[str] = []
    new_engine_name: str = ""
    engines_confirmed: bool = False
    readme_choice: Optional[ReadmeChoice] = None
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
        col.copy() for col in DEFAULT_EXCEL_COLUMNS_DATA
    ]
    column_structure_finalized: bool = False
    editing_column_id: Optional[str] = None
    editing_column_name: str = ""
    show_formula_modal: bool = False
    selected_column_for_formula: Optional[ExcelColumn] = (
        None
    )
    new_column_inputs: dict[ColumnGroup, str] = {
        group: "" for group in COLUMN_GROUPS_ORDER
    }
    formula_review_active: bool = False
    editing_formula_column_id: Optional[str] = None
    editing_formula_description_input: str = ""
    editing_formula_excel_style_input: str = ""
    show_formula_wizard_modal: bool = False
    uploaded_file_data: Dict[str, List[List[str]]] = {}
    uploaded_file_info: Dict[str, str] = {}
    template_preview_ready: bool = False

    def _update_word_count_excel_formula(
        self, source_language: Language | None
    ):
        """
        Updates the Excel formula for the 'Word Count' column based on the source language.
        Uses character count for CJK languages, and a generic word count for others.
        """
        new_excel_columns = [
            col.copy() for col in self.excel_columns
        ]
        word_count_column_updated = False
        for i, col in enumerate(new_excel_columns):
            if col.get("id") == "word_count":
                if (
                    source_language
                    and source_language in CJK_LANGUAGES
                ):
                    new_excel_columns[i][
                        "formula_excel_style"
                    ] = CJK_WORD_COUNT_EXCEL_FORMULA
                else:
                    new_excel_columns[i][
                        "formula_excel_style"
                    ] = GENERIC_WORD_COUNT_EXCEL_FORMULA
                word_count_column_updated = True
                break
        if word_count_column_updated:
            self.excel_columns = new_excel_columns

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
                "Language pairs confirmed! Set MT model(s) next.",
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
                "Please enter 3rd party model(s).",
                duration=3000,
            )
        else:
            yield rx.toast(
                f"The model, '{name}', is already selected.",
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
                "Please select or add at least one MT model.",
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
                "MT Model(s) confirmed! Customize Read Me instructions next.",
                duration=3000,
            )
        else:
            yield rx.toast(
                "Error: No project selected. Cannot confirm MT model.",
                duration=4000,
            )

    @rx.event
    async def set_readme_choice(self, choice: ReadmeChoice):
        self.readme_choice = choice
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
        """Set the pass threshold after validating the input."""
        try:
            threshold_str_cleaned = str(
                threshold_str
            ).strip()
            self.pass_threshold = (
                float(threshold_str_cleaned)
                if threshold_str_cleaned
                else None
            )
        except ValueError:
            self.pass_threshold = None
            yield rx.toast(
                "Please enter a valid number for the pass threshold.",
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
                col.copy() for col in saved_cols_raw
            ]
        else:
            self.excel_columns = [
                col.copy()
                for col in DEFAULT_EXCEL_COLUMNS_DATA
            ]
        project_langs = (
            project_state.project_language_pairs.get(
                project_name, []
            )
        )
        primary_source_lang_for_project: Language | None = (
            None
        )
        if project_langs:
            primary_source_lang_for_project = cast(
                Language, project_langs[0][0]
            )
        self._update_word_count_excel_formula(
            primary_source_lang_for_project
        )
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
                if cols[i]["group"] == target_group:
                    if cols[i].get("movable_within_group"):
                        idx_swap = i
                        break
            current_movable_index_in_group = -1
            movable_items_in_group_indices = []
            for i, col_data_item in enumerate(cols):
                if col_data_item[
                    "group"
                ] == target_group and col_data_item.get(
                    "movable_within_group"
                ):
                    movable_items_in_group_indices.append(i)
                    if i == idx_target:
                        current_movable_index_in_group = (
                            len(
                                movable_items_in_group_indices
                            )
                            - 1
                        )
            if current_movable_index_in_group > 0:
                idx_swap = movable_items_in_group_indices[
                    current_movable_index_in_group - 1
                ]
        elif direction == "right":
            current_movable_index_in_group = -1
            movable_items_in_group_indices = []
            for i, col_data_item in enumerate(cols):
                if col_data_item[
                    "group"
                ] == target_group and col_data_item.get(
                    "movable_within_group"
                ):
                    movable_items_in_group_indices.append(i)
                    if i == idx_target:
                        current_movable_index_in_group = (
                            len(
                                movable_items_in_group_indices
                            )
                            - 1
                        )
            if (
                current_movable_index_in_group != -1
                and current_movable_index_in_group
                < len(movable_items_in_group_indices) - 1
            ):
                idx_swap = movable_items_in_group_indices[
                    current_movable_index_in_group + 1
                ]
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
                "Cannot move column further in this direction within its group.",
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
        if not new_name:
            yield rx.toast(
                "Column name cannot be empty.",
                duration=3000,
            )
            return
        all_current_display_names_lower = [
            col_data["name"].lower()
            for col_data in self.display_excel_columns
            if col_data["id"] != self.editing_column_id
        ]
        if (
            new_name.lower()
            in all_current_display_names_lower
        ):
            yield rx.toast(
                f"Column name '{new_name}' already exists or conflicts with a metric name.",
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
    def set_new_column_input_for_group(
        self, group: ColumnGroup, name: str
    ):
        self.new_column_inputs[group] = name

    @rx.event
    def add_new_column_to_group(
        self, group_name: ColumnGroup
    ):
        new_col_name = self.new_column_inputs[
            group_name
        ].strip()
        if not new_col_name:
            yield rx.toast(
                f"Please enter a name for the new column in {group_name}.",
                duration=3000,
            )
            return
        all_current_display_names_lower = [
            col_data["name"].lower()
            for col_data in self.display_excel_columns
        ]
        if (
            new_col_name.lower()
            in all_current_display_names_lower
        ):
            yield rx.toast(
                f"Column name '{new_col_name}' already exists or conflicts with a metric.",
                duration=3000,
            )
            return
        new_column_id = f"user_col_{uuid.uuid4().hex[:8]}"
        new_column: ExcelColumn = {
            "name": new_col_name,
            "id": new_column_id,
            "group": group_name,
            "description": "User-added column",
            "editable_name": True,
            "movable_within_group": True,
            "required": False,
            "metric_source": False,
            "custom_user_added": True,
            "removable": True,
            "formula_description": None,
            "formula_excel_style": None,
        }
        insert_at_index = len(self.excel_columns)
        for i in range(len(self.excel_columns) - 1, -1, -1):
            if self.excel_columns[i]["group"] == group_name:
                insert_at_index = i + 1
                break
        temp_excel_columns = list(self.excel_columns)
        temp_excel_columns.insert(
            insert_at_index, new_column
        )
        self.excel_columns = temp_excel_columns
        self.new_column_inputs[group_name] = ""
        yield rx.toast(
            f"Column '{new_col_name}' added to {group_name}.",
            duration=2000,
        )

    @rx.event
    def remove_column_by_id(self, column_id: str):
        col_to_remove = next(
            (
                col
                for col in self.excel_columns
                if col["id"] == column_id
            ),
            None,
        )
        if col_to_remove and col_to_remove.get("removable"):
            self.excel_columns = [
                col
                for col in self.excel_columns
                if col["id"] != column_id
            ]
            yield rx.toast(
                f"Column '{col_to_remove['name']}' removed.",
                duration=2000,
            )
        elif col_to_remove:
            yield rx.toast(
                f"Column '{col_to_remove['name']}' cannot be removed.",
                duration=3000,
            )
        else:
            yield rx.toast(
                f"Column with ID '{column_id}' not found.",
                duration=3000,
            )

    async def _save_column_structure_to_project(
        self,
    ) -> tuple[bool, str | None]:
        """
        Attempts to save the column structure. Does not yield toasts.
        Returns:
            A tuple (success: bool, error_message: Optional[str]).
            success is True if saved, False otherwise.
            error_message contains a message if success is False.
        """
        from app.states.project_state import ProjectState

        if self.editing_formula_column_id is not None:
            return (
                False,
                "Please save or cancel your current formula edit.",
            )
        if self.editing_column_id is not None:
            return (
                False,
                "Please save or cancel your current column name edit.",
            )
        project_state = await self.get_state(ProjectState)
        if not project_state.selected_project:
            return (
                False,
                "Error: No project selected. Cannot save column structure.",
            )
        project_name = project_state.selected_project
        base_columns_to_save = [
            col.copy()
            for col in self.excel_columns
            if not col.get("metric_source")
        ]
        project_state.project_excel_columns[
            project_name
        ] = base_columns_to_save
        self.show_formula_modal = False
        self.selected_column_for_formula = None
        return (True, None)

    @rx.event
    async def proceed_from_column_editor(self):
        if self.editing_column_id is not None:
            yield rx.toast(
                "Please finish editing the column name first (Save or Cancel).",
                duration=3000,
            )
            return
        if self.columns_with_formulas:
            self.formula_review_active = True
            yield rx.toast(
                "Proceeding to formula review.",
                duration=2000,
            )
        else:
            save_successful, error_message = (
                await self._save_column_structure_to_project()
            )
            if save_successful:
                self.column_structure_finalized = True
                self.formula_review_active = False
                yield rx.toast(
                    "Column structure confirmed. Proceeding to pre-load template.",
                    duration=2500,
                )
            elif error_message:
                yield rx.toast(error_message, duration=4000)

    @rx.event
    async def confirm_formulas_and_proceed_to_uploads(self):
        if self.editing_formula_column_id is not None:
            yield rx.toast(
                "Please save or cancel your current formula edit before proceeding.",
                duration=3500,
            )
            return
        save_successful, error_message = (
            await self._save_column_structure_to_project()
        )
        if save_successful:
            self.column_structure_finalized = True
            self.formula_review_active = False
            yield rx.toast(
                "Formulas and column structure confirmed. Proceeding to pre-load template.",
                duration=3000,
            )
        elif error_message:
            yield rx.toast(error_message, duration=4000)

    @rx.event
    def back_to_edit_columns_from_review(self):
        """Navigates from formula review back to the column editor."""
        self.formula_review_active = False
        self.editing_formula_column_id = None
        self.editing_formula_description_input = ""
        self.editing_formula_excel_style_input = ""
        yield rx.toast(
            "Returned to column editor.", duration=2000
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
        self.column_structure_finalized = False
        self._reset_column_state()
        self.formula_review_active = False
        self.editing_formula_column_id = None
        self._reset_file_upload_state()

    def _reset_file_upload_state(self):
        self.uploaded_file_data = {}
        self.uploaded_file_info = {}
        self.template_preview_ready = False

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
            col.copy() for col in DEFAULT_EXCEL_COLUMNS_DATA
        ]
        self.editing_column_id = None
        self.editing_column_name = ""
        self.show_formula_modal = False
        self.selected_column_for_formula = None
        self.new_column_inputs = {
            group: "" for group in COLUMN_GROUPS_ORDER
        }

    def _load_project_data_after_engines(
        self, project_state: "ProjectState"
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
            self.custom_readme_content = ""
        else:
            self.readme_choice = "customize"
        self.stakeholder_comments = (
            project_state.project_stakeholder_comments.get(
                project_name, ""
            )
        )
        self._load_metric_pass_column_data(project_state)

    def _load_metric_pass_column_data(
        self, project_state: "ProjectState"
    ):
        if not project_state.selected_project:
            self._reset_metric_and_pass_state()
            self._reset_column_state()
            self._reset_file_upload_state()
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
                col_data.copy()
                for col_data in saved_base_columns_raw
            ]
        else:
            self.excel_columns = [
                col_data.copy()
                for col_data in DEFAULT_EXCEL_COLUMNS_DATA
            ]
        project_langs = (
            project_state.project_language_pairs.get(
                project_name, []
            )
        )
        primary_source_lang_for_project: Language | None = (
            None
        )
        if project_langs:
            primary_source_lang_for_project = cast(
                Language, project_langs[0][0]
            )
        self._update_word_count_excel_formula(
            primary_source_lang_for_project
        )
        self.editing_column_id = None
        self.editing_column_name = ""
        self.new_column_inputs = {
            group: "" for group in COLUMN_GROUPS_ORDER
        }
        self._reset_file_upload_state()

    @rx.event
    def reset_state(self):
        self.current_source_language = None
        self.current_target_language = None
        self.selected_pairs_for_session = []
        self.pairs_confirmed = False
        self.available_engines = ["\uf8ffMT", "\uf8ffFM"]
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
        self._update_word_count_excel_formula(None)
        self.column_structure_finalized = False
        self.formula_review_active = False
        self.editing_formula_column_id = None
        self.editing_formula_description_input = ""
        self.editing_formula_excel_style_input = ""
        self.show_formula_wizard_modal = False
        self._reset_file_upload_state()

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
    def set_column_structure_finalized(
        self, finalized: bool
    ):
        self.column_structure_finalized = finalized
        if not finalized:
            self.formula_review_active = False
            self.editing_formula_column_id = None
            self._reset_file_upload_state()

    @rx.event
    def set_template_preview_ready(self, ready: bool):
        self.template_preview_ready = ready
        if not ready:
            pass

    @rx.event
    def show_formula_info(self, column_id: str):
        all_display_cols = self.display_excel_columns
        found_column: Optional[ExcelColumn] = None
        for col in all_display_cols:
            if col["id"] == column_id:
                found_column = col
                break
        if self.editing_formula_column_id == column_id:
            original_col_data = next(
                (
                    c
                    for c in self.excel_columns
                    if c["id"] == column_id
                ),
                None,
            )
            if original_col_data:
                found_column = original_col_data
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

    @rx.event
    def start_editing_formula(self, column_id: str):
        if (
            self.editing_formula_column_id
            and self.editing_formula_column_id != column_id
        ):
            self.cancel_formula_edits()
        col_to_edit = next(
            (
                c
                for c in self.excel_columns
                if c["id"] == column_id
            ),
            None,
        )
        if col_to_edit and (
            col_to_edit.get("formula_description")
            or col_to_edit.get("formula_excel_style")
        ):
            self.editing_formula_column_id = column_id
            self.editing_formula_description_input = (
                col_to_edit.get("formula_description", "")
            )
            self.editing_formula_excel_style_input = (
                col_to_edit.get("formula_excel_style", "")
            )
        else:
            yield rx.toast(
                "This column does not have an editable formula.",
                duration=3000,
            )

    @rx.event
    def set_editing_formula_description_input(
        self, description: str
    ):
        self.editing_formula_description_input = description

    @rx.event
    def set_editing_formula_excel_style_input(
        self, excel_style: str
    ):
        self.editing_formula_excel_style_input = excel_style

    @rx.event
    def save_formula_edits(self):
        if self.editing_formula_column_id is None:
            return
        idx = -1
        for i, col in enumerate(self.excel_columns):
            if col["id"] == self.editing_formula_column_id:
                idx = i
                break
        if idx != -1:
            temp_cols = [
                c.copy() for c in self.excel_columns
            ]
            temp_cols[idx][
                "formula_description"
            ] = (
                self.editing_formula_description_input.strip()
            )
            temp_cols[idx][
                "formula_excel_style"
            ] = (
                self.editing_formula_excel_style_input.strip()
            )
            if not temp_cols[idx].get(
                "formula_description"
            ) and (
                not temp_cols[idx].get(
                    "formula_excel_style"
                )
            ):
                temp_cols[idx]["formula_description"] = None
                temp_cols[idx]["formula_excel_style"] = None
            self.excel_columns = temp_cols
            self.editing_formula_column_id = None
            self.editing_formula_description_input = ""
            self.editing_formula_excel_style_input = ""
            yield rx.toast(
                "Formula updated.", duration=2000
            )
        else:
            yield rx.toast(
                "Error: Could not find column to update formula.",
                duration=3000,
            )
            self.editing_formula_column_id = None

    @rx.event
    def cancel_formula_edits(self):
        self.editing_formula_column_id = None
        self.editing_formula_description_input = ""
        self.editing_formula_excel_style_input = ""

    @rx.event
    def open_formula_wizard(self):
        self.show_formula_wizard_modal = True
        yield rx.toast(
            "Formula Wizard coming soon!", duration=3000
        )

    @rx.event
    def close_formula_wizard(self):
        self.show_formula_wizard_modal = False

    async def _parse_uploaded_file_content(
        self, file: rx.UploadFile
    ):
        """
        Parses file content into list of rows.
        Yields a toast on error, then yields None.
        Otherwise, yields the parsed data.
        """
        try:
            content_bytes = await file.read()
            content_str = content_bytes.decode("utf-8-sig")
        except Exception as e:
            yield rx.toast(
                f"Error reading file {file.name}: {e}",
                duration=5000,
            )
            return
        file_data: List[List[str]] = []
        if file.name.lower().endswith((".csv", ".tsv")):
            try:
                delimiter = (
                    ","
                    if file.name.lower().endswith(".csv")
                    else "\t"
                )
                csv_reader = csv.reader(
                    io.StringIO(content_str),
                    delimiter=delimiter,
                )
                for row in csv_reader:
                    file_data.append(
                        [str(cell) for cell in row]
                    )
                yield file_data
            except Exception as e:
                yield rx.toast(
                    f"Error parsing CSV/TSV {file.name}: {e}",
                    duration=5000,
                )
                return
        elif file.name.lower().endswith(".txt"):
            file_data = [
                [line] for line in content_str.splitlines()
            ]
            yield file_data
        else:
            yield rx.toast(
                f"Unsupported file type: {file.name}. Please use .txt, .csv, or .tsv.",
                duration=4000,
            )
            return

    @rx.event
    async def handle_file_upload(
        self,
        files: list[rx.UploadFile],
        column_target_id: str,
    ):
        if not files:
            return
        file = files[0]
        parsed_data_result: List[List[str]] | None = None
        async for item in self._parse_uploaded_file_content(
            file
        ):
            if isinstance(item, rx.event.EventSpec):
                yield item
            else:
                parsed_data_result = item
                break
        if parsed_data_result is not None:
            temp_uploaded_file_data = (
                self.uploaded_file_data.copy()
            )
            temp_uploaded_file_info = (
                self.uploaded_file_info.copy()
            )
            temp_uploaded_file_data[column_target_id] = (
                parsed_data_result
            )
            temp_uploaded_file_info[column_target_id] = (
                f"{file.name} ({len(parsed_data_result)} rows)"
            )
            self.uploaded_file_data = (
                temp_uploaded_file_data
            )
            self.uploaded_file_info = (
                temp_uploaded_file_info
            )
            yield rx.toast(
                f"File '{file.name}' uploaded for column ID '{column_target_id}'.",
                duration=3000,
            )

    @rx.event
    def clear_uploaded_file(self, column_target_id: str):
        temp_uploaded_file_data = (
            self.uploaded_file_data.copy()
        )
        temp_uploaded_file_info = (
            self.uploaded_file_info.copy()
        )
        if column_target_id in temp_uploaded_file_data:
            del temp_uploaded_file_data[column_target_id]
        if column_target_id in temp_uploaded_file_info:
            del temp_uploaded_file_info[column_target_id]
        self.uploaded_file_data = temp_uploaded_file_data
        self.uploaded_file_info = temp_uploaded_file_info
        yield rx.toast(
            f"Cleared uploaded file for column ID '{column_target_id}'.",
            duration=2000,
        )

    @rx.event
    def proceed_to_generate_template_preview(self):
        required_cols_ids = [
            col_spec["id"]
            for col_spec in self.template_input_columns_for_upload
        ]
        missing_files_display_names = []
        for (
            col_spec
        ) in self.template_input_columns_for_upload:
            if (
                col_spec["id"]
                not in self.uploaded_file_data
            ):
                missing_files_display_names.append(
                    col_spec["name"]
                )
        if missing_files_display_names:
            yield rx.toast(
                f"Please upload files for: {', '.join(missing_files_display_names)}.",
                duration=4000,
            )
            return
        self.template_preview_ready = True
        yield rx.toast(
            "Files processed. Generating preview...",
            duration=2000,
        )

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
    def is_proceed_from_column_editor_disabled(
        self,
    ) -> bool:
        return self.editing_column_id is not None

    @rx.var
    def is_confirm_formulas_and_proceed_disabled(
        self,
    ) -> bool:
        return self.editing_formula_column_id is not None

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
    ) -> FinalExcelDisplayType:
        grouped_display_columns: dict[
            ColumnGroup, ColumnsInGroupList
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
                    "custom_user_added": col_data.get(
                        "custom_user_added", False
                    ),
                    "removable": col_data.get(
                        "removable", False
                    ),
                    "is_first_movable_in_group": False,
                    "is_last_movable_in_group": False,
                    "allow_file_upload": col_data.get(
                        "allow_file_upload", False
                    ),
                }
                grouped_display_columns[group].append(
                    full_col_data
                )
        metric_display_cols: ColumnsInGroupList = []
        for metric_info in self.all_included_metrics:
            metric_name = metric_info["name"]
            safe_metric_name = re.sub(
                "[^a-zA-Z0-9_]", "_", metric_name.lower()
            )
            metric_col_id = f"metric_{safe_metric_name}"
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
                    custom_user_added=False,
                    removable=False,
                    is_first_movable_in_group=False,
                    is_last_movable_in_group=False,
                    allow_file_upload=False,
                )
            )
        if "Metric" not in grouped_display_columns:
            grouped_display_columns["Metric"] = []
        grouped_display_columns["Metric"].extend(
            metric_display_cols
        )
        result_with_flags: FinalExcelDisplayType = []
        for group_name_val in COLUMN_GROUPS_ORDER:
            cols_in_group_val: ColumnsInGroupList = (
                grouped_display_columns.get(
                    group_name_val, []
                )
            )
            processed_cols_in_group: ColumnsInGroupList = []
            movable_indices_in_this_displayed_group = [
                i
                for i, c_disp in enumerate(
                    cols_in_group_val
                )
                if c_disp.get("movable_within_group")
                and (not c_disp.get("metric_source"))
            ]
            first_movable_disp_idx = (
                movable_indices_in_this_displayed_group[0]
                if movable_indices_in_this_displayed_group
                else -1
            )
            last_movable_disp_idx = (
                movable_indices_in_this_displayed_group[-1]
                if movable_indices_in_this_displayed_group
                else -1
            )
            for i_disp, col_data_item_orig in enumerate(
                cols_in_group_val
            ):
                col_data_item = col_data_item_orig.copy()
                is_movable_here = col_data_item.get(
                    "movable_within_group", False
                ) and (
                    not col_data_item.get("metric_source")
                )
                if is_movable_here:
                    col_data_item[
                        "is_first_movable_in_group"
                    ] = (i_disp == first_movable_disp_idx)
                    col_data_item[
                        "is_last_movable_in_group"
                    ] = (i_disp == last_movable_disp_idx)
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
        flat_list: list[ExcelColumn] = []
        for (
            _,
            cols_in_group,
        ) in self.final_excel_columns_for_display:
            flat_list.extend(cols_in_group)
        return flat_list

    @rx.var
    def columns_with_formulas(self) -> list[ExcelColumn]:
        return [
            col
            for col in self.display_excel_columns
            if col.get("formula_description")
            or col.get("formula_excel_style")
        ]

    @rx.var
    def template_input_columns_for_upload(
        self,
    ) -> List[ExcelColumn]:
        """Returns columns from 'Input' group that allow file upload."""
        return [
            col
            for col in self.display_excel_columns
            if col["group"] == "Input"
            and col.get("allow_file_upload")
        ]

    @rx.var
    def preview_table_data(self) -> List[Dict[str, str]]:
        """Prepares data for the preview table, aligning rows from uploaded files."""
        if (
            not self.template_preview_ready
            or not self.uploaded_file_data
        ):
            return []
        num_rows = 0
        if self.uploaded_file_data:
            num_rows = max(
                (
                    len(data)
                    for data in self.uploaded_file_data.values()
                    if data
                ),
                default=0,
            )
        num_rows_to_show = min(num_rows, MAX_PREVIEW_ROWS)
        preview_rows: List[Dict[str, str]] = []
        input_column_specs = [
            col_spec
            for col_spec in self.display_excel_columns
            if col_spec["group"] == "Input"
        ]
        for i in range(num_rows_to_show):
            row_dict: Dict[str, str] = {}
            for col_spec in input_column_specs:
                col_id = col_spec["id"]
                col_name = col_spec["name"]
                data_for_col = self.uploaded_file_data.get(
                    col_id
                )
                if data_for_col and i < len(data_for_col):
                    row_dict[col_name] = (
                        data_for_col[i][0]
                        if data_for_col[i]
                        else ""
                    )
                else:
                    row_dict[col_name] = ""
            preview_rows.append(row_dict)
        return preview_rows

    @rx.var
    def preview_table_headers(self) -> List[str]:
        if not self.template_preview_ready:
            return []
        return [
            col["name"]
            for col in self.display_excel_columns
            if col["group"] == "Input"
        ]