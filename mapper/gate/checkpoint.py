from typing import Set

import numpy as np

from mapper.gate.gate import Gate
from mapper.gate.type import Type
from mapper.state.mapping import Mapping


class Checkpoint(Gate):
  """
    Checkpoint gates segement the circuit into smaller parts.
  """

  def __init__(self):
    super().__init__(Type.CHECKPOINT, set(), set(), -1)
    self.gates = set()
    self.prev: Checkpoint = None
    self.next: Checkpoint = None
    self.done = False

  
  def can_be_executed(self, costs: np.ndarray, mapping: Mapping) -> bool:
      return self.next is not None


  def to_logical(self, mapping: Mapping) -> "Gate":
      return self

  
  def gates_to_consider(self, look_ahead: int) -> Set[Gate]:
    """
      Returns the gates, which should be considered for the heuristic.
    """
    gates = set()
    cp = self
    i = 0
    while cp and i < look_ahead:
      gates.update(cp.gates)
      i += 1
      cp = cp.next
    return gates


  def __repr__(self) -> str:
    return f"CHECKPOINT [{self.depth}]"

  