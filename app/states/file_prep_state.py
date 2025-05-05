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
    """Manages state specific to the File Prep view, especially for MT language pairs."""

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

    @rx.event
    def set_current_source_language(self, lang: str):
        """Sets the source language for the next pair."""
        self.current_source_language = lang

    @rx.event
    def set_current_target_language(self, lang: str):
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
                self.selected_pairs_for_session = (
                    self.selected_pairs_for_session
                    + [new_pair]
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
            project_state.project_language_pairs[
                project_state.selected_project
            ] = list(self.selected_pairs_for_session)
            async with self:
                self.pairs_confirmed = True
            yield rx.toast(
                "Language pairs confirmed!", duration=3000
            )
        else:
            yield rx.toast(
                "Error: No project selected. Cannot confirm pairs.",
                duration=4000,
            )

    @rx.event
    def reset_state(self):
        """Resets the FilePrepState to its initial values."""
        self.current_source_language = None
        self.current_target_language = None
        self.selected_pairs_for_session = []
        self.pairs_confirmed = False

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
    def is_confirm_disabled(self) -> bool:
        """Checks if the 'Confirm Pairs' button should be disabled."""
        return not self.selected_pairs_for_session