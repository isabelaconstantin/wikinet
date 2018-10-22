from scipy import sparse
import time

start = time.perf_counter()
As = sparse.csr_matrix(adjacency_undirected)
As = As*As*As
Ad = np.empty(adjacency_undirected.shape, dtype=adjacency_undirected.dtype)
As.todense(out=Ad)
print(time.perf_counter() - start)

start = time.perf_counter()
adjacency_undirected_power_3=np.linalg.matrix_power(adjacency_undirected,3)
print(time.perf_counter() - start)