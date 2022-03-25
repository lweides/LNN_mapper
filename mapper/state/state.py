from typing import Dict, Set

import numpy as np

from mapper.gate.checkpoint import Checkpoint
from mapper.gate.gate import Gate
from mapper.gate.type import Type
from mapper.state.mapping import Mapping


class State:
  """
    Represents a state in the search space
  """

  BRIDGE_DISTANCE = 3

  def __init__(self, working_set: Set[Gate], resolved_gates: Set[Gate], mapping: Mapping, cost: int, remaining_cost: int, output: Gate, parent: "State", used_qubits: Set[int], checkpoint: Checkpoint):
    """
      Creates a new state.
      The working_set represents the gates which are currently considered,
      the resolved_gates all the gates which have already been resolved.
    """
    self.working_set = working_set
    self.resolved_gates = resolved_gates
    self.mapping = mapping
    self.cost = cost
    self.remaining_cost = remaining_cost
    self.output = output
    self.parent = parent
    self.used_qubits = used_qubits
    self.checkpoint = checkpoint

  
  def total_cost(self, costs: np.ndarray, checkpoint_look_ahead: int) -> int:
    """
      Returns the total cost, e.g. cost until now + heuristic cost until the end
    """
    return self.cost + self._heuristic(costs, checkpoint_look_ahead)


  def _heuristic(self, costs: np.ndarray, checkpoint_look_ahead: int) -> int:
    """
      Returns the estimated cost until the end
    """
    return self.remaining_cost \
      + self._remaining_swaps(costs, checkpoint_look_ahead) * 30


  def _remaining_swaps(self, costs: np.ndarray, checkpoint_look_ahead: int) -> int:
    """
      Sums all swaps in the remaining_gates set, which is not admissible
    """
    sum = 0
    for gate in self.checkpoint.prev.gates_to_consider(checkpoint_look_ahead):
      if gate.type != Type.CNOT or gate in self.resolved_gates:
        continue
  
      p1, p2 = self.mapping.logical_to_physical(gate.q1, gate.q2)
      cost = costs[p1, p2] - 1
      sum += cost
    return sum

  def is_done(self) -> bool:
    """
      Returns true iff the circuit is mapped completely
    """
    l = len(self.working_set)
    if l == 0:
      return True
    if l != 1: 
      return False
    gate = self.working_set.pop()
    if gate.type == Type.CHECKPOINT and gate.done:
      return True

    self.working_set.add(gate)
    return False

  
  def successors(self, costs: np.ndarray, neighbours: Dict[int, Set[int]]) -> Set["State"]:
    """
      Calculates all possible successor states to this state
    """
    successors = set()

    state = self._execute_gates(costs)
    if state is not None:
      if state.is_done():
        return { state }
      return state.successors(costs, neighbours)
    resolvables = [(g, g.can_be_resolved(self.resolved_gates)) for g in self.working_set]

    for gate, resolvable in resolvables:
      execution_distance = gate.execution_distance(costs, self.mapping)
      if resolvable:
        # insert bridge gates
        if gate.type == Type.CNOT: # works only for CNOT gates
          # execution_distance = gate.execution_distance(costs, self.mapping)
          if execution_distance == State.BRIDGE_DISTANCE: # bridges work only for a certain distance
            # using the provided architecture, only 1 bridge will ever be
            # possible, but we account for other architectures as well
            successors.update(self._generate_bridges(gate, neighbours))

      # even if the gate is not resolvabe, we still generate swap gates
      if gate.is_multi_qubit_gate():
        successors.update(self._generate_swaps(gate.q1, neighbours))
        successors.update(self._generate_swaps(gate.q2, neighbours))

    return successors


  def _execute_gates(self, costs: np.ndarray) -> "State":
    """
      Executes all gates, which can currently be executed
    """
    state = self
    for gate in state.working_set: # TODO check this
      executable = gate.can_be_executed(costs, state.mapping)
      resolvable = gate.can_be_resolved(state.resolved_gates)
      if executable and resolvable:
        state = state._execute_gate(gate)

    if state != self:
      return state
    return None


  def _execute_gate(self, gate: Gate) -> "State":
    """
      Executes a gate, returning the resulting state
    """
    working_set = self.working_set.copy()
    working_set.remove(gate)
    working_set.update(gate.children)

    resolved_set = self.resolved_gates.copy()
    resolved_set.add(gate)

    cost = self.cost + gate.cost()
    remaining_cost = self.remaining_cost - gate.cost()
    output = gate.to_logical(self.mapping)

    used_qubits = self.used_qubits.copy()
    if gate.type == Type.CNOT or gate.type == Type.SWAP:
      # a gate only uses qubits if it is a cnot or a swap gate, all other gates
      # (which use only 1 qubit), can be assigned other qubits
      used_qubits.add(output.q1)
      used_qubits.add(output.q2)

    checkpoint = self.checkpoint
    if gate is self.checkpoint:
      checkpoint = checkpoint.next

    return State(working_set, resolved_set, self.mapping, cost, remaining_cost, output, self, used_qubits, checkpoint)

  
  def _generate_bridges(self, gate: Gate, neighbours: Dict[int, Set[int]]) -> Set["State"]:
    """
      Executes the current CNOT gate by applying a bride operation.
      Using the brooklyn architecture, only 1 neighbour can act as a bridge,
      but we account for other architecture as well, which would maybe allow
      for more than 1 neighbour to act as a bridge.
    """
    p1, p2 = self.mapping.logical_to_physical(gate.q1, gate.q2)
    neighbours1 = neighbours[p1]
    neighbours2 = neighbours[p2]
    intersecton = neighbours1.intersection(neighbours2)

    # we now create dummy states to represent each of the CNOT outputs
    bridges = set()
    for pi in intersecton:
      # pretty sure bridges work like this, not the other way round
      # even if it's the other way round, the performance would be identical
      g1 = Gate(Type.CNOT, None, None, pi, p2)
      s1 = State(None, None, self.mapping, self.cost + 10, self.remaining_cost, g1, self, None, self.checkpoint)
      g2 = Gate(Type.CNOT, None, None, p1, pi)
      s2 = State(None, None, self.mapping, self.cost + 20, self.remaining_cost, g2, s1, None, self.checkpoint)
      g3 = Gate(Type.CNOT, None, None, pi, p2)
      s3 = State(None, None, self.mapping, self.cost + 30, self.remaining_cost, g3, s2, None, self.checkpoint)
      
      working_set = self.working_set.copy()
      working_set.remove(gate)
      working_set.update(gate.children)

      resolved_set = self.resolved_gates.copy()
      resolved_set.add(gate)

      used_gates = self.used_qubits.copy()
      used_gates.add(p1)
      used_gates.add(p2)
      used_gates.add(pi)
      
      g4 = Gate(Type.CNOT, gate.children, gate.parents, p1, pi)
      s4 = State(working_set, resolved_set, self.mapping, self.cost + 40, self.remaining_cost - Type.CNOT.cost, g4, s3, used_gates, self.checkpoint)
      bridges.add(s4)

    return bridges


  def _generate_swaps(self, qubit: int, neighbours: Dict[int, Set[int]]) -> Set["State"]:
    """
      Generates swaps using the qubit provided.
      In case the qubts, upon which the swaps operate, have not been used,
      this method just updates the mapping and does not emit a swap gate.
    """
    swaps = set()
    p, _ = self.mapping.logical_to_physical(qubit)
    for pn in neighbours[p]:
      ln, _ = self.mapping.physical_to_logical(pn)
      mapping = self.mapping.swap(qubit, ln)
      
      working_set = self.working_set.copy()
      resolved_set = self.resolved_gates.copy()
      cost = self.cost + Type.SWAP.cost

      if p in self.used_qubits or pn in self.used_qubits:
        output = Gate(Type.SWAP, None, None, p, pn)
        used_qubits = self.used_qubits.copy()
        used_qubits.add(p)
        used_qubits.add(pn)
        swaps.add(
          State(working_set, resolved_set, mapping, cost, self.remaining_cost, output, self, used_qubits, self.checkpoint)
        )
      else:
        # we back propagate all changes later on
        # we also do not add p and pn to the used gates, as we remove these swap gates later
        output = Gate(Type.FREE_SWAP, None, None, p, pn)
        swaps.add(
          State(working_set, resolved_set, mapping, self.cost, self.remaining_cost, output, self, self.used_qubits, self.checkpoint)
        )

    return swaps


  def __eq__(self, __o) -> bool:
    if __o is None or not isinstance(__o, State):
      return False

    return self.cost == __o.cost \
        and self.remaining_cost == __o.remaining_cost \
        and self.mapping == __o.mapping \
        and self.working_set == __o.working_set


  def __hash__(self) -> int:
    return self.cost ^ self.remaining_cost ^ self.mapping.__hash__()

  
  def __lt__(self, __o: "State") -> bool:
    """
      We prioritze a deeper depth (greedy)
    """
    return self.checkpoint.depth > __o.checkpoint.depth


      
      

