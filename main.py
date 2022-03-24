import argparse
import time

from mapper.mapper import map
from mapper.qasm.input import get_coupling_map


def main(args: argparse.Namespace):
  start = time.time()
  coupling_map = get_coupling_map() # hardcoded, can of course be arbitrary
  info = map(args.file, args.output, coupling_map, args.checkpoint_offset, args.checkpoint_look_ahead)
  end = time.time()
  if args.verbose:
    print(f"Succesfully mapped circuit {args.file}")
    print(f"Used {info.swaps} swap gates")
    print(f"Used {info.free_swaps} free swaps (i.e. reordering of qubits)")
    print("Circuit uses the following initial mapping: (qubits which are not listed are mapped to themselves)")
    print(f"\t{info.initial_mapping}")
    print(f"Mapping took {(end - start):.3f}s")
    print(f"Circuit costs in total {info.cost}")


def setup_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser()
  parser.add_argument("file", help="Circuit file")
  parser.add_argument("--output", "-o", help="Output file", default="output.qasm")
  parser.add_argument("--checkpoint-offset", help="Offset of checkpoints", default=3, type=int)
  parser.add_argument("--checkpoint-look-ahead", help="Amount of checkpoints to look ahead", default=2, type=int)
  parser.add_argument("--verbose", "-v", help="Print additional infos", default=False, action="store_true")
  return parser


if __name__ == "__main__":
  parser = setup_parser()
  args = parser.parse_args()
  main(args)