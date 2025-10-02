from __future__ import annotations
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

    @property
    def should_open_file(self) -> bool:
        return self in [ActionType.OPEN_ITEM, ActionType.OPEN_FILE]

    @property
    def should_open_dir(self) -> bool:
        return self in [ActionType.OPEN_ITEM, ActionType.OPEN_FILE_EXPLORER]


def action_callback__open_in_file_explorer(path: Path) -> None:
    Popen(f"explorer \"{path!s}\"")


def action_callback__open_cmd_at(path: Path) -> None:
    Popen(f"cmd /K cd \"{path!s}\"")


def get_item_types(action_type: ActionType) -> List[ItemType]:
    if action_type == ActionType.OPEN_FILE_EXPLORER:
        return [ItemType.DIRECTORY]
    if action_type == ActionType.OPEN_FILE:
        return [ItemType.FILE]
    if action_type == ActionType.OPEN_CMD:
        return [ItemType.DIRECTORY]
    if action_type == ActionType.OPEN_ITEM:
        return [ItemType.DIRECTORY, ItemType.FILE]
    raise ValueError(f"Unsupported action of type {action_type}")


def get_action(action_type: ActionType) -> ActionCallback_T:
    if action_type in [
            ActionType.OPEN_FILE_EXPLORER,
            ActionType.OPEN_FILE,
            ActionType.OPEN_ITEM,
        ]:
        return action_callback__open_in_file_explorer

    if action_type == ActionType.OPEN_CMD:
        return action_callback__open_cmd_at

    raise ValueError(f"Invalid action {action_type}")
