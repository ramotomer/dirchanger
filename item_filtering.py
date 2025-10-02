from __future__ import annotations
import re
from pathlib import Path
from typing import List, Callable, TYPE_CHECKING
from exceptions import NoMatchFoundForSpecifier, MultipleNatchesFoundForSpecifier
if TYPE_CHECKING:
    from dir_list import DirectoryListing, ItemType

FileCondition_T = Callable[[str, str], bool]
Specifier_T = str


FILE_PATTERNS_TO_IGNORE = [
    r".*~",
    r"#.*#",
]


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


def choose_file_by_specifier(dir_list: DirectoryListing, current_path: Path, specifier: Specifier_T, desired_item_types: List[ItemType]) -> Path:
    items = dir_list.filter_types(desired_item_types)
    items = [item for item in items if not should_exclude_file(item)]

    matched_files = []
    for condition in FILE_CONDITIONS:
        matched_files = [filename for filename in items if is_a_match(condition, filename, specifier)]

        if len(matched_files) == 1:
            return current_path / Path(matched_files[0])
        continue
    raise_could_not_locate_path(matched_files, desired_item_types, current_path, specifier)
