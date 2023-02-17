import os

FOLDER = 0
FILE = 1


class DirectoryEntry:
    def __init__(self, type: int, entry_name: str):
        self._type = type
        self._entry_name = entry_name

    def get_type(self):
        """Returns the type of the entry that this object represents"""
        return self._type

    def get_entry_name(self):
        """Returns the name of the entry that this object represents"""
        return self._entry_name


class DirectoryEntryFile(DirectoryEntry):
    def __init__(self, entry_name: str, questions_available: bool = False):
        super().__init__(type=FILE, entry_name=entry_name)
        self.questions_available = questions_available

    def set_questions_available(self, status: bool):
        """Sets the availability of the questions to a new status"""
        self.questions_available = status


class DirectoryEntryFolder(DirectoryEntry):
    def __init__(self, entry_name: str, path: str):
        super().__init__(type=FOLDER, entry_name=entry_name)
        self._path: str = path
        self._immediate_decks: dict[str, DirectoryEntryFile]
        self._sub_folders: dict[str, DirectoryEntryFolder]
        self._immediate_decks, self._sub_folders = get_entries_from_path(self._path)

    def get_immediate_decks(self) -> dict[str, DirectoryEntryFile]:
        """Returns first levels decks"""
        return self._immediate_decks

    def get_immediate_folders(self) -> dict[str, "DirectoryEntryFolder"]:
        """Returns first levels folders"""
        return self._sub_folders

    def get_path(self):
        """Returns the path of the folder that this object represents"""
        return self._path


def get_decks_structure_from_disk(root_folder_path: str) -> DirectoryEntryFolder:
    """Retrieve the decks structure

    Parameters
    ----------
    root_folder_path : str
        Path to the root folder of the decks structure

    Returns
    -------
    DirectoryEntryFolder
        Rappresentation of the directory

    """
    deck_structure = DirectoryEntryFolder(entry_name="root", path=root_folder_path)
    return deck_structure


def get_entries_from_path(
    path: str,
) -> tuple[dict[str, DirectoryEntryFile], dict[str, DirectoryEntryFolder]]:
    """Returns the entries of the provided path.

    It is a function used to retrieve the content of a folder containing .pdf and .txt files

    Parameters
    ----------
    path : str
        Path of folder containing the decks we want to extract

    Returns
    -------
    tuple[dict[str, DirectoryEntryFile], dict[str, DirectoryEntryFile]]
    Two dictionaries are returned inside a tuple and for both of them the keys are the filenames. The mapped items are the entries contained in the folder. In the first element there are DirectoryEntryFiles and in the second there are DirectoryEntryFolders.

    """
    immediate_decks: dict[str, DirectoryEntryFile] = dict({})
    immediate_folder: dict[str, DirectoryEntryFolder] = dict({})
    with os.scandir(path) as entries:
        files_processed: set[str] = set({})
        for entry in entries:
            if not entry.name.startswith(".") and entry.is_file():
                process_entry_file(immediate_decks, files_processed, entry.name)
            elif not entry.name.startswith(".") and entry.is_dir():
                process_entry_folder(immediate_folder, path, entry.name)
    return (immediate_decks, immediate_folder)


def process_entry_file(
    immediate_decks: dict[str, DirectoryEntryFile],
    files_processed: set[str],
    entry_name: str,
) -> None:
    """Process a file of a directory.

    It adds the DirectoryEntryFile if the filename, excluding the extension, was not encountered before. If the corrisponding .txt file is met then questions_available of that entry is set to True.

    Parameters
    ----------
    decks : dict[str, DirectoryEntryFile]
        The keys are the filenames, and the items are DirectoryEntryFiles contained in the path
    files_processed : set[str]
        Set containing the filenames already processed from the current folder
    entry_name : str
        Name of the entry that is going to be processed by the function

    Returns
    -------
    None


    """
    filename, file_extension = os.path.splitext(entry_name)

    match file_extension:
        case ".pdf":
            if filename not in files_processed:
                immediate_decks[filename] = DirectoryEntryFile(
                    entry_name=entry_name,
                    questions_available=False,
                )
                files_processed.add(filename)
        case ".txt":
            if filename not in files_processed:
                immediate_decks[filename] = DirectoryEntryFile(
                    entry_name=entry_name,
                    questions_available=True,
                )
                files_processed.add(filename)
            else:
                immediate_decks[filename].set_questions_available(status=True)

        case _:
            print("File {filename} not processed".format(filename=entry_name))


def process_entry_folder(
    immediate_folders: dict[str, DirectoryEntryFolder],
    path_to_folder: str,
    entry_name: str,
) -> None:
    """Process an inner directory.

    Adds the DirectoryEntryFolder to the dictionary containing the folders passed as a parameter. The creation of the sub-DirectoryEntryFolder goes on recursively.

    Parameters
    ----------
    immediate_folders : dict[str, DirectoryEntryFolder]
        The keys are directory names, and the items are the DirectoryEntryFolder contained in the path
    path_to_folder : str
        Path to the current entry
    entry_name : str
        Name of the entry that is going to be processed by the function

    Returns
    -------
    None


    """
    child_folder = os.path.join(path_to_folder, entry_name)
    immediate_folders[entry_name] = DirectoryEntryFolder(
        entry_name=entry_name, path=child_folder
    )
