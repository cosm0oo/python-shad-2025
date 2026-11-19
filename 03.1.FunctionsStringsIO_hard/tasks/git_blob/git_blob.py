from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import zlib


class BlobType(Enum):
    """Helper class for holding blob type"""
    COMMIT = b'commit'
    TREE = b'tree'
    DATA = b'blob'

    @classmethod
    def from_bytes(cls, type_: bytes) -> 'BlobType':
        for member in cls:
            if member.value == type_:
                return member
        assert False, f'Unknown type {type_.decode("utf-8")}'


@dataclass
class Blob:
    """Any blob holder"""
    type_: BlobType
    content: bytes


@dataclass
class Commit:
    """Commit blob holder"""
    tree_hash: str
    parents: list[str]
    author: str
    committer: str
    message: str


@dataclass
class Tree:
    """Tree blob holder"""
    children: dict[str, Blob]


def read_blob(path: Path) -> Blob:
    """
    Read blob-file, decompress and parse header
    :param path: path to blob-file
    :return: blob-file type and content
    """
    with open(path, 'rb') as f:
        data = zlib.decompress(f.read())

    null_pos = data.index(b'\x00')
    header = data[:null_pos]
    content = data[null_pos + 1:]

    type_str, _ = header.split(b' ', 1)
    blob_type = BlobType.from_bytes(type_str)

    return Blob(type_=blob_type, content=content)


def traverse_objects(obj_dir: Path) -> dict[str, Blob]:
    """
    Traverse directory with git objects and load them
    :param obj_dir: path to git "objects" directory
    :return: mapping from hash to blob with every blob found
    """
    blobs = {}

    for dir_path in obj_dir.iterdir():
        if not dir_path.is_dir():
            continue

        prefix = dir_path.name
        for file_path in dir_path.iterdir():
            hash_str = prefix + file_path.name
            blobs[hash_str] = read_blob(file_path)

    return blobs


def parse_commit(blob: Blob) -> Commit:
    """
    Parse commit blob
    :param blob: blob with commit type
    :return: parsed commit
    """
    lines = blob.content.decode('utf-8').split('\n')

    tree_hash = ''
    parents = []
    author = ''
    committer = ''

    i = 0
    for i, line in enumerate(lines):
        if line == '':
            break

        key, value = line.split(' ', 1)
        if key == 'tree':
            tree_hash = value
        elif key == 'parent':
            parents.append(value)
        elif key == 'author':
            author = value
        elif key == 'committer':
            committer = value

    message = '\n'.join(lines[i + 1:]).rstrip('\n')

    return Commit(tree_hash=tree_hash, parents=parents, author=author, committer=committer, message=message)


def parse_tree(blobs: dict[str, Blob], tree_root: Blob, ignore_missing: bool = True) -> Tree:
    """
    Parse tree blob
    :param blobs: all read blobs (by traverse_objects)
    :param tree_root: tree blob to parse
    :param ignore_missing: ignore blobs which were not found in objects directory
    :return: tree contains children blobs (or only part of them found in objects directory)
    NB. Children blobs are not being parsed according to type.
        Also nested tree blobs are not being traversed.
    """
    children = {}
    content = tree_root.content
    pos = 0

    while pos < len(content):
        null_pos = content.index(b'\x00', pos)
        header = content[pos:null_pos]
        _, name = header.split(b' ', 1)

        hash_bytes = content[null_pos + 1:null_pos + 21]
        hash_str = hash_bytes.hex()

        if hash_str in blobs:
            children[name.decode('utf-8')] = blobs[hash_str]

        pos = null_pos + 21

    return Tree(children=children)


def find_initial_commit(blobs: dict[str, Blob]) -> Commit:
    """
    Iterate over blobs and find initial commit (without parents)
    :param blobs: blobs read from objects dir
    :return: initial commit
    """
    for blob in blobs.values():
        if blob.type_ == BlobType.COMMIT:
            commit = parse_commit(blob)
            if not commit.parents:
                return commit


def search_file(blobs: dict[str, Blob], tree_root: Blob, filename: str) -> Blob:
    """
    Traverse tree blob (can have nested tree blobs) and find requested file,
    check if file was not found (assertion).
    :param blobs: blobs read from objects dir
    :param tree_root: root blob for traversal
    :param filename: requested file
    :return: requested file blob
    """
    tree = parse_tree(blobs, tree_root)

    if filename in tree.children:
        return tree.children[filename]

    for child in tree.children.values():
        if child.type_ == BlobType.TREE:
            return search_file(blobs, child, filename)
