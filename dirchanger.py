from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Callable

from actions import ActionType, get_action, get_item_types
from dir_list import get_directory_listing, ItemType
from item_filtering import choose_file_by_specifier
from utils import user_friendly_errors

FileCondition_T = Callable[[str, str], bool]
ActionCallback_T = Callable[[Path], None]


BASE_PATH = Path(r"C:\ramotomer")


def locate_complete_path(base_path: Path, target_item_types: List[ItemType], specifiers: List[str]) -> Path:
    current_path = base_path

    while specifiers:
        is_last_iteration = (len(specifiers) == 1)
        current_item_type = target_item_types if is_last_iteration else [ItemType.DIRECTORY]

        dir_list = get_directory_listing(current_path)
        current_path = choose_file_by_specifier(dir_list, current_path, specifiers[0], current_item_type)
        specifiers = specifiers[1:]
    return current_path


def main():
    action_type = ActionType(sys.argv[1])
    user_specifiers = sys.argv[2:]

    action = get_action(action_type)
    item_types = get_item_types(action_type)

    path = locate_complete_path(BASE_PATH, item_types, user_specifiers)
    action(path)


if __name__ == '__main__':
    with user_friendly_errors():
        main()
