from __future__ import annotations
import clipboard
from pathlib import Path
from subprocess import Popen
from typing import List, Callable
from enum import Enum
from dir_list import ItemType


ActionCallback_T = Callable[[Path], None]


class ActionType(Enum):
    OPEN_FILE_EXPLORER = "open_file_explorer"
    OPEN_FILE          = "open_file"
    OPEN_CMD           = "open_cmd"
    OPEN_ITEM          = "open_item"
    COPY_FULL_PATH     = "copy_full_path"

    @property
    def accepts_file_items(self) -> bool:
        return self in [ActionType.OPEN_ITEM, ActionType.OPEN_FILE, ActionType.COPY_FULL_PATH]

    @property
    def accepts_directory_items(self) -> bool:
        return self in [ActionType.OPEN_ITEM, ActionType.OPEN_FILE_EXPLORER, ActionType.COPY_FULL_PATH]


def action_callback__open_in_file_explorer(path: Path) -> None:
    Popen(f"explorer \"{path!s}\"")


def action_callback__open_cmd_at(path: Path) -> None:
    Popen(f"cmd /K cd \"{path!s}\"")


def action_callback__copy_full_path(path: Path) -> None:
    clipboard.copy(str(path))


def get_item_types(action_type: ActionType) -> List[ItemType]:
    item_types: List[ItemType] = []
    if action_type.accepts_file_items:
        item_types.append(ItemType.FILE)
    if action_type.accepts_directory_items:
        item_types.append(ItemType.DIRECTORY)
    assert len(item_types) > 0, f"Action of type {action_type} resulted in no desired items! Unsupported?"
    return item_types


def get_action(action_type: ActionType) -> ActionCallback_T:
    if action_type in [
            ActionType.OPEN_FILE_EXPLORER,
            ActionType.OPEN_FILE,
            ActionType.OPEN_ITEM,
        ]:
        return action_callback__open_in_file_explorer

    if action_type == ActionType.OPEN_CMD:
        return action_callback__open_cmd_at

    if action_type == ActionType.COPY_FULL_PATH:
        return action_callback__copy_full_path

    raise ValueError(f"Invalid action {action_type}")
