import reflex as rx
from typing import Optional, Literal, TypedDict

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
            self._load_project_text_and_metrics(
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
    def set_readme_choice(self, choice: ReadmeChoice):
        self.readme_choice = choice
        if choice == "default":
            self.custom_readme_content = self.default_readme
        elif choice == "customize":
            project_state = self.get_state(ProjectState)
            saved_readme = (
                project_state.project_readme_content.get(
                    project_state.selected_project,
                    self.default_readme,
                )
                if project_state
                and project_state.selected_project
                else self.default_readme
            )
            self.custom_readme_content = (
                saved_readme
                if saved_readme != self.default_readme
                else self.default_readme
            )
        elif choice == "new":
            project_state = self.get_state(ProjectState)
            saved_readme = (
                project_state.project_readme_content.get(
                    project_state.selected_project,
                    self.default_readme,
                )
                if project_state
                and project_state.selected_project
                else self.default_readme
            )
            self.custom_readme_content = (
                ""
                if saved_readme == self.default_readme
                else saved_readme
            )

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
        yield rx.toast(
            "Stakeholder Perspective Confirmed! Define Metrics next.",
            duration=3000,
        )

    @rx.event
    def toggle_evergreen_metric(self, metric_name: str):
        if metric_name in self.included_evergreen_metrics:
            self.included_evergreen_metrics = [
                m
                for m in self.included_evergreen_metrics
                if m != metric_name
            ]
            if metric_name in self.metric_weights:
                del self.metric_weights[metric_name]
        else:
            self.included_evergreen_metrics.append(
                metric_name
            )
            self.metric_weights[metric_name] = 5

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
        if (
            any(
                (
                    metric["name"] == name
                    for metric in self.custom_metrics
                )
            )
            or name in self.evergreen_metrics_definitions
        ):
            yield rx.toast(
                f"A metric with the name '{name}' already exists.",
                duration=3000,
            )
            return
        self.custom_metrics.append(
            CustomMetric(name=name, definition=definition)
        )
        self.metric_weights[name] = 5
        self.new_custom_metric_name = ""
        self.new_custom_metric_definition = ""

    @rx.event
    def remove_custom_metric(self, metric_name: str):
        self.custom_metrics = [
            m
            for m in self.custom_metrics
            if m["name"] != metric_name
        ]
        if metric_name in self.metric_weights:
            del self.metric_weights[metric_name]

    @rx.event
    def set_metric_weight(
        self, metric_name: str, weight_str: str
    ):
        try:
            weight = int(weight_str)
            if 1 <= weight <= 10:
                self.metric_weights[metric_name] = weight
            else:
                yield rx.toast(
                    f"Weight for '{metric_name}' must be between 1 and 10.",
                    duration=3000,
                )
        except ValueError:
            yield rx.toast(
                f"Invalid weight for '{metric_name}'. Please enter a number.",
                duration=3000,
            )

    @rx.event
    async def confirm_metrics(self):
        from app.states.project_state import ProjectState

        if not self.all_included_metrics:
            yield rx.toast(
                "Please include at least one metric.",
                duration=3000,
            )
            return
        for metric in self.all_included_metrics:
            if (
                metric["name"] not in self.metric_weights
                or not 1
                <= self.metric_weights[metric["name"]]
                <= 10
            ):
                yield rx.toast(
                    f"Invalid or missing weight for metric: {metric['name']}. Weight must be 1-10.",
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
        project_state.project_included_metrics[
            project_state.selected_project
        ] = {
            "evergreen": list(
                self.included_evergreen_metrics
            ),
            "custom": list(self.custom_metrics),
        }
        project_state.project_metric_weights[
            project_state.selected_project
        ] = dict(self.metric_weights)
        self.metrics_confirmed = True
        yield rx.toast(
            "Metrics and Weights Confirmed! Configuration complete.",
            duration=3000,
        )

    def _reset_downstream_of_pairs(self):
        """Resets state from Engines onwards."""
        self.engines_confirmed = False
        self.readme_confirmed = False
        self.stakeholder_confirmed = False
        self.metrics_confirmed = False
        self.readme_choice = None
        self.custom_readme_content = self.default_readme
        self.stakeholder_comments = ""
        self.selected_engines = []
        self.new_engine_name = ""
        self._reset_metric_state()

    def _reset_downstream_of_engines(self):
        """Resets state from ReadMe onwards."""
        self.readme_confirmed = False
        self.stakeholder_confirmed = False
        self.metrics_confirmed = False
        self.readme_choice = None
        self.stakeholder_comments = ""
        self._reset_metric_state()

    def _reset_downstream_of_readme(self):
        """Resets state from Stakeholder onwards."""
        self.stakeholder_confirmed = False
        self.metrics_confirmed = False
        self._reset_metric_state()

    def _reset_downstream_of_stakeholder(self):
        """Resets state from Metrics onwards."""
        self.metrics_confirmed = False

    def _reset_metric_state(self):
        """Resets only the metric-related state to defaults."""
        self.included_evergreen_metrics = list(
            EVERGREEN_METRICS.keys()
        )
        self.custom_metrics = []
        self.new_custom_metric_name = ""
        self.new_custom_metric_definition = ""
        self.metric_weights = {
            metric: 5 for metric in EVERGREEN_METRICS
        }

    def _load_project_text_and_metrics(self, project_state):
        """Loads ReadMe, Stakeholder data, and Metric settings from ProjectState."""
        if not project_state.selected_project:
            self._reset_metric_state()
            self.custom_readme_content = self.default_readme
            self.stakeholder_comments = ""
            self.readme_choice = None
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
            self.readme_choice = "customize"
        self.stakeholder_comments = (
            project_state.project_stakeholder_comments.get(
                project_name, ""
            )
        )
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
        if saved_metrics_config and saved_weights:
            self.included_evergreen_metrics = list(
                saved_metrics_config.get(
                    "evergreen", EVERGREEN_METRICS.keys()
                )
            )
            self.custom_metrics = list(
                saved_metrics_config.get("custom", [])
            )
            self.metric_weights = dict(saved_weights)
            all_included_names = (
                self.included_evergreen_metrics
                + [cm["name"] for cm in self.custom_metrics]
            )
            for name in all_included_names:
                if name not in self.metric_weights:
                    self.metric_weights[name] = 5
        else:
            self._reset_metric_state()

    @rx.event
    def reset_state(self):
        """Resets the entire FilePrepState."""
        self.current_source_language = None
        self.current_target_language = None
        self.selected_pairs_for_session = []
        self.pairs_confirmed = False
        self._reset_downstream_of_pairs()

    @rx.event
    def set_pairs_confirmed(self, confirmed: bool):
        """Allows editing pairs again, resets downstream state."""
        self.pairs_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_pairs()

    @rx.event
    def set_engines_confirmed(self, confirmed: bool):
        """Allows editing engines again, resets downstream state."""
        self.engines_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_engines()

    @rx.event
    def set_readme_confirmed(self, confirmed: bool):
        """Allows editing ReadMe again, resets downstream state."""
        self.readme_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_readme()

    @rx.event
    def set_stakeholder_confirmed(self, confirmed: bool):
        """Allows editing Stakeholder comments again, resets downstream state."""
        self.stakeholder_confirmed = confirmed
        if not confirmed:
            self._reset_downstream_of_stakeholder()

    @rx.event
    def set_metrics_confirmed(self, confirmed: bool):
        """Allows editing Metrics again."""
        self.metrics_confirmed = confirmed

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
            if metric["name"] not in self.metric_weights:
                return True
        return False

    @rx.var
    def final_readme_content(self) -> str:
        if self.readme_choice == "default":
            return self.default_readme
        elif self.readme_choice in ["customize", "new"]:
            return self.custom_readme_content
        return self.default_readme

    @rx.var
    def all_included_metrics(self) -> list[dict[str, str]]:
        """Returns a list of all included metrics (evergreen + custom) with their definitions."""
        metrics = []
        for name in self.included_evergreen_metrics:
            metrics.append(
                {
                    "name": name,
                    "definition": self.evergreen_metrics_definitions.get(
                        name, "Definition not found."
                    ),
                }
            )
        for custom_metric in self.custom_metrics:
            metrics.append(
                {
                    "name": custom_metric["name"],
                    "definition": custom_metric[
                        "definition"
                    ],
                }
            )
        return metrics