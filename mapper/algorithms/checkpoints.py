from typing import Set
from queue import PriorityQueue

from mapper.gate.gate import Gate
from mapper.gate.checkpoint import Checkpoint


def add_checkpoints(working_set: Set[Gate], checkpoint_offset: int) -> Gate:
  """
    Adds checkpoint gates every checkpoint_depth depth level.
    They are used to break the circuit into manageable parts
  """
  pq = PriorityQueue()
  checkpoints = dict()
  visited = set()

  checkpoint: Checkpoint = checkpoints.setdefault(0, Checkpoint())

  for gate in working_set:
    checkpoint.children.add(gate)
    gate.parents.add(checkpoint)
    pq.put_nowait((gate.depth, gate, ))

  while not pq.empty():
    curr_tuple = pq.get_nowait()
    current: Gate = curr_tuple[1]

    if current in visited:
      continue

    visited.add(current)   

    next_checkpoint_depth = ((current.depth // checkpoint_offset) + 1) * checkpoint_offset
    prev_checkpoint_depth = (current.depth // checkpoint_offset) * checkpoint_offset

    checkpoint: Checkpoint = checkpoints.setdefault(next_checkpoint_depth, Checkpoint())
    prev_cp: Checkpoint = checkpoints.setdefault(prev_checkpoint_depth, Checkpoint())
    
    prev_cp.next = checkpoint
    checkpoint.prev = prev_cp
    checkpoint.depth = next_checkpoint_depth
    prev_cp.gates.add(current)

    n_children = set()
    for child in current.children:
      pq.put_nowait((child.depth, child, ))
      if child.depth >= next_checkpoint_depth:
        cp_depth = ((child.depth // checkpoint_offset)) * checkpoint_offset
        cp: Checkpoint = checkpoints.setdefault(cp_depth, Checkpoint())
        cp.depth = cp_depth
        cp.children.add(child)

        child.parents.remove(current)
        child.parents.add(cp)

        n_children.add(checkpoint) # adds the checkpoint as a child to the current gate
        checkpoint.parents.add(current)
      else:
        n_children.add(child)
    current.children = n_children

  last_cps = list(filter(lambda cp: cp.next is None, checkpoints.values()))
  
  if len(last_cps) != 1:
    raise ValueError("Failed to map")
  
  last_cp = last_cps[0]
  last_cp.done = True
  
  return checkpoints[0]
