from typing import List

from scipy.sparse.csgraph import dijkstra as dijkstra_scipy
import numpy as np


def dijkstra(coupling_map: List[List[int]], vertex_count: int) -> np.ndarray:
  """
    Performs a dijkstra algorithm upon the coupling_map, returning the distances between each qubit.
  """
  return dijkstra_scipy(_coupling_map_to_graph_matrix(coupling_map, vertex_count), directed=False)


def _coupling_map_to_graph_matrix(coupling_map: List[List[int]], vertex_count: int) -> np.ndarray:
  """
    Converts the coupling map into a graph.
  """
  matrix = np.zeros(shape=(vertex_count, vertex_count))
  for edge in coupling_map:
    matrix[edge[0], edge[1]] = 1
  return matrix

