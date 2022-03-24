from typing import Set, List

import numpy as np

from mapper.gate.type import Type
from mapper.state.mapping import Mapping


class Gate:
  """
    Represents a gate in the quantum circuit
  """

  def __init__(self, type: Type, children: Set["Gate"], parents: Set["Gate"], q1: int, q2: int = -1, params: List = None):
    self.type = type
    self.children = children
    self.parents = parents
    if parents:
      self.depth = max(p.depth for p in parents) + 1
    else:
      self.depth = 0
    self.q1 = q1
    self.q2 = q2
    self.params = params

  
  def cost(self) -> int:
    """
      Returns the cost of the gate, as defined in mapper.gate.type.Type.
    """
    return self.type.cost

  
  def is_multi_qubit_gate(self) -> bool:
    """
      Returns true iff this gate uses more than 1 qubit.
    """
    return self.type == Type.CNOT or self.type == Type.SWAP


  def can_be_resolved(self, resolved_gates: Set["Gate"]) -> bool:
    """
      Returns true iff all gates this gate depends on have already been resolved.
    """
    return len(self.parents.difference(resolved_gates)) == 0


  def can_be_executed(self, costs: np.ndarray, mapping: Mapping) -> bool:
    """
      Returns true iff this gate can be executed, e.g. it only uses one qubit
      or the distance between q1 and q2 == 1
    """
    if self.type != Type.CNOT and self.type != Type.SWAP:
      return True

    return self.execution_distance(costs, mapping) == 1

  
  def execution_distance(self, costs: np.ndarray, mapping: Mapping) -> int:
    """
      Returns the distance between q1 and q2
    """
    p1, p2 = mapping.logical_to_physical(self.q1, self.q2)
    return costs[p1, p2]

  def to_logical(self, mapping: Mapping) -> "Gate":
    """
      Transforms this gate into another gate, which uses the mapping
    """
    p1, p2 = mapping.logical_to_physical(self.q1, self.q2)
    if self.type == Type.MEASURE:
      return Gate(self.type, None, None, p1, self.q2, self.params)
    return Gate(self.type, None, None, p1, p2, self.params)
  
  def __lt__(self, __o) -> bool:
    """
      Just some dummy < implementation for priority queue to add the checkpoint gates
    """
    return self.type != Type.CHECKPOINT


  def __repr__(self) -> str:
    return f"{self.type}: {self.q1} -> {self.q2} [{self.depth}]"
  
