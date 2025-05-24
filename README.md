
#  Stake Crash Streak Analyzer and Simulator

This repository provides two powerful Python Tkinter-based GUI tools for analyzing and simulating crash multipliers from Stake's crash game. The tools help users identify patterns, sub-2x streaks, and generate statistical insights based on real or simulated multiplier data.

---

## Project Structure

- `decomposeCrash.py`: **Sub-2x Streak Analyzer GUI**  
  Loads `.csv` files of crash multipliers, finds and visualizes sub-2.00x streaks, and summarizes their frequency and sequences interactively.

- `hash2csv.py`: **Crash Multiplier Simulator GUI**  
  Simulates crash multipliers using a given server seed (SHA256 hash chain), generates statistical summaries (mean, median, percentiles, gaps, etc.), and exports the result to a `.csv` file.

---

## Features

### `decomposeCrash.py` Highlights
- Detects all sub-2.00x streaks from historical `.csv` logs.
- Displays start indices and sequences for each streak length.
- Frequency breakdown for streak lengths ≥3.
- GUI auto-loads latest `.csv` from `crashLogs` folder.

### `hash2csv.py` Highlights
- Accepts a server seed hash and generates a hash chain to compute crash multipliers.
- Finds all sub-2.00x streaks and identifies the top 100 by length.
- Computes detailed statistics:
  - Multiplier distribution
  - Sub-2x streak length stats
  - Gap stats between top streaks
- Saves crash multipliers as a clean `.csv` log.
- Provides a summary popup for easy analysis.

---

## Initials:

### Prerequisites
- Python 3.7+
- `pandas`, `numpy` libraries

Install with:
```bash
pip install pandas numpy
```

---

## Folder Setup

Create a directory `crashLogs` in the following path to enable automatic CSV detection and saving:

```
C:\Users\admin\Desktop\crash\crashLogs
```

Ensure that both scripts run on the same machine or adjust the paths accordingly.

---

## Usage

### For `decomposeCrash.py`:
1. Run the script:
   ```bash
   python decomposeCrash.py
   ```
2. Load a `.csv` crash log file or let the script auto-detect the latest one.
3. Explore the streak list and view details in the GUI.

### For `hash2csv.py`:
1. Run the script:
   ```bash
   python hash2csv.py
   ```
2. Enter a valid 64-character server seed hash.
3. Set the number of simulations (e.g., 10000).
4. Optionally check the box for `stake.us` mode.
5. Click `Run Simulation` to generate and analyze crash multipliers.

---

## Output

- `.csv` files saved in `crashLogs` contain only crash multipliers.
- A popup shows comprehensive analysis for each run.

---

## Notes

- These tools are for educational or analytical purposes only.
- The server seed must be deterministic and pre-generated using SHA256 logic.

---

## License

This project is open-source and distributed under the MIT License.

---

## Acknowledgments

Inspired by patterns in Stake’s Crash game and designed to provide statistical insights into multiplier randomness and streak probabilities.
