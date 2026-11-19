from pathlib import Path
import os
import subprocess


def python_sort(file_in: Path, file_out: Path) -> None:
    """
    Sort tsv file using python built-in sort
    :param file_in: tsv file to read from
    :param file_out: tsv file to write to
    """
    with open(file_in, 'r', encoding='utf-8', newline='') as f:
        lines = f.readlines()

    def sort_key(line: str) -> tuple[int, str]:
        stripped = line.rstrip('\n\r')
        if not stripped:
            return (0, '')
        parts = stripped.split('\t', 1)
        if len(parts) >= 2:
            try:
                num = int(parts[1])
            except ValueError:
                num = 0
            return (num, parts[0])
        return (0, stripped)

    sorted_lines = sorted(lines, key=sort_key)

    with open(file_out, 'w', encoding='utf-8', newline='') as f:
        f.writelines(sorted_lines)


def util_sort(file_in: Path, file_out: Path) -> None:
    env = dict(os.environ)
    env['LC_ALL'] = 'C'

    with open(file_in, 'r', encoding='utf-8', newline='') as f_in:
        with open(file_out, 'w', encoding='utf-8', newline='') as f_out:
            subprocess.run(
                ['sort', '-t', '\t', '-k2,2n', '-k1,1'],
                stdin=f_in,
                stdout=f_out,
                check=True,
                env=env
            )
