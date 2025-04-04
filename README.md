# RUP-IC3: A Reusable, Unsat-Core-Guided Parallel Acceleration Framework for IC3

This project implements RUP-IC3, an enhanced IC3 model checking framework integrating three novel acceleration strategies:
- **R**: Bad state reuse across verification frontiers
- **U**: Unsat-core guided clause generalization 
- **P**: Parallel optimal clause order exploration

## Experimental Platform

### Hardware & Software Environment
- **CPU**: 48-core Intel Xeon (2.1GHz) with 96GB RAM
- **OS**: Ubuntu 20.04.3 LTS (64-bit)
- **Dependencies**:
  - OCaml 4.11.0
  - Z3 Solver 4.8.7
  - Python 3.8.10

## Project Structure

### Benchmark DatasetsThe benchmarks used in this project are sourced from the public repository at [kind2-mc/kind2-benchmarks](https://github.com/kind2-mc/kind2-benchmarks).

| Dataset         | Path Specification File              | Models |
|----------------|---------------------------------------|--------|
| l1l2 Benchmarks | `bin/path/l1l2_513_path.csv`          | 513    |
| Main Benchmarks | `bin/path/1719_path.csv`              | 1,719  |


### Executables
| Directory      | Implementations                                                                 |
|----------------|---------------------------------------------------------------------------------|
| `bin/l12`      | O-IC3_l1l2, R-IC3_l1l2, U-IC3_l1l2, RU-IC3_l1l2                                    |
| `bin/`         | O-IC3 (Baseline), P-IC3 (Parallel), RUP-IC3 (Full implementation)              |

### Scripts
| Directory      | Scripts                                                                         |
|----------------|---------------------------------------------------------------------------------|
| `scripts/l12`  | l1l2 dataset runners:<br>• `base_run_l1l2.py`<br>• `reuse_run_l1l2.py`<br>• `unsatcore_run_l1l2.py` <br>• `reuse_and_unsatcore_run_l1l2.py` |
| `scripts/`     | main dataset runners:<br>• `base_run_1719.py`<br>• `3thread_run_1719.py`<br>• `3in1_run.py` |

### Results
| Dataset         | Result Files                                                                 |
|-----------------|------------------------------------------------------------------------------|
| l1l2 Benchmarks | `O-IC3_l1l2.csv`, `R-IC3_l1l2.csv`, `U-IC3_l1l2.csv`, `RU-IC3_l1l2.csv`          |
| main Benchmarks | `O-IC3_1719.csv`, `P-IC3_1719.csv`, `RUP-IC3_513.csv`, `RUP-IC3_1719.csv`    |

## Getting Started

### Execution Workflow
1. Navigate to scripts directory:
   ```bash
   cd bin/scripts/
2. Run batch execution script:
    ```bash
    python3 batch_run.py