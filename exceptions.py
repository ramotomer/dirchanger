class DirChangerError(Exception):
    pass


class CouldNotLocatePath(DirChangerError):
    pass


class NoMatchFoundForSpecifier(CouldNotLocatePath):
    pass


class MultipleNatchesFoundForSpecifier(CouldNotLocatePath):
    pass
