import reflex as rx
from typing import Optional, Literal

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
DEFAULT_README_PLACEHOLDER = "\n**Instructions for MT Output Evaluation**\n\nThank you for helping evaluate the machine translation output. Your feedback is crucial for improving our systems.\n\n**Task:**\n\n1.  Read the source text segment carefully.\n2.  Read the corresponding machine-translated text segment.\n3.  Evaluate the translation based on the following criteria:\n    *   **Fluency:** Is the translated text grammatically correct and natural-sounding in the target language?\n    *   **Adequacy:** Does the translation accurately convey the meaning of the source text?\n    *   **Usability:** Could this translation be used as-is for its intended purpose (e.g., understanding information, communication)?\n4.  Assign scores or provide comments based on the project-specific guidelines.\n5.  Identify any critical errors (e.g., mistranslations, omissions, offensive content).\n\n**Please focus on:**\n*   Meaning and accuracy.\n*   Naturalness and flow.\n*   Typos or grammatical mistakes.\n\n**Do not focus on:**\n*   Minor stylistic preferences unless they significantly impact meaning or usability.\n\nIf you encounter any issues or have questions, please contact the project manager.\n"


class FilePrepState(rx.State):
    """Manages state specific to the File Prep view, including MT language pairs, engines, and Read Me instructions."""

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
    custom_readme_content: str = ""
    readme_expanded: bool = False
    readme_confirmed: bool = False
    default_readme: str = DEFAULT_README_PLACEHOLDER

    @rx.event
    def set_current_source_language(self, lang: Language):
        """Sets the source language for the next pair."""
        self.current_source_language = lang

    @rx.event
    def set_current_target_language(self, lang: Language):
        """Sets the target language for the next pair."""
        self.current_target_language = lang

    @rx.event
    def add_language_pair(self):
        """Adds the currently selected language pair to the session list."""
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
        """Removes a language pair from the session list."""
        self.selected_pairs_for_session = [
            pair
            for pair in self.selected_pairs_for_session
            if pair != pair_to_remove
        ]

    @rx.event
    async def confirm_language_pairs(self):
        """Confirms the selected language pairs and saves them to the project state."""
        from app.states.project_state import ProjectState

        if not self.selected_pairs_for_session:
            yield rx.toast(
                "Please add at least one language pair.",
                duration=3000,
            )
            return
        project_state = await self.get_state(ProjectState)
        if project_state.selected_project:
            if (
                project_state.selected_project
                not in project_state.project_language_pairs
            ):
                project_state.project_language_pairs[
                    project_state.selected_project
                ] = []
            project_state.project_language_pairs[
                project_state.selected_project
            ] = list(self.selected_pairs_for_session)
            self.selected_engines = list(
                project_state.project_mt_engines.get(
                    project_state.selected_project, []
                )
            )
            self.pairs_confirmed = True
            self.engines_confirmed = False
            self.readme_confirmed = False
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
        """Updates the input field for adding a new engine."""
        self.new_engine_name = name

    @rx.event
    def toggle_engine(self, engine_name: str):
        """Adds or removes a predefined engine from the selected list."""
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
        """Adds a custom engine name from the input field."""
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
        """Removes an engine from the selected list (used for custom/selected ones)."""
        self.selected_engines = [
            eng
            for eng in self.selected_engines
            if eng != engine_name
        ]

    @rx.event
    async def confirm_engines(self):
        """Confirms the selected MT engines, saves them, and prepares for ReadMe step."""
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
            saved_readme = (
                project_state.project_readme_content.get(
                    project_state.selected_project, None
                )
            )
            if (
                saved_readme is None
                or saved_readme == self.default_readme
            ):
                self.readme_choice = "default"
                self.custom_readme_content = (
                    self.default_readme
                )
            else:
                self.custom_readme_content = saved_readme
                self.readme_choice = (
                    "new"
                    if not saved_readme.strip()
                    else "customize"
                )
            self.engines_confirmed = True
            self.readme_confirmed = False
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
        """Sets the user's choice for the Read Me instructions."""
        self.readme_choice = choice
        if choice == "default":
            self.custom_readme_content = self.default_readme
        elif choice == "customize":
            if not self.custom_readme_content.strip():
                self.custom_readme_content = (
                    self.default_readme
                )
        elif choice == "new":
            self.custom_readme_content = ""

    @rx.event
    def set_custom_readme_content(self, content: str):
        """Updates the content of the custom Read Me."""
        self.custom_readme_content = content

    @rx.event
    def toggle_readme_expanded(self):
        """Toggles the visibility of the default Read Me content."""
        self.readme_expanded = not self.readme_expanded

    @rx.event
    async def confirm_readme(self):
        """Confirms the Read Me choice and content, saves to project state."""
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
        yield rx.toast(
            "Read Me Instructions Confirmed!", duration=3000
        )

    @rx.event
    def reset_state(self):
        """Resets the FilePrepState to its initial values."""
        self.current_source_language = None
        self.current_target_language = None
        self.selected_pairs_for_session = []
        self.pairs_confirmed = False
        self.selected_engines = []
        self.new_engine_name = ""
        self.engines_confirmed = False
        self.readme_choice = None
        self.custom_readme_content = ""
        self.readme_expanded = False
        self.readme_confirmed = False

    @rx.event
    def set_pairs_confirmed(self, confirmed: bool):
        """Allows editing pairs again by setting confirmed to False."""
        self.pairs_confirmed = confirmed
        if not confirmed:
            self.engines_confirmed = False
            self.readme_confirmed = False
            self.readme_choice = None
            self.custom_readme_content = ""

    @rx.event
    def set_engines_confirmed(self, confirmed: bool):
        """Allows editing engines again by setting confirmed to False."""
        self.engines_confirmed = confirmed
        if not confirmed:
            self.readme_confirmed = False
            self.readme_choice = None
            self.custom_readme_content = ""

    @rx.event
    def set_readme_confirmed(self, confirmed: bool):
        """Allows editing ReadMe again."""
        self.readme_confirmed = confirmed

    @rx.var
    def is_add_pair_disabled(self) -> bool:
        """Checks if the 'Add Pair' button should be disabled."""
        return (
            self.current_source_language is None
            or self.current_target_language is None
            or self.current_source_language
            == self.current_target_language
        )

    @rx.var
    def is_confirm_pairs_disabled(self) -> bool:
        """Checks if the 'Confirm Pairs' button should be disabled."""
        return not self.selected_pairs_for_session

    @rx.var
    def is_add_engine_disabled(self) -> bool:
        """Checks if the 'Add Engine' button should be disabled."""
        return self.new_engine_name.strip() == ""

    @rx.var
    def is_confirm_engines_disabled(self) -> bool:
        """Checks if the 'Confirm Engines' button should be disabled."""
        return not self.selected_engines

    @rx.var
    def is_confirm_readme_disabled(self) -> bool:
        """Checks if the 'Confirm ReadMe' button should be disabled."""
        if self.readme_choice is None:
            return True
        if self.readme_choice in ["customize", "new"] and (
            not self.custom_readme_content.strip()
        ):
            return True
        return False

    @rx.var
    def final_readme_content(self) -> str:
        """Determines the final Read Me content based on the user's choice."""
        if self.readme_choice == "default":
            return self.default_readme
        elif self.readme_choice in ["customize", "new"]:
            return self.custom_readme_content
        return ""