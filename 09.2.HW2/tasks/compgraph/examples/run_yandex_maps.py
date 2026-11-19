import json
from pathlib import Path
from compgraph import algorithms


def main() -> None:
    """Run Yandex Maps speed analysis algorithm"""
    resources_dir = Path(__file__).parent.parent / "resources"
    times_file = resources_dir / "travel_times.txt"
    lengths_file = resources_dir / "road_graph_data.txt"

    if not times_file.exists() or not lengths_file.exists():
        print("Error: Input files not found")
        print("Please extract resources/extract_me.tgz first")
        return

    graph = algorithms.yandex_maps_graph(
        "travel_time",
        "edge_length",
        enter_time_column="enter_time",
        leave_time_column="leave_time",
        edge_id_column="edge_id",
        start_coord_column="start",
        end_coord_column="end",
        weekday_result_column="weekday",
        hour_result_column="hour",
        speed_result_column="speed",
    )

    def read_times() -> list[dict[str, str]]:
        times = []
        with open(times_file) as f:
            for line in f:
                times.append(json.loads(line))
        return times

    def read_lengths() -> list[dict[str, str]]:
        lengths = []
        with open(lengths_file) as f:
            for line in f:
                lengths.append(json.loads(line))
        return lengths

    times = read_times()
    lengths = read_lengths()

    result = list(graph.run(travel_time=lambda: iter(times), edge_length=lambda: iter(lengths)))

    print("Average speed by weekday and hour:")
    print("-" * 50)
    print(f"{'Weekday':<10} {'Hour':<6} {'Speed (km/h)':<15}")
    print("-" * 50)

    sorted_result = sorted(result, key=lambda x: (x["weekday"], x["hour"]))
    for row in sorted_result:
        hour = row['hour']
        if isinstance(hour, (int, float)):
            hour_str = f"{int(hour):<6}"
        else:
            hour_str = f"{str(hour):<6}"
        speed = row['speed']
        if isinstance(speed, (int, float)):
            speed_str = f"{float(speed):<15.2f}"
        else:
            speed_str = f"{str(speed):<15}"
        print(f"{row['weekday']:<10} {hour_str} {speed_str}")


if __name__ == "__main__":
    main()
