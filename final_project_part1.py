import min_heap
import random

class DirectedWeightedGraph:

    def __init__(self):
        self.adj = {}
        self.weights = {}

    def are_connected(self, node1, node2):
        for neighbour in self.adj[node1]:
            if neighbour == node2:
                return True
        return False

    def adjacent_nodes(self, node):
        return self.adj[node]

    def add_node(self, node):
        self.adj[node] = []

    def add_edge(self, node1, node2, weight):
        if node2 not in self.adj[node1]:
            self.adj[node1].append(node2)
        self.weights[(node1, node2)] = weight

    def w(self, node1, node2):
        if self.are_connected(node1, node2):
            return self.weights[(node1, node2)]

    def number_of_nodes(self):
        return len(self.adj)


def dijkstra(G, source):
    pred = {} #Predecessor dictionary. Isn't returned, but here for your understanding
    dist = {} #Distance dictionary
    Q = min_heap.MinHeap([])
    nodes = list(G.adj.keys())

    #Initialize priority queue/heap and distances
    for node in nodes:
        Q.insert(min_heap.Element(node, float("inf")))
        dist[node] = float("inf")
    dist[source] = 0
    Q.decrease_key(source, 0)

    #Meat of the algorithm
    while not Q.is_empty():
        current_element = Q.extract_min()
        current_node = current_element.value
        dist[current_node] = current_element.key
        for neighbour in G.adj[current_node]:
            if neighbour in Q.map and dist[current_node] + G.w(current_node, neighbour) < dist[neighbour]:
                new_dist = dist[current_node] + G.w(current_node, neighbour)
                Q.decrease_key(neighbour, new_dist)
                dist[neighbour] = new_dist
                pred[neighbour] = current_node
    return dist

def dijkstra_approx(G, source, k):
    pred = {}
    dist = {}
    relax_count = {}
    Q = min_heap.MinHeap([])
    nodes = list(G.adj.keys())

    for node in nodes:
        Q.insert(min_heap.Element(node, float("inf")))
        dist[node] = float("inf")
        relax_count[node] = 0

    dist[source] = 0
    Q.decrease_key(source, 0)

    while not Q.is_empty():
        current_element = Q.extract_min()
        current_node = current_element.value
        dist[current_node] = current_element.key

        for neighbour in G.adj[current_node]:
            new_dist = dist[current_node] + G.w(current_node, neighbour)

            if (
                neighbour in Q.map
                and new_dist < dist[neighbour]
                and relax_count[neighbour] < k
            ):
                Q.decrease_key(neighbour, new_dist)
                dist[neighbour] = new_dist
                relax_count[neighbour] += 1
                pred[neighbour] = current_node

    return dist

def bellman_ford(G, source):
    pred = {} #Predecessor dictionary. Isn't returned, but here for your understanding
    dist = {} #Distance dictionary
    nodes = list(G.adj.keys())

    #Initialize distances
    for node in nodes:
        dist[node] = float("inf")
    dist[source] = 0

    #Meat of the algorithm
    for _ in range(G.number_of_nodes()):
        for node in nodes:
            if dist[node] == float("inf"):
                continue
            for neighbour in G.adj[node]:
                if dist[neighbour] > dist[node] + G.w(node, neighbour):
                    dist[neighbour] = dist[node] + G.w(node, neighbour)
                    pred[neighbour] = node
    return dist

def bellman_ford_approx(G, source, k):
    pred = {}
    dist = {}
    relax_count = {}
    nodes = list(G.adj.keys())

    for node in nodes:
        dist[node] = float("inf")
        relax_count[node] = 0
    dist[source] = 0

    for _ in range(G.number_of_nodes()):
        updated = False

        for node in nodes:
            if dist[node] == float("inf"):
                continue

            for neighbour in G.adj[node]:
                new_dist = dist[node] + G.w(node, neighbour)

                if new_dist < dist[neighbour] and relax_count[neighbour] < k:
                    dist[neighbour] = new_dist
                    relax_count[neighbour] += 1
                    pred[neighbour] = node
                    updated = True

        if not updated:
            break

    return dist

def total_dist(dist):
    total = 0
    for key in dist.keys():
        total += dist[key]
    return total

def finite_total_dist(dist):
    total = 0
    for value in dist.values():
        if value != float("inf"):
            total += value
    return total

def create_random_complete_graph(n,upper):
    G = DirectedWeightedGraph()
    for i in range(n):
        G.add_node(i)
    for i in range(n):
        for j in range(n):
            if i != j:
                G.add_edge(i,j,random.randint(1,upper))
    return G

def create_random_density_graph(n, density, upper):
    G = DirectedWeightedGraph()
    for i in range(n):
        G.add_node(i)
    for i in range(n - 1):
        G.add_edge(i, i + 1, random.randint(1, upper))
    max_edges = n * (n - 1)
    target_edges = int(density * max_edges)
    current_edges = len(G.weights)
    while current_edges < target_edges:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v and not G.are_connected(u, v):
            G.add_edge(u, v, random.randint(1, upper))
            current_edges += 1
    return G

#Assumes G represents its nodes as integers 0,1,...,(n-1)
def mystery(G):
    n = G.number_of_nodes()
    d = init_d(G)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][j] > d[i][k] + d[k][j]: 
                    d[i][j] = d[i][k] + d[k][j]
    return d

def init_d(G):
    n = G.number_of_nodes()
    d = [[float("inf") for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if G.are_connected(i, j):
                d[i][j] = G.w(i, j)
        d[i][i] = 0
    return d
