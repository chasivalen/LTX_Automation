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


class FilePrepState(rx.State):
    """Manages state specific to the File Prep view, including MT language pairs and engines."""

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
        """Confirms the selected MT engines and saves them to the project state."""
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
            self.engines_confirmed = True
            yield rx.toast(
                "MT Engines confirmed!", duration=3000
            )
        else:
            yield rx.toast(
                "Error: No project selected. Cannot confirm engines.",
                duration=4000,
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

    @rx.event
    def set_pairs_confirmed(self, confirmed: bool):
        """Allows editing pairs again by setting confirmed to False."""
        self.pairs_confirmed = confirmed
        if not confirmed:
            self.engines_confirmed = False

    @rx.event
    def set_engines_confirmed(self, confirmed: bool):
        """Allows editing engines again by setting confirmed to False."""
        self.engines_confirmed = confirmed

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