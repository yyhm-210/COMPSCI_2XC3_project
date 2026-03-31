import min_heap

def a_star(G, s, d, h):
    pred = {} # Predecessor dictionary
    dist = {} # Distance dictionary (represents g(n))
    Q = min_heap.MinHeap([])
    nodes = list(G.adj.keys())

    # Initialize priority queue/heap and distances
    for node in nodes:
        Q.insert(min_heap.Element(node, float("inf")))
        dist[node] = float("inf")
    dist[s] = 0
    Q.decrease_key(s, h[s])

    # Meat of the algorithm
    while not Q.is_empty():
        current_element = Q.extract_min()
        current_node = current_element.value
        
        # stop if we meet the destination
        if current_node == d:
            break

        for neighbour in G.adj[current_node]:
            if dist[current_node] + G.w(current_node, neighbour) < dist[neighbour]:
                dist[neighbour] = dist[current_node] + G.w(current_node, neighbour)
                pred[neighbour] = current_node
                # f(n) = g(n) + h(n)
                Q.decrease_key(neighbour, dist[current_node] + G.w(current_node, neighbour) + h[neighbour])

    # find the shortest path 
    path = []
    if d in pred or d == s:
        n = d
        while n != None:
            path.append(n)
            n = pred.get(n)
        path.reverse()

    return pred, path

