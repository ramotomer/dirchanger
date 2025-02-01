import sys
from os import walk
from pathlib import Path
from subprocess import Popen
from typing import List, Callable

from exceptions import NoMatchFoundForSpecifier, MultipleNatchesFoundForSpecifier
from utils import run_as_user_shortcut, rpartial

FileCondition_T = Callable[[str, str], bool]


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


def get_subdirectories(path: Path) -> List[str]:
    recursive_dir_generator = walk(path)
    path_, directories, files = next(recursive_dir_generator)
    return directories


def locate_path(base_path: Path, specifiers: List[str]) -> Path:
    if not specifiers:
        return base_path

    current_specifier, *leftover_specifiers = specifiers
    files = get_subdirectories(base_path)

    conditions: List[FileCondition_T] = [
        file_condition__prefix,
        file_condition__contains,
        file_condition__fuzzy_contains,
    ]

    matched = []
    for condition in conditions:
        matched = [filename for filename in files if is_a_match(condition, filename, current_specifier)]
        if len(matched) == 1:
            return locate_path((base_path / Path(matched[0])), leftover_specifiers)
        continue

    if not matched:
        raise NoMatchFoundForSpecifier(f"None of the files in {str(base_path)!r} matched specifier {current_specifier!r}!")
    raise MultipleNatchesFoundForSpecifier(f"Too many files in {str(base_path)!r} matched specifier {current_specifier!r}!\n{matched}")


def open_path(path: Path) -> None:
    Popen(f"explorer \"{path!s}\"")


if __name__ == '__main__':
    BASE_PATH = Path(r"C:\ramotomer")
    user_specifiers = sys.argv[1:]

    run_as_user_shortcut(rpartial(
        open_path,
        rpartial(locate_path, BASE_PATH, user_specifiers)
    ))
