import re
import sys
from enum import Enum
from os import walk
from pathlib import Path
from subprocess import Popen
from typing import List, Callable, NamedTuple

from exceptions import NoMatchFoundForSpecifier, MultipleNatchesFoundForSpecifier
from utils import user_friendly_errors

FileCondition_T = Callable[[str, str], bool]
ActionCallback_T = Callable[[Path], None]
Specifier_T = str

BASE_PATH = Path(r"C:\ramotomer")
FILE_PATTERNS_TO_IGNORE = [
    r".*~",
    r"#.*#",
]


class ItemType(Enum):
    DIRECTORY = "directory"
    FILE      = "file"


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


class DirectoryListing(NamedTuple):
    directory: List[str]
    file:      List[str]

    def filter_types(self, item_types: List[ItemType]):
        items = []
        assert len(item_types) == len(set(item_types)), f"Duplicates not expected in: {item_types}"
        for item_type in item_types:
            if item_type == ItemType.FILE:
                items.extend(self.file)
                continue
            if item_type == ItemType.DIRECTORY:
                items.extend(self.directory)
                continue
            raise ValueError(f"Unsupported item type {item_type}")
        return items


def file_condition__prefix(filename: str, specifier: str) -> bool:
    return filename.startswith(specifier)


def file_condition__contains(filename: str, specifier: str) -> bool:
    return specifier in filename


def file_condition__fuzzy_contains(filename: str, specifier: str) -> bool:
    """
    Find if the filename could be turned into the specifier by removing characters.
    Case-insensitive.

    Examples:
        ("hello", 'h') -> True
        ("hEllo", 'ell') -> True
        ("hello", 'ho') -> True
        ("hello", 'bel') -> False
        ("hello world", 'hw') -> True
        ("hello world", 'helwo') -> True
        ("hello world", 'allo') -> False
        ("", 'a') -> False
        ("a", '') -> True
    """
    remaining_filename = filename.lower()
    remaining_specifier = specifier.lower()

    while remaining_specifier:
        current_char = remaining_specifier[0]
        if current_char not in remaining_filename:
            return False

        remaining_filename = remaining_filename[remaining_specifier.index(remaining_specifier[0]) + 1:]
        remaining_specifier = remaining_specifier[1:]

    return True


def is_a_match(matcher: FileCondition_T, filename: str, specifier: str) -> bool:
    return matcher(filename, specifier)


def should_exclude_file(filename: str) -> bool:
    for pattern in FILE_PATTERNS_TO_IGNORE:
        match = re.match(pattern, filename)
        if match is not None and match.group(0) == filename:
            return True
    return False


def get_directory_listing(path: Path) -> DirectoryListing:
    recursive_dir_generator = walk(path)
    path_, directories, files = next(recursive_dir_generator)
    return DirectoryListing(directories, files)


FILE_CONDITIONS: List[FileCondition_T] = [
    file_condition__prefix,
    file_condition__contains,
    file_condition__fuzzy_contains,
]


def raise_could_not_locate_path(matched_files: List[str], searched_item_types: List[ItemType], searched_path: Path, specifier: Specifier_T) -> None:
    types_str = ','.join([item_type.value for item_type in searched_item_types[:-1]])
    types_str += ' or '.join(([types_str] if types_str else []) + [searched_item_types[-1].value])

    if not matched_files:
        raise NoMatchFoundForSpecifier(f"No {types_str} in {str(searched_path)!r} matched specifier {specifier!r}!")
    raise MultipleNatchesFoundForSpecifier(f"More than one {types_str} in {str(searched_path)!r} matched specifier {specifier!r}!\n{matched_files}")


def choose_file_by_specifier(current_path: Path, next_specifier: Specifier_T, desired_item_types: List[ItemType]) -> Path:
    items = get_directory_listing(current_path).filter_types(desired_item_types)

    matched_files = []
    for condition in FILE_CONDITIONS:
        matched_files = [filename for filename in items if is_a_match(condition, filename, next_specifier) and not should_exclude_file(filename)]

        if len(matched_files) == 1:
            return current_path / Path(matched_files[0])
        continue
    raise_could_not_locate_path(matched_files, desired_item_types, current_path, next_specifier)


def locate_complete_path(base_path: Path, target_item_types: List[ItemType], specifiers: List[str]) -> Path:
    current_path = base_path

    while specifiers:
        is_last_iteration = (len(specifiers) == 1)
        current_item_type = target_item_types if is_last_iteration else [ItemType.DIRECTORY]

        current_path = choose_file_by_specifier(current_path, specifiers[0], current_item_type)
        specifiers = specifiers[1:]
    return current_path


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
