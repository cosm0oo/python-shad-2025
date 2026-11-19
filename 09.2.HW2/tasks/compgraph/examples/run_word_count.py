import json
from pathlib import Path
from compgraph import algorithms


def main() -> None:
    """Run word count algorithm on text corpus"""
    resources_dir = Path(__file__).parent.parent / "resources"
    input_file = resources_dir / "text_corpus.txt"

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        print("Please extract resources/extract_me.tgz first")
        return

    graph = algorithms.word_count_graph("docs", text_column="text", count_column="count")

    def read_docs() -> list[dict[str, str]]:
        docs = []
        with open(input_file) as f:
            for line in f:
                docs.append(json.loads(line))
        return docs

    docs = read_docs()
    result = list(graph.run(docs=lambda: iter(docs)))

    print("Word count results (top 20):")
    print("-" * 40)
    for row in result[-20:]:
        count = row['count']
        if isinstance(count, (int, float)):
            count_str = f"{int(count):5d}"
        else:
            count_str = f"{str(count):>5s}"
        print(f"{row['text']:20s} {count_str}")


if __name__ == "__main__":
    main()
