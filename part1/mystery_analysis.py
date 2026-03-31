import time
import math
import random
import matplotlib.pyplot as plt

from final_project_part1 import (
    DirectedWeightedGraph,
    create_random_complete_graph,
    mystery,
)

UPPER_WEIGHT = 20
TRIALS = 5


def print_matrix(M):
    for row in M:
        print(row)
    print()


def manual_test_positive():
    G = DirectedWeightedGraph()
    for i in range(4):
        G.add_node(i)

    G.add_edge(0, 1, 4)
    G.add_edge(0, 2, 10)
    G.add_edge(1, 2, 2)
    G.add_edge(2, 3, 3)
    G.add_edge(1, 3, 8)

    print("Manual Test 1: Positive Weights")
    result = mystery(G)
    print_matrix(result)


def manual_test_negative_edge():
    G = DirectedWeightedGraph()
    for i in range(4):
        G.add_node(i)

    G.add_edge(0, 1, 4)
    G.add_edge(0, 2, 11)
    G.add_edge(1, 2, -2)
    G.add_edge(2, 3, 3)
    G.add_edge(1, 3, 10)

    print("Manual Test 2: Negative Edge, No Negative Cycle")
    result = mystery(G)
    print_matrix(result)


def runtime_experiment():
    n_values = [10, 20, 30, 40, 50, 60]
    avg_times = []

    for n in n_values:
        runs = []

        for _ in range(TRIALS):
            G = create_random_complete_graph(n, UPPER_WEIGHT)

            start = time.perf_counter()
            mystery(G)
            end = time.perf_counter()

            runs.append(end - start)

        avg_times.append(sum(runs) / len(runs))

    plt.figure()
    plt.plot(n_values, avg_times, marker="o")
    plt.xlabel("Number of Nodes (n)")
    plt.ylabel("Average Runtime (seconds)")
    plt.title("Mystery Algorithm Runtime vs Graph Size")
    plt.grid(True)
    plt.savefig("mystery_runtime.png", dpi=300, bbox_inches="tight")
    plt.close()

    return n_values, avg_times


def loglog_experiment(n_values, avg_times):
    log_n = [math.log(x) for x in n_values]
    log_t = [math.log(y) for y in avg_times]

    plt.figure()
    plt.plot(log_n, log_t, marker="o")
    plt.xlabel("log(n)")
    plt.ylabel("log(runtime)")
    plt.title("Mystery Algorithm Log-Log Plot")
    plt.grid(True)
    plt.savefig("mystery_loglog.png", dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    random.seed(42)

    manual_test_positive()
    manual_test_negative_edge()

    n_values, avg_times = runtime_experiment()
    loglog_experiment(n_values, avg_times)

    print("n values:", n_values)
    print("average times:", avg_times)
    print("Mystery analysis graphs generated.")