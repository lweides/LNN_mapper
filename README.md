# LNN Mapper

## Environment

This section assumes the use of Windows and python version `3.8`.
- Create a virtual environment with `python -m venv venv`
- Activate it with `. venv/Scripts/activate`
- Install the requirements with `pip install -r requirements.txt`

## Usage

The mapper can either be used as a package or as a script.

### Usage as package

Import the `map` function from `mapper.mapper`:
```python
  from mapper.mapper import map

  info = map(
    "path/to/circuit.qasm",
    "path/to/output.qasm",
    [[0, 1], [1, 0], [1, 2], [2, 1]], # coupling map
    checkpoint_offset, # defaults to 3
    checkpoint_look_ahead # defaults to 2
  )
```
This will read the circuit from `"path/to/circuit.qasm"`, map it to the given `coupling_map` and write the circuit to `"path/to/output.qasm"`. The `info` object contains information on the mapping, e.g. total mapped cost. Varying the parameters `checkpoint_offset` and `checkpoint_look_ahead` has a big influence on the runtime and performance of the mapper. Use with caution!

You can of course also use all the internals for a more fine granular control over the mapping process.

### Usage as script

The command to map a circuit is `python main.py path/to/circuit.qasm`. For more information use `python main.py --help`.

## Benchmark

A script to execute a given benchmark is also included. Can be executed using `python benchmark.py path/to/benchmark/circuits_folder path/to/output_folder --result results.csv`

Keep in mind that the results can differ slightly between different runs because of some involved randomness. The divitations should be negligible.

## Inner workings

The mapping is based on an A* algorithm. A single state in the search space is composed of the currently considered gates (`working_set`), the current mapping of the logical to the physical qubits (`mapping`), a `checkpoint` gate and the cost of all gates until this state (`cost`).

The algorithm does not process the gates one by one, but uses the `DAG` of dependencies of the individual gates. Furthermore, the `DAG` is "squeezed" to a single gate, a so called `checkpoint` gate. All edges of the `DAG`, which would cross the height of the `checkpoint` gate (given a planar visualization) are redirected into the `checkpoint` gate. This technique helps to reduce the search space. We also don't allow states to be processed by the A* algorithm, if the `depth` of the `checkpoint` gate is shallower than the highest processed `depth` so far. This also greatly reduced the search space.

As heuristic, only a simple `swap` counting strategy is used. We don't consider all remaining gates, but only ones which lie a couple of `checkpoints` ahead. This heuristic is in general **not** admissible.

We further employ the concept of `free swaps`. If qubits would need to be swapped, for example to execute a `cnot` gate, but those 2 qubits have not been used before (and also all qubits, which lie in between them), we create a `free swap` chain. Essentially `swap` gates, but with `0` cost. In the post processing of the mapping, we need to account for them and backpropagate these `free swaps`.

## Performance

The mapper performs better than a primitive approach, which considers one gate at a time and inserts `swap` gates to satisfy the `cnot` constraints. It has also a rather fast execution speed, taking ~1.33s to map the `adder-16.qasm` circuit. This execution time is, of course, subject to the executing hardware.

## Shortcomings

This mapper does as of now **not** compute an initial mapping for the qubits. Some papers have suggested that the initial mapping can have a big impact on mapping performance. However, due to the concept of `free swaps`, some rearanging of qubits does occur.

The algorithm could also be parallelized, but (1) because of the fast runtime, it felt kind of useless and (2) due to Pythons `GIL`, CPU intensive work cannot be multithread in Python.
