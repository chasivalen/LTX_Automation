import reflex as rx
from typing import Literal, Optional

ViewType = Literal[
    "default",
    "file_prep",
    "final_file_prep",
    "update_tableau",
    "seo_automation",
]
ProjectType = Literal["MT", "LLM", "Gen AI"]
InitialChoiceType = Literal["SEO", "LTX Bench"]


class AppState(rx.State):
    """Manages the overall application state, including navigation and workflow selection."""

    initial_choice: InitialChoiceType | None = None
    project_selected: bool = False
    selected_view: ViewType = "default"
    file_prep_project_type: ProjectType | None = None

    async def _get_reset_file_prep_event(self):
        """Helper to get the reset event handler reference for FilePrepState."""
        from app.states.file_prep_state import FilePrepState

        return FilePrepState.reset_state

    @rx.event
    async def set_initial_choice(
        self, choice: InitialChoiceType
    ):
        """Sets the initial workflow choice (SEO or LTX Bench) and resets relevant states."""
        self.initial_choice = choice
        self.project_selected = False
        self.selected_view = "default"
        self.file_prep_project_type = None
        reset_event = (
            await self._get_reset_file_prep_event()
        )
        yield reset_event

    @rx.event
    async def reset_initial_choice(self):
        """Resets the initial workflow choice and all dependent states."""
        self.initial_choice = None
        self.project_selected = False
        self.selected_view = "default"
        self.file_prep_project_type = None
        reset_event = (
            await self._get_reset_file_prep_event()
        )
        yield reset_event

    @rx.event
    async def set_project_selected(self, selected: bool):
        """
        Sets the project selected status for the LTX Bench workflow.
        Resets LTX Bench views and File Prep state if deselected.
        Also resets the project choice dropdown in ProjectState if deselected.
        """
        self.project_selected = selected
        if not selected:
            self.selected_view = "default"
            self.file_prep_project_type = None
            from app.states.file_prep_state import (
                FilePrepState,
            )

            yield FilePrepState.reset_state
            from app.states.project_state import (
                ProjectState,
            )

            project_s = await self.get_state(ProjectState)
            project_s.project_choice_in_dropdown = None

    @rx.event
    async def set_selected_view(self, view: ViewType):
        """
        Sets the currently active view within the LTX Bench workflow.
        Resets File Prep state if navigating away from or into the File Prep view.
        """
        old_view = self.selected_view
        self.selected_view = view
        if (
            old_view == "file_prep"
            and view != "file_prep"
            or (
                old_view != "file_prep"
                and view == "file_prep"
            )
        ):
            self.file_prep_project_type = None
            reset_event = (
                await self._get_reset_file_prep_event()
            )
            yield reset_event

    @rx.event
    async def set_file_prep_project_type(
        self, project_type: ProjectType
    ):
        """
        Sets the project type within the File Prep view (for LTX Bench).
        Resets the file prep state (language pairs, etc.) when the type changes.
        """
        if self.file_prep_project_type != project_type:
            self.file_prep_project_type = project_type
            reset_event = (
                await self._get_reset_file_prep_event()
            )
            yield reset_event