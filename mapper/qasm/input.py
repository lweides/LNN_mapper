from typing import Dict, List, Set, Tuple

from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.test.mock.backends import FakeBrooklyn

from mapper.gate.type import Type
from mapper.gate.gate import Gate


def read_gates(file_name: str) -> Tuple[Set[Gate], List[Gate], List[ClassicalRegister]]:
  """
    Reads the given .qasm file, returning a working set,
    the gates of the quantum registers and the classical registers
  """
  qc = QuantumCircuit.from_qasm_file(file_name)
  offsets = _get_qreg_offsets(qc)
  working_set, gates = _map_gates(qc, offsets)
  return working_set, gates, qc.cregs


def _map_gates(qc: QuantumCircuit, offsets: Dict[str, int]) -> Tuple[Set[Gate], List[Gate]]:
  """
    Returns the initial working set, which are all gates without dependencies
  """
  working_set = set()
  last_gate = dict() # maps qubits to the last gates which used them
  gates = []

  for instr in qc.data:
    q1 = instr[1][0].index + offsets[instr[1][0].register.name]
    q2 = -1
    name = instr[0].name
    params = instr[0].params
    parents = set()
    
    if q1 in last_gate:
      parents.add(last_gate[q1])

    if name == Type.CNOT.value or name == Type.SWAP.value:
      q2 = instr[1][1].index + offsets[instr[1][1].register.name]
      if q2 in last_gate:
        parents.add(last_gate[q2])

    elif name == Type.MEASURE.value:
      q2 = instr[2][0].index

    elif name == Type.BARRIER.value:
      q2 = [c.index + offsets[c.register.name] for c in instr[1]]
      for d in q2:
        if d in last_gate:
          parents.add(last_gate[d])

    elif name == Type.X.value or name == Type.ROTATE_Z.value or name == Type.SQRT.value:
      # noting to do
      pass

    else:
      raise ValueError(f"Encountered unknown gate: {name}")

    gate = Gate(Type.from_name(name), set(), parents, q1, q2, params)
    gates.append(gate)

    last_gate[q1] = gate
    if name == Type.CNOT.value or name == Type.SWAP.value:
      last_gate[q2] = gate
    
    elif name == Type.BARRIER.value:
      for qubit in q2:
        last_gate[qubit] = gate

    for parent in parents:
      parent.children.add(gate)

    if len(parents) == 0:
      working_set.add(gate)

  return working_set, gates

def _get_qreg_offsets(qc: QuantumCircuit) -> Dict[str, int]:
  """
    Computes the offset for each QuantumRegister
  """
  offsets = {}
  qubit_count = 0

  for qreg in qc.qregs:
    offsets[qreg.name] = qubit_count
    qubit_count += qreg.size

  return offsets


def get_coupling_map():
  """
    Returns the coupling map to use, which at the moment
    is just a Fake Brooklyn one.
  """
  return FakeBrooklyn().configuration().coupling_map


def get_neighbours(coupling_map) -> Dict[int, Set[int]]:
  """
    Returns a map containing the neighbours of each qubit.
  """
  neighbours = {}
  for edge in coupling_map:
    if not edge[0] in neighbours:
      neighbours[edge[0]] = set()
    neighbours[edge[0]].add(edge[1])
  return neighbours