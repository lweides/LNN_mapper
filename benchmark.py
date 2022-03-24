import argparse
import os
import csv
from typing import List

from mapper.mapper import map
from mapper.qasm.input import get_coupling_map


def main(args: argparse.Namespace):
  if not os.path.isdir(args.output):
    os.mkdir(args.output)

  coupling_map = get_coupling_map()
  results = dict()

  for file in os.listdir(args.folder):
    if file.endswith(".qasm"):
      cost = map_file(file, args.folder, args.output, coupling_map, 3, 2)
      results[file] = cost
      print(f"{file} done, cost: {cost}")

  with open(args.result, "w", newline="") as f:
    writer = csv.DictWriter(f, ["filename", "cost"])
    writer.writeheader()
    for circuit, cost in results.items():
      writer.writerow({ "filename": circuit, "cost": cost })


def map_file(circuit_name: str, input_folder: str, output_folder: str, coupling_map: List[List[int]], checkpoint_offset: int, checkpoint_look_ahead: int) -> int:
  info = map(f"{input_folder}/{circuit_name}", f"{output_folder}/{circuit_name}", coupling_map, checkpoint_offset, checkpoint_look_ahead)
  return info.cost

def setup_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser()
  parser.add_argument("folder", help="Benchmark folder")
  parser.add_argument("output", help="Output folder")
  parser.add_argument("--result", "-r", help="Result csv file name", default="results.csv")
  return parser


if __name__ == "__main__":
  parser = setup_parser()
  args = parser.parse_args()
  main(args)