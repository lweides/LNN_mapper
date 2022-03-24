from queue import PriorityQueue
from typing import Dict, Set

import numpy as np

from mapper.state.state import State


def astar(initial_states: Set[State], costs: np.ndarray, neighbours: Dict[int, Set[int]], checkpoint_look_ahead: int) -> State:
  """
    Performs the astar algorithm.
    Does not allow states to be processed, which have a shallower checkpoint than the current deepest checkpoint.
  """
  pq = PriorityQueue()
  visited = set()
  checkpoint_depth = 0
  for state in initial_states:
    pq.put_nowait((0, state, ))

  while not pq.empty():
    cur_tuple = pq.get_nowait()
    current: State = cur_tuple[1]

    if current in visited:
      continue

    if current.checkpoint.depth < checkpoint_depth:
      continue

    visited.add(current)

    if current.is_done():
      return current

    for state in current.successors(costs, neighbours):
      checkpoint_depth = max(checkpoint_depth, state.checkpoint.depth)
      cost = state.total_cost(costs, checkpoint_look_ahead)
      pq.put_nowait((cost, state, ))

  raise Exception("Failed to map circuit")
