
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
import logging

if TYPE_CHECKING:
    from app.states.project_state import ProjectState

logger = logging.getLogger(__name__)

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
ReadmeChoice = Literal["default", "customize", "new"]
ColumnGroup = Literal[
    "Input",
    "Pre-Evaluation",
    "Scoring",
    "Calculated Score",
    "Freeform",
]

DEFAULT_README_HTML = ""
