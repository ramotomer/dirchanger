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
Specifier_T = str


FILE_PATTERNS_TO_IGNORE = [
    r".*~",
]


class ItemType(Enum):
    DIRECTORY = "directory"
    FILE      = "file"


class ActionType(Enum):
    OPEN_FILE_EXPLORER = "open_file_explorer"
    OPEN_FILE          = "open_file"
    OPEN_CMD           = "open_cmd"


class DirectoryListing(NamedTuple):
    directory: List[str]
    file:      List[str]

    def of_type(self, item_type: ItemType):
        return getattr(self, item_type.value)


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


def raise_could_not_locate_path(matched_files: List[str], searched_item_type: ItemType, searched_path: Path, specifier: Specifier_T) -> None:
    if not matched_files:
        raise NoMatchFoundForSpecifier(f"No {searched_item_type.value} in {str(searched_path)!r} matched specifier {specifier!r}!")
    raise MultipleNatchesFoundForSpecifier(f"More than one {searched_item_type.value} in {str(searched_path)!r} matched specifier {specifier!r}!\n{matched_files}")


def choose_file_by_specifier(current_path: Path, next_specifier: Specifier_T, current_item_type: ItemType) -> Path:
    items = get_directory_listing(current_path).of_type(current_item_type)

    matched_files = []
    for condition in FILE_CONDITIONS:
        matched_files = [filename for filename in items if is_a_match(condition, filename, next_specifier) and not should_exclude_file(filename)]

        if len(matched_files) == 1:
            return current_path / Path(matched_files[0])
        continue

    raise_could_not_locate_path(matched_files, current_item_type, current_path, next_specifier)


def locate_complete_path(base_path: Path, target_item_type: ItemType, specifiers: List[str]) -> Path:
    current_path = base_path

    while specifiers:
        current_item_type = target_item_type if len(specifiers) == 1 else ItemType.DIRECTORY

        current_path = choose_file_by_specifier(current_path, specifiers[0], current_item_type)
        specifiers = specifiers[1:]

    return current_path


def open_in_file_explorer(path: Path) -> None:
    Popen(f"explorer \"{path!s}\"")


def open_cmd_at(path: Path) -> None:
    Popen(f"cmd /K cd \"{path!s}\"")


if __name__ == '__main__':
    with user_friendly_errors():
        BASE_PATH = Path(r"C:\ramotomer")
        action_type = ActionType(sys.argv[1])
        user_specifiers = sys.argv[2:]

        if action_type == ActionType.OPEN_FILE_EXPLORER:
            action = open_in_file_explorer
            item_type = ItemType.DIRECTORY

        elif action_type == ActionType.OPEN_FILE:
            action = open_in_file_explorer
            item_type = ItemType.FILE

        elif action_type == ActionType.OPEN_CMD:
            action = open_cmd_at
            item_type = ItemType.DIRECTORY

        else:
            raise ValueError(f"Invalid action {action_type}")

        path = locate_complete_path(BASE_PATH, item_type, user_specifiers)
        action(path)
