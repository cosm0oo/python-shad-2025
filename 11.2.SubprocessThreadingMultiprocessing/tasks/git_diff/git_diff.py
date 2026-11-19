import subprocess
from pathlib import Path


def get_changed_dirs(git_path: Path, from_commit_hash: str, to_commit_hash: str) -> set[Path]:
    """
    Get directories which content was changed between two specified commits
    :param git_path: path to git repo directory
    :param from_commit_hash: hash of commit to do diff from
    :param to_commit_hash: hash of commit to do diff to
    :return: sequence of changed directories between specified commits
    """
    result = subprocess.run(
        ['git', 'diff', '--name-only', from_commit_hash, to_commit_hash],
        cwd=git_path,
        capture_output=True,
        text=True,
        check=True
    )

    changed_files = result.stdout.strip().split('\n')
    if not changed_files or changed_files == ['']:
        return set()

    dirs = set()
    for file_path in changed_files:
        if file_path:
            file_path_obj = Path(file_path)
            parent_dir = file_path_obj.parent
            if parent_dir == Path('.'):
                dirs.add(git_path)
            else:
                dirs.add(git_path / parent_dir)

    return dirs
