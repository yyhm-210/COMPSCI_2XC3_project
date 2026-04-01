
import csv
import heapq
import math
import os
import time
from collections import defaultdict

import matplotlib.pyplot as plt


class DirectedWeightedGraph:
    def __init__(self):
        self.adj = {}
        self.weights = {}

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, node1, node2, weight):
        self.add_node(node1)
        self.add_node(node2)
        if node2 not in self.adj[node1]:
            self.adj[node1].append(node2)
        self.weights[(node1, node2)] = weight

    def w(self, node1, node2):
        return self.weights[(node1, node2)]

    def get_adj_nodes(self, node):
        return self.adj[node]

    def get_num_of_nodes(self):
        return len(self.adj)


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
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_id = int(row['id'])
            stations[station_id] = {
                'lat': float(row['latitude']),
                'lon': float(row['longitude']),
                'name': row['name'],
                'display_name': row['display_name'],
                'zone': row['zone'],
                'total_lines': int(row['total_lines']),
                'rail': int(row['rail'])
            }
    return stations


def build_graph(stations_path, connections_path):
    stations = load_stations(stations_path)
    graph = DirectedWeightedGraph()
    line_lookup = defaultdict(set)

    with open(connections_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row['station1'])
            v = int(row['station2'])
            line = int(row['line'])
            w = haversine(stations[u]['lat'], stations[u]['lon'], stations[v]['lat'], stations[v]['lon'])
            graph.add_edge(u, v, w)
            graph.add_edge(v, u, w)
            line_lookup[(u, v)].add(line)
            line_lookup[(v, u)].add(line)

    return graph, stations, line_lookup


def build_heuristics(stations):
    nodes = list(stations.keys())
    heuristics = {}
    for dest in nodes:
        lat2 = stations[dest]['lat']
        lon2 = stations[dest]['lon']
        heuristics[dest] = {
            node: haversine(stations[node]['lat'], stations[node]['lon'], lat2, lon2)
            for node in nodes
        }
    return heuristics


def reconstruct_path(pred, source, dest):
    if source == dest:
        return [source]
    if dest not in pred:
        return []
    path = [dest]
    current = dest
    while current != source:
        current = pred[current]
        path.append(current)
    path.reverse()
    return path


def dijkstra(graph, source):
    dist = {node: math.inf for node in graph.adj}
    pred = {}
    dist[source] = 0.0
    pq = [(0.0, source)]
    visited = set()

    while pq:
        current_dist, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        for neighbour in graph.get_adj_nodes(node):
            new_dist = current_dist + graph.w(node, neighbour)
            if new_dist < dist[neighbour]:
                dist[neighbour] = new_dist
                pred[neighbour] = node
                heapq.heappush(pq, (new_dist, neighbour))

    return pred, dist


def a_star(graph, source, dest, heuristic):
    dist = {node: math.inf for node in graph.adj}
    pred = {}
    dist[source] = 0.0
    pq = [(heuristic[source], source)]
    visited = set()

    while pq:
        _, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        if node == dest:
            break
        for neighbour in graph.get_adj_nodes(node):
            new_dist = dist[node] + graph.w(node, neighbour)
            if new_dist < dist[neighbour]:
                dist[neighbour] = new_dist
                pred[neighbour] = node
                heapq.heappush(pq, (new_dist + heuristic[neighbour], neighbour))

    return pred, reconstruct_path(pred, source, dest), dist


def path_line_count(path, line_lookup):
    if len(path) < 2:
        return 0
    used = set()
    for u, v in zip(path, path[1:]):
        used.update(line_lookup[(u, v)])
    return len(used)


def bucket_label(value, edges):
    for left, right in zip(edges[:-1], edges[1:]):
        if left <= value < right:
            return f'{left}-{right}'
    return f'{edges[-2]}+'


def plot_overall_runtime(mean_dijkstra, mean_astar):
    plt.figure(figsize=(7, 5))
    plt.plot(['Dijkstra', 'A*'], [mean_dijkstra, mean_astar], marker='o')
    plt.xlabel('Algorithm')
    plt.ylabel('Average Runtime (seconds)')
    plt.title('Experiment 1: Overall Runtime Comparison')
    plt.grid(True)
    plt.show()


def plot_line_bucket_runtime(labels, dijkstra_values, astar_values):
    x = range(len(labels))
    plt.figure(figsize=(9, 5))
    plt.plot(list(x), dijkstra_values, marker='o', label='Dijkstra')
    plt.plot(list(x), astar_values, marker='o', label='A*')
    plt.xticks(list(x), labels)
    plt.xlabel('Distinct line count in shortest path')
    plt.ylabel('Average Runtime (seconds)')
    plt.title('Experiment 2: Runtime vs. Number of Lines Used')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_distance_speedup(labels, speedups):
    x = range(len(labels))
    plt.figure(figsize=(10, 5))
    plt.plot(list(x), speedups, marker='o')
    plt.xticks(list(x), labels)
    plt.xlabel('Straight-line distance bin (km)')
    plt.ylabel('Average Dijkstra/A* Speedup')
    plt.title('Experiment 3: Speedup vs. Source-Destination Distance')
    plt.grid(True)
    plt.show()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stations_path = os.path.join(base_dir, 'london_stations.csv')
    connections_path = os.path.join(base_dir, 'london_connections.csv')

    graph, stations, line_lookup = build_graph(stations_path, connections_path)
    heuristics = build_heuristics(stations)
    nodes = list(stations.keys())

    results = []
    line_buckets = {1: [], 2: [], 3: [], 4: [], 5: []}
    distance_edges = [0, 2, 5, 10, 15, 20, 30, 40, 60]
    distance_buckets = {f'{left}-{right}': [] for left, right in zip(distance_edges[:-1], distance_edges[1:])}

    t0 = time.perf_counter()
    pair_count = 0

    for source in nodes:
        start = time.perf_counter()
        _, dijkstra_dist = dijkstra(graph, source)
        dijkstra_time = time.perf_counter() - start

        for dest in nodes:
            if source == dest:
                continue

            start = time.perf_counter()
            _, path, _ = a_star(graph, source, dest, heuristics[dest])
            astar_time = time.perf_counter() - start

            shortest_distance = dijkstra_dist[dest]
            hop_count = max(len(path) - 1, 0)
            line_count = path_line_count(path, line_lookup)
            speedup = dijkstra_time / astar_time if astar_time > 0 else math.inf

            results.append([
                source, dest, dijkstra_time, astar_time,
                shortest_distance, hop_count, line_count, speedup
            ])

            line_key = line_count if line_count < 5 else 5
            line_buckets[line_key].append((dijkstra_time, astar_time))

            distance_key = bucket_label(shortest_distance, distance_edges)
            if distance_key in distance_buckets:
                distance_buckets[distance_key].append(speedup)

            pair_count += 1

    elapsed = time.perf_counter() - t0

    dijkstra_times = [row[2] for row in results]
    astar_times = [row[3] for row in results]
    mean_dijkstra = sum(dijkstra_times) / len(dijkstra_times)
    mean_astar = sum(astar_times) / len(astar_times)

    line_labels = ['1', '2', '3', '4', '5+']
    line_dijkstra = []
    line_astar = []
    for key in [1, 2, 3, 4, 5]:
        values = line_buckets[key]
        if values:
            line_dijkstra.append(sum(x for x, _ in values) / len(values))
            line_astar.append(sum(y for _, y in values) / len(values))
        else:
            line_dijkstra.append(0.0)
            line_astar.append(0.0)

    distance_labels = [f'{left}-{right}' for left, right in zip(distance_edges[:-1], distance_edges[1:])]
    distance_speedups = []
    for label in distance_labels:
        values = distance_buckets[label]
        distance_speedups.append(sum(values) / len(values) if values else 0.0)

    plot_overall_runtime(mean_dijkstra, mean_astar)
    plot_line_bucket_runtime(line_labels, line_dijkstra, line_astar)
    plot_distance_speedup(distance_labels, distance_speedups)

    faster_fraction = sum(1 for row in results if row[7] > 1) / len(results)
    print(f'Pairs processed: {pair_count}')
    print(f'Total runtime: {elapsed:.2f} seconds')
    print(f'Average Dijkstra runtime: {mean_dijkstra:.6f} seconds')
    print(f'Average A* runtime: {mean_astar:.6f} seconds')
    print(f'A* faster fraction: {faster_fraction:.4f}')


if __name__ == '__main__':
    main()
