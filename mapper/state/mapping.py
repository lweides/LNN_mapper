from typing import Tuple

import numpy as np


class Mapping:
  """
    Represents a mapping from physical to logical qubits
  """
  def __init__(self, qubit_count: int, logical_to_physical: np.ndarray = None, physical_to_logical: np.ndarray = None):
    if logical_to_physical is None:
      if physical_to_logical is not None:
        raise ValueError("physical_to_logical has to be None if logical_to_physical is None")
      logical_to_physical = np.arange(qubit_count)
      physical_to_logical = np.arange(qubit_count)
    else:
      if physical_to_logical is None:
        physical_to_logical = np.argsort(logical_to_physical)

    self._qubit_count = qubit_count
    self._logical_to_physical = logical_to_physical
    self._physical_to_logical = physical_to_logical

    self._logical_to_physical.flags.writeable = False
    self._physical_to_logical.flags.writeable = False

  
  def swap(self, q1: int, q2: int) -> "Mapping":
    """
      Swaps the logical qubits q1 and q2
    """
    ltp = self._logical_to_physical.copy()
    ltp[q1], ltp[q2] = ltp[q2], ltp[q1]

    p1, p2 = ltp[q2], ltp[q1]
    ptl = self._physical_to_logical.copy()
    ptl[p1], ptl[p2] = ptl[p2], ptl[p1]
    return Mapping(self._qubit_count, ltp, ptl)

  def swap_inplace(self, q1: int, q2: int):
    """
      Performs a swap operation inplace
    """
    self._logical_to_physical.flags.writeable = True
    self._physical_to_logical.flags.writeable = True

    self._logical_to_physical[q1], self._logical_to_physical[q2] = self._logical_to_physical[q2], self._logical_to_physical[q1]
    p1, p2 = self._logical_to_physical[q2], self._logical_to_physical[q1]
    self._physical_to_logical[p1], self._physical_to_logical[p2] = self._physical_to_logical[p2], self._physical_to_logical[p1]

    self._logical_to_physical.flags.writeable = False
    self._physical_to_logical.flags.writeable = False



  def logical_to_physical(self, l1: int, l2: int = 0) -> Tuple[int, int]:
    """
      Maps the logical qubits l1 and l2 to their current physical mapping
    """
    p1 = self._logical_to_physical[l1]
    p2 = self._logical_to_physical[l2]
    return p1, p2


  def physical_to_logical(self, p1: int, p2: int = 0) -> Tuple[int, int]:
    """
      Maps the physical qubits p1 and p2 to their current logical mapping.
      An inverse of Mapping::logical_to_physical(...)
    """
    return self._physical_to_logical[p1], self._physical_to_logical[p2]

  
  def __eq__(self, __o: object) -> bool:
    if __o is None or not isinstance(__o, Mapping):
      return False

    return self._qubit_count == __o._qubit_count \
      and (self._logical_to_physical == __o._logical_to_physical).all()

  
  def __hash__(self) -> int:
    return self._qubit_count ^ self._logical_to_physical.data.tobytes().__hash__()

  
  def __repr__(self) -> str:
    repr = ""
    for l, p in enumerate(self._logical_to_physical):
      if l != p:
        repr += f"{l} -> {p}, "
    return repr[:-2]