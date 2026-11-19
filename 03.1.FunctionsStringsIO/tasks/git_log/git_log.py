import typing as tp


def reformat_git_log(inp: tp.IO[str], out: tp.IO[str]) -> None:
    """Reads git log from `inp` stream, reformats it and prints to `out` stream

    Expected input format: `<sha-1>\t<date>\t<author>\t<email>\t<message>`
    Output format: `<first 7 symbols of sha-1>.....<message>`
    """
    for line in inp:
        parts = line.strip().split('\t')
        sha = parts[0][:7]
        message = parts[4]
        dots_count = 80 - 7 - len(message)
        formatted = f"{sha}{'.' * dots_count}{message}\n"
        out.write(formatted)
