from __future__ import annotations

from dataclasses import dataclass

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


@dataclass
class PathAction:
    type:                ActionType
    callback:            ActionCallback_T
    accepted_item_types: List[ItemType]


def action_callback__open_in_file_explorer(path: Path) -> None:
    Popen(f"explorer \"{path!s}\"")


def action_callback__open_cmd_at(path: Path) -> None:
    Popen(f"cmd /K cd \"{path!s}\"")


def action_callback__copy_full_path(path: Path) -> None:
    clipboard.copy(str(path))


PATH_ACTIONS = [
    PathAction(ActionType.OPEN_FILE_EXPLORER, action_callback__open_in_file_explorer,  [ItemType.DIRECTORY]               ),
    PathAction(ActionType.OPEN_FILE,          action_callback__open_in_file_explorer,  [ItemType.FILE]                    ),
    PathAction(ActionType.OPEN_CMD,           action_callback__open_cmd_at,            [ItemType.DIRECTORY]               ),
    PathAction(ActionType.OPEN_ITEM,          action_callback__open_in_file_explorer,  [ItemType.FILE, ItemType.DIRECTORY]),
    PathAction(ActionType.COPY_FULL_PATH,     action_callback__copy_full_path,         [ItemType.FILE, ItemType.DIRECTORY]),
]


def get_action(action_str: str) -> PathAction:
    results = [action for action in PATH_ACTIONS if action.type.value == action_str]
    assert len(results) > 0,  f"Unknown action type {action_str!r}"
    assert len(results) <= 1, f"Too many matching actions, this is impossible, {results=}"
    return results[0]
