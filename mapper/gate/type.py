from enum import Enum


class Type(Enum):

  def __init__(self, name, cost):
    self._value_ = name
    self.cost = cost

  CNOT = ("cx", 10)
  SWAP = ("swap", 30)
  MEASURE = ("measure", 0)
  ROTATE_Z = ("rz", 0)
  SQRT = ("sx", 1)
  BARRIER = ("barrier", 0)
  X = ("x", 1)
  FREE_SWAP = ("f_swap", 0)
  CHECKPOINT = ("checkpoint", 0)

  @staticmethod
  def from_name(name: str) -> "Type":
    if name == "cx": return Type.CNOT
    elif name == "swap": return Type.SWAP
    elif name == "measure": return Type.MEASURE
    elif name == "rz": return Type.ROTATE_Z
    elif name == "sx": return Type.SQRT
    elif name == "barrier": return Type.BARRIER
    elif name == "x": return Type.X
    elif name == "f_swap": return Type.FREE_SWAP
    elif name == "checkpoint": return Type.CHECKPOINT
    else: raise ValueError(f"Encountered unknown name: {name}")

