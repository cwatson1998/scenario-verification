## Reproducing Results
The file analysis/sequential_analysis.ipynb reproduces all the values found in Table 2 of the submission.

The files analysis/invariant_preconditions_rule_2.ipynb and analysis/invariant_preconditions_rule_3.ipynb find the invariant preconditions for applying Rule 2 and Rule 3, respectively.

## PRISM models
This repository contains PRISM files that model the behavior of two autonomous systems (an airplane that must stay on a taxiway, and a model race car that must navigate a track).
Each PRISM file has a variable ``scenario'' that determines which scenario is currently active.
The PRISM models themselves do not model transitions between scenarios. Instead, we first /summarize/ each scenario and represent it explicitly as a stochastic matrix.
The scenarios we consider are:

- TaxiNet:
  -- (scenario=0): Bright light.
  -- (scenario=1): Dark light.
- F1Tenth:
  -- (scenario=0): Left turn.
  -- (scenario=1): Right turn.
  -- (scenario=2): Straight track segment.

For each 

There are two PRISM .pm files for each autonomous system.
1. Summarized. Each step in this DTMC represents the complete execution of a scenario.
2. Unsummarized. Used internally for summary generation. The current value of the ``timer'' variable represents the number of (autonomous system) timesteps spent in the current scenario.
There is also a serialized file called '..._SUMMARIES.npz'. This is a .npz file that contains an explicit representation of the summary as the A matrix and b vector. These are created and de-serialized using functionality in analysis/explicit_summaries.py and form the basis of our analyses. They are equivalent to the stochastic matrix of the "Summarized" prism file.




The state set of the ``Summarized'' model (when all ``error states'' are treated as a single state) is the state set of the summarized autonomous system.

## Installation
We ran our experiments using Python 3 with the packages in requirements.txt installed. In order to set up your python environment, you can make a new Python environment that contains Python 3.10 and Pip (using e.g. conda) and then run

```bash
pip install -r requirements.txt
```

### Gurobi Installation

Gurobi requires a valid license to work. Follow these steps to install and activate Gurobi:

1. **Download and Install Gurobi**  
   Visit the [Gurobi website](https://www.gurobi.com/downloads/) and download the appropriate version for your system. Follow the installation instructions provided.

2. **Activate Your License**  
   After installing Gurobi, activate your license by running:
   ```bash
   grbgetkey <your-license-key>
   ```
   Replace `<your-license-key>` with your actual Gurobi license key.

3. **Verify Installation**  
   Ensure Gurobi is available in your Python environment by running:
   ```bash
   python -c "import gurobipy; print(gurobipy.__version__)"
   ```

### Troubleshooting

If you encounter issues with `z3-solver`, install it manually with:

```bash
pip install z3-solver