import csv
import math
import time
import matplotlib.pyplot as plt
from final_project_part1 import DirectedWeightedGraph, dijkstra
from Astar import a_star

def load_stations(file):
    stations = {}
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stations[int(row["id"])] = (float(row["latitude"]), float(row["longitude"]))
    return stations

def load_connections(file):
    edges = []
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges.append((int(row["station1"]), int(row["station2"])))
    return edges

def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def build_graph(stations, edges):
    G = DirectedWeightedGraph()
    for s in stations:
        G.add_node(s)
    for u, v in edges:
        w = distance(stations[u], stations[v])
        G.add_edge(u, v, w)
        G.add_edge(v, u, w)
    return G

def build_heuristic(stations, dest):
    h = {}
    for node in stations:
        h[node] = distance(stations[node], stations[dest])
    return h

def run_experiment(G, stations, pairs):
    dijkstra_times = []
    astar_times = []

    for s, d in pairs:
        start = time.time()
        dijkstra(G, s)
        dijkstra_times.append(time.time() - start)

        h = build_heuristic(stations, d)
        start = time.time()
        a_star(G, s, d, h)
        astar_times.append(time.time() - start)

    return dijkstra_times, astar_times

def main():
    stations = load_stations("london_stations.csv")
    edges = load_connections("london_connections.csv")
    G = build_graph(stations, edges)

    nodes = list(stations.keys())
    pairs = [(nodes[i], nodes[i+1]) for i in range(0, 50, 2)]

    dijkstra_times, astar_times = run_experiment(G, stations, pairs)

    x = list(range(len(pairs)))

    plt.figure()
    plt.plot(x, dijkstra_times, marker="o", label="Dijkstra")
    plt.plot(x, astar_times, marker="o", label="A*")
    plt.xlabel("Test Case Index")
    plt.ylabel("Time (seconds)")
    plt.title("Dijkstra vs A* Runtime Comparison")
    plt.legend()
    plt.grid(True)
    plt.show()

    avg_d = sum(dijkstra_times)/len(dijkstra_times)
    avg_a = sum(astar_times)/len(astar_times)

    plt.figure()
    plt.bar(["Dijkstra", "A*"], [avg_d, avg_a])
    plt.ylabel("Average Time (seconds)")
    plt.title("Average Runtime Comparison")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()