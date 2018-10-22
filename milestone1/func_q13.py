#  we modified the API to account for the matrix multiplication, in order to do it just once.
def compute_clustering_coefficient(adjacency, node, power_matrix=None):
    """Compute the clustering coefficient of a node.

    Parameters
    ----------
    adjacency: numpy array
        The (weighted) adjacency matrix of a graph.
    node: int
        The node whose clustering coefficient will be computed. A number between 0 and n_nodes-1.

    Returns
    -------
    float
        The clustering coefficient of the node. A number between 0 and 1.
    """

    degree = np.sum(adjacency, axis=0)
    if power_matrix == None:
        power_matrix = np.linalg.matrix_power(adjacency, 3)

    L = power_matrix[node][node] / 2
    k = degree[node]

    clustering_coefficient = L / (k * (k - 1) / 2)

    return clustering_coefficient, power_matrix