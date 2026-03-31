import random
import time
import matplotlib.pyplot as plt

from final_project_part1 import (
    create_random_complete_graph,
    create_random_density_graph,
    dijkstra,
    bellman_ford,
    dijkstra_approx,
    bellman_ford_approx,
    finite_total_dist,
)

UPPER_WEIGHT = 20
SOURCE = 0
TRIALS = 12


def relative_error(exact_dist, approx_dist):
    exact_total = finite_total_dist(exact_dist)
    approx_total = finite_total_dist(approx_dist)

    if exact_total == 0:
        return 0.0

    return (approx_total - exact_total) / exact_total


def average(values):
    return sum(values) / len(values)


# Experiment 1:
# Goal: study how approximation quality changes as k increases.
# Design: keep graph size fixed at n = 50 and use complete graphs.
# Variable changed: k in [1, 2, 3, 5, 10, 20].
# What to observe: whether larger k makes the approximate result closer to the exact result.

def experiment_1_effect_of_k():
    n = 50
    k_values = [1, 2, 3, 5, 10, 20]

    dijkstra_errors = []
    bellman_errors = []

    for k in k_values:
        d_errors = []
        b_errors = []

        for _ in range(TRIALS):
            G = create_random_complete_graph(n, UPPER_WEIGHT)

            exact_d = dijkstra(G, SOURCE)
            exact_b = bellman_ford(G, SOURCE)

            approx_d = dijkstra_approx(G, SOURCE, k)
            approx_b = bellman_ford_approx(G, SOURCE, k)

            d_errors.append(relative_error(exact_d, approx_d))
            b_errors.append(relative_error(exact_b, approx_b))

        dijkstra_errors.append(average(d_errors))
        bellman_errors.append(average(b_errors))

    plt.figure()
    plt.plot(k_values, dijkstra_errors, marker="o", label="Dijkstra Approx")
    plt.plot(k_values, bellman_errors, marker="o", label="Bellman-Ford Approx")
    plt.xlabel("k")
    plt.ylabel("Average Relative Error")
    plt.title("Experiment 1: Effect of k on Approximation Quality")
    plt.legend()
    plt.grid(True)
    plt.savefig("exp1_k_vs_error.png", dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "k_values": k_values,
        "dijkstra_errors": dijkstra_errors,
        "bellman_errors": bellman_errors,
    }


# Experiment 2:
# Goal: study how runtime changes as the graph becomes larger.
# Design: keep k fixed at 5 and use complete graphs.
# Variable changed: n in [10, 20, 50, 100].
# What to observe: whether both approximation algorithms take more time on larger graphs.

def experiment_2_effect_of_n():
    n_values = [10, 20, 50, 100]
    k = 5

    dijkstra_times = []
    bellman_times = []

    for n in n_values:
        d_runs = []
        b_runs = []

        for _ in range(TRIALS):
            G = create_random_complete_graph(n, UPPER_WEIGHT)

            start = time.perf_counter()
            dijkstra_approx(G, SOURCE, k)
            end = time.perf_counter()
            d_runs.append(end - start)

            start = time.perf_counter()
            bellman_ford_approx(G, SOURCE, k)
            end = time.perf_counter()
            b_runs.append(end - start)

        dijkstra_times.append(average(d_runs))
        bellman_times.append(average(b_runs))

    plt.figure()
    plt.plot(n_values, dijkstra_times, marker="o", label="Dijkstra Approx")
    plt.plot(n_values, bellman_times, marker="o", label="Bellman-Ford Approx")
    plt.xlabel("Number of Nodes (n)")
    plt.ylabel("Average Runtime (seconds)")
    plt.title("Experiment 2: Effect of Graph Size on Runtime")
    plt.legend()
    plt.grid(True)
    plt.savefig("exp2_n_vs_runtime.png", dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "n_values": n_values,
        "dijkstra_times": dijkstra_times,
        "bellman_times": bellman_times,
    }


# Experiment 3:
# Goal: study how approximation quality changes as graph density changes.
# Design: keep n fixed at 50 and k fixed at 3.
# Variable changed: density in [0.1, 0.3, 0.6, 1.0].
# What to observe: whether denser graphs make it easier or harder for the approximation algorithms
# to find good paths under a fixed relaxation limit.

def experiment_3_effect_of_density():
    n = 50
    k = 3
    density_values = [0.1, 0.3, 0.6, 1.0]

    dijkstra_errors = []
    bellman_errors = []

    for density in density_values:
        d_errors = []
        b_errors = []

        for _ in range(TRIALS):
            if density == 1.0:
                G = create_random_complete_graph(n, UPPER_WEIGHT)
            else:
                G = create_random_density_graph(n, density, UPPER_WEIGHT)

            exact_d = dijkstra(G, SOURCE)
            exact_b = bellman_ford(G, SOURCE)

            approx_d = dijkstra_approx(G, SOURCE, k)
            approx_b = bellman_ford_approx(G, SOURCE, k)

            d_errors.append(relative_error(exact_d, approx_d))
            b_errors.append(relative_error(exact_b, approx_b))

        dijkstra_errors.append(average(d_errors))
        bellman_errors.append(average(b_errors))

    plt.figure()
    plt.plot(density_values, dijkstra_errors, marker="o", label="Dijkstra Approx")
    plt.plot(density_values, bellman_errors, marker="o", label="Bellman-Ford Approx")
    plt.xlabel("Graph Density")
    plt.ylabel("Average Relative Error")
    plt.title("Experiment 3: Effect of Graph Density on Approximation Quality")
    plt.legend()
    plt.grid(True)
    plt.savefig("exp3_density_vs_error.png", dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "density_values": density_values,
        "dijkstra_errors": dijkstra_errors,
        "bellman_errors": bellman_errors,
    }


if __name__ == "__main__":
    random.seed(42)

    results_1 = experiment_1_effect_of_k()
    results_2 = experiment_2_effect_of_n()
    results_3 = experiment_3_effect_of_density()

    print("Experiment 1:", results_1)
    print("Experiment 2:", results_2)
    print("Experiment 3:", results_3)
    print("All graphs generated.")