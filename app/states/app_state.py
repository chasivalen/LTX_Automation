import reflex as rx


class AppState(rx.State):
    """Manages the overall application state."""

    project_selected: bool = False