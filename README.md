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


The state set of the ``Summarized'' model (when all ``error states'' are treated as a single state) is the state set of the summarized autonomous system.
