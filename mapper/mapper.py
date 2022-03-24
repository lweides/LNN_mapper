from typing import List

from mapper.algorithms.astar import astar
from mapper.algorithms.checkpoints import add_checkpoints
from mapper.algorithms.dijkstra import dijkstra
from mapper.qasm.input import get_neighbours, read_gates
from mapper.qasm.mapping_info import MappingInfo
from mapper.qasm.output import create_mapping_comment, state_to_circuit
from mapper.state.mapping import Mapping
from mapper.state.state import State


def map(input_file: str, output_file: str, coupling_map: List[List[int]], checkpoint_offset: int = 3, checkpoint_look_ahead: int = 2) -> MappingInfo:
  """
    Maps the circuit given in input_file to the architecture specified by the coupling_map.
    Writes the mapped circuit into the output_file, with a comment at the end which
    specifies the initial mapping of the logical to the physical qubits.
  """
  working_set, gates, cregs = read_gates(input_file)
  checkpoint = add_checkpoints(working_set, checkpoint_offset)

  neighbours = get_neighbours(coupling_map)
  qubit_count = len(neighbours)
  costs = dijkstra(coupling_map, qubit_count)
  remaining_cost = sum(g.cost() for g in gates)

  # atm no initial mapping is computed, this could improve the performace drastically
  mapping = Mapping(qubit_count)
  state = State({ checkpoint }, set(), mapping, 0, remaining_cost, None, None, set(), checkpoint)

  result = astar({ state }, costs, neighbours, checkpoint_look_ahead)

  qc, initial_mapping, swaps, free_swaps = state_to_circuit(result, cregs, mapping)
  comment = create_mapping_comment(initial_mapping)

  qc.qasm(filename=output_file)
  with open(output_file, "a") as f:
    f.write(comment + "\n")

  return MappingInfo(swaps, free_swaps, result.cost, initial_mapping)
