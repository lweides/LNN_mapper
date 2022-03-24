from mapper.state.mapping import Mapping


class MappingInfo:
  """
    Collected information about one mapping pass.
  """
  def __init__(self, swaps: int, free_swaps: int, cost: int, initial_mapping: Mapping):
    self.swaps = swaps
    self.free_swaps = free_swaps
    self.cost = cost
    self.initial_mapping = initial_mapping


  def __repr__(self) -> str:
    return f"swaps: {self.swaps}, free_swaps: {self.free_swaps}, cost: {self.cost}, initial_mapping: {self.initial_mapping}"
    