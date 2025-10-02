from __future__ import annotations
from enum import Enum
from os import walk
from pathlib import Path
from typing import List, NamedTuple


class ItemType(Enum):
    DIRECTORY = "directory"
    FILE      = "file"


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


def get_directory_listing(path: Path) -> DirectoryListing:
    recursive_dir_generator = walk(path)
    path_, directories, files = next(recursive_dir_generator)
    return DirectoryListing(directories, files)
