import csv
import math
import os
import time
from collections import defaultdict
import matplotlib.pyplot as plt
from final_project_part1 import DirectedWeightedGraph, dijkstra
from Astar import a_star

def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_stations(path):
    stations = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_id = int(row["id"])
            stations[station_id] = {
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"]),
                "name": row.get("name", ""),
                "display_name": row.get("display_name", ""),
            }
    return stations


def build_graph(stations_path, connections_path):
    stations = load_stations(stations_path)
    graph = DirectedWeightedGraph()
    line_lookup = defaultdict(set)

    for station_id in stations:
        graph.add_node(station_id)

    with open(connections_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row["station1"])
            v = int(row["station2"])
            line = row.get("line", "")
            weight = haversine(
                stations[u]["lat"], stations[u]["lon"],
                stations[v]["lat"], stations[v]["lon"]
            )
            graph.add_edge(u, v, weight)
            graph.add_edge(v, u, weight)
            line_lookup[frozenset((u, v))].add(line)

    return graph, stations, line_lookup


def build_heuristics(stations):
    heuristics = {}
    node_ids = list(stations.keys())
    for dest in node_ids:
        heuristics[dest] = {}
        for node in node_ids:
            heuristics[dest][node] = haversine(
                stations[node]["lat"], stations[node]["lon"],
                stations[dest]["lat"], stations[dest]["lon"]
            )
    return heuristics


def path_line_count(path, line_lookup):
    if len(path) < 2:
        return 0
    used_lines = set()
    for u, v in zip(path[:-1], path[1:]):
        used_lines.update(line_lookup[frozenset((u, v))])
    return len(used_lines)


def bucket_label(value, edges):
    for left, right in zip(edges[:-1], edges[1:]):
        if left <= value < right:
            return f"{left}-{right}"
    return f"{edges[-2]}+"


def run_experiments(graph, stations, heuristics, line_lookup):
    node_ids = list(stations.keys())
    pair_records = []

    for source in node_ids:
        start = time.perf_counter()
        dist = dijkstra(graph, source)
        dijkstra_source_time = time.perf_counter() - start

        normalized_dijkstra_time = dijkstra_source_time

        for dest in node_ids:
            if source == dest:
                continue

            start = time.perf_counter()
            pred, path = a_star(graph, source, dest, heuristics[dest])
            astar_time = time.perf_counter() - start

            line_count = path_line_count(path, line_lookup)
            distance = dist[dest]
            speedup = normalized_dijkstra_time / astar_time if astar_time > 0 else float("inf")

            pair_records.append({
                "source": source,
                "dest": dest,
                "dijkstra_time": normalized_dijkstra_time,
                "astar_time": astar_time,
                "distance": distance,
                "line_count": line_count,
                "speedup": speedup
            })

    return pair_records


def plot_overall_runtime(pair_records):
    d_times = [r["dijkstra_time"] for r in pair_records]
    a_times = [r["astar_time"] for r in pair_records]

    mean_d = sum(d_times) / len(d_times)
    mean_a = sum(a_times) / len(a_times)

    plt.figure()
    plt.plot(["Dijkstra", "A*"], [mean_d, mean_a], marker="o")
    plt.xlabel("Algorithm")
    plt.ylabel("Average Runtime (seconds)")
    plt.title("Experiment 1: Overall Runtime Comparison")
    plt.grid(True)
    plt.show()


def plot_line_transfer_runtime(pair_records):
    buckets = {1: [], 2: [], 3: [], 4: [], 5: []}

    for r in pair_records:
        key = r["line_count"]
        if key >= 5:
            key = 5
        if key >= 1:
            buckets[key].append((r["dijkstra_time"], r["astar_time"]))

    labels = ["1", "2", "3", "4", "5+"]
    d_vals = []
    a_vals = []

    for key in [1, 2, 3, 4, 5]:
        values = buckets[key]
        if values:
            d_vals.append(sum(x for x, _ in values) / len(values))
            a_vals.append(sum(y for _, y in values) / len(values))
        else:
            d_vals.append(0.0)
            a_vals.append(0.0)

    plt.figure()
    plt.plot(labels, d_vals, marker="o", label="Dijkstra")
    plt.plot(labels, a_vals, marker="o", label="A*")
    plt.xlabel("Number of Lines Used")
    plt.ylabel("Average Runtime (seconds)")
    plt.title("Experiment 2: Runtime vs Line Transfers")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_distance_speedup(pair_records):
    edges = [0, 2, 5, 10, 15, 20, 30, 40, 60]
    buckets = {bucket_label(left, edges): [] for left in edges[:-1]}
    labels = [f"{left}-{right}" for left, right in zip(edges[:-1], edges[1:])]

    for r in pair_records:
        label = bucket_label(r["distance"], edges)
        if label in buckets:
            buckets[label].append(r["speedup"])

    speedups = []
    for label in labels:
        values = buckets[label]
        speedups.append(sum(values) / len(values) if values else 0.0)

    plt.figure()
    plt.plot(labels, speedups, marker="o")
    plt.xlabel("Straight-line Distance (km)")
    plt.ylabel("Average Dijkstra / A* Speedup")
    plt.title("Experiment 3: Speedup vs Distance")
    plt.grid(True)
    plt.show()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    stations_file = os.path.join(base_dir, "london_stations.csv")
    connections_file = os.path.join(base_dir, "london_connections.csv")

    graph, stations, line_lookup = build_graph(stations_file, connections_file)
    heuristics = build_heuristics(stations)

    pair_records = run_experiments(graph, stations, heuristics, line_lookup)

    plot_overall_runtime(pair_records)
    plot_line_transfer_runtime(pair_records)
    plot_distance_speedup(pair_records)


if __name__ == "__main__":
    main()