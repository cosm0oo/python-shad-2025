import json
from pathlib import Path
from compgraph import algorithms


def main() -> None:
    """Run PMI algorithm on text corpus"""
    resources_dir = Path(__file__).parent.parent / "resources"
    input_file = resources_dir / "text_corpus.txt"

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        print("Please extract resources/extract_me.tgz first")
        return

    graph = algorithms.pmi_graph("docs", doc_column="doc_id", text_column="text", result_column="pmi")

    def read_docs() -> list[dict[str, str]]:
        docs = []
        with open(input_file) as f:
            for line in f:
                docs.append(json.loads(line))
        return docs

    docs = read_docs()
    result = list(graph.run(docs=lambda: iter(docs)))

    print("PMI results (top 50 by PMI):")
    print("-" * 60)

    sorted_result = sorted(result, key=lambda x: x["pmi"], reverse=True)[:50]
    for row in sorted_result:
        doc_id = row['doc_id']
        if isinstance(doc_id, (int, float)):
            doc_id_str = f"{int(doc_id):5d}"
        else:
            doc_id_str = f"{str(doc_id):>5s}"
        print(f"Doc {doc_id_str} | {row['text']:20s} | PMI: {row['pmi']:.4f}")


if __name__ == "__main__":
    main()
