# Waffle Production Optimizer

A Python tool for optimizing waffle production planning using open-source optimization solvers.

## Overview

This tool helps to optimize waffle production by solving two key questions:

1. How to minimize overall production cost while meeting waffle demand
2. How to maximize waffle output for a given production schedule

The implementation uses a modular design with support for multiple optimization solvers, including PuLP (with various backends like CBC, GLPK) and Google OR-Tools.

## Features

- **Data Processing**: Load and validate input data from Excel files
- **Feasibility Checking**: Identify potential issues before optimization
- **Multiple Optimization Objectives**: Minimize cost or maximize output
- **Multiple Solvers**: Support for various optimization backends
- **Reporting**: Export detailed results to Excel for further analysis
- **Validation**: Verify solution feasibility and quality

## Mathematical Formulation

### Problem Overview

The Waffle Production Optimization model addresses the efficient allocation of waffle production across different pan types over a planning horizon (typically weeks). The model handles two key optimization objectives:

1. **Cost Minimization**: Determine the least costly production schedule that satisfies all waffle demand.
2. **Output Maximization**: Determine the production schedule that maximizes the total number of waffles produced.

### Indices and Sets

- $w \in W$: Set of waffle types
- $p \in P$: Set of pan types
- $t \in T$: Set of time periods (weeks)
- $A \subseteq W \times P$: Set of allowed combinations of waffle types and pan types

### Parameters

- $D_{wt}$: Demand for waffle type $w$ in week $t$ (in number of pans)
- $S_{pt}$: Supply of pan type $p$ available in week $t$
- $N_w$: Number of waffles of type $w$ that can be produced per pan
- $C_{wp}$: Cost per waffle for producing waffle type $w$ using pan type $p$
- $A_{wp}$: Binary parameter indicating whether waffle type $w$ can be produced using pan type $p$ (1 if allowed, 0 otherwise)

### Decision Variables

- $X_{wpt}$: Integer variable representing the number of pans of type $p$ used to produce waffle type $w$ in week $t$

### Objective Functions

#### 1. Cost Minimization

The objective is to minimize the total production cost:

$$\min Z_{cost} = \sum_{w \in W} \sum_{p \in P} \sum_{t \in T} C_{wp} \cdot N_w \cdot X_{wpt}$$

Where $C_{wp} \cdot N_w$ represents the total cost of using one pan of type $p$ to produce waffle type $w$.

#### 2. Output Maximization

The objective is to maximize the total number of waffles produced:

$$\max Z_{output} = \sum_{w \in W} \sum_{p \in P} \sum_{t \in T} N_w \cdot X_{wpt}$$

### Constraints

#### 1. Demand Satisfaction

For each waffle type and each week, the number of pans used must exactly meet the demand:

$$\sum_{p \in P} X_{wpt} = D_{wt} \quad \forall w \in W, \forall t \in T$$

#### 2. Supply Limitation with Cumulative Tracking

A key feature of this model is the cumulative tracking of pan supply. Unused pans from earlier weeks can be used in later weeks. For each pan type and each week, the cumulative usage up to and including that week cannot exceed the cumulative supply:

$$\sum_{w \in W} \sum_{t' \leq t} X_{wpt'} \leq \sum_{t' \leq t} S_{pt'} \quad \forall p \in P, \forall t \in T$$

Where $t' \leq t$ represents all weeks up to and including week $t$.

#### 3. Allowed Combinations

Waffle types can only be produced using compatible pan types:

$$X_{wpt} = 0 \quad \forall (w,p) \notin A, \forall t \in T$$

This constraint is implicitly enforced by only defining variables for allowed combinations.

#### 4. Non-negativity and Integrality

All decision variables must be non-negative integers:

$$X_{wpt} \in \mathbb{Z}^+ \cup \{0\} \quad \forall w \in W, \forall p \in P, \forall t \in T$$

### Model Variants

#### Allowing Production to Exceed Demand

In the output maximization variant, the model can be adjusted to allow production to exceed demand, changing the demand satisfaction constraint to:

$$\sum_{p \in P} X_{wpt} \geq D_{wt} \quad \forall w \in W, \forall t \in T$$

This variant is controlled by the `limit_to_demand` parameter in the code.

### Example

Consider a simple scenario with:
- Two waffle types: Standard and Deluxe
- Two pan types: Regular and Premium
- Two weeks in the planning horizon

**Parameters:**
- Demand ($D_{wt}$):
  - Week 1: 100 pans of Standard, 50 pans of Deluxe
  - Week 2: 150 pans of Standard, 75 pans of Deluxe
- Supply ($S_{pt}$):
  - Week 1: 120 Regular pans, 80 Premium pans
  - Week 2: 100 Regular pans, 90 Premium pans
- Waffles per pan ($N_w$):
  - Standard: 10 waffles/pan
  - Deluxe: 8 waffles/pan
- Cost per waffle ($C_{wp}$):
  - Standard on Regular: $0.50
  - Standard on Premium: $0.60
  - Deluxe on Regular: $0.70
  - Deluxe on Premium: $0.65
- All combinations are allowed ($A_{wp} = 1$ for all $w,p$)

**Decision Variables:**
- Week 1:
  - $X_{Standard,Regular,1}$: Number of Regular pans used for Standard waffles in Week 1
  - $X_{Standard,Premium,1}$: Number of Premium pans used for Standard waffles in Week 1
  - $X_{Deluxe,Regular,1}$: Number of Regular pans used for Deluxe waffles in Week 1
  - $X_{Deluxe,Premium,1}$: Number of Premium pans used for Deluxe waffles in Week 1
- Week 2: Similar variables for Week 2

**Constraints:**
1. Demand satisfaction:
   - $X_{Standard,Regular,1} + X_{Standard,Premium,1} = 100$
   - $X_{Deluxe,Regular,1} + X_{Deluxe,Premium,1} = 50$
   - $X_{Standard,Regular,2} + X_{Standard,Premium,2} = 150$
   - $X_{Deluxe,Regular,2} + X_{Deluxe,Premium,2} = 75$

2. Cumulative supply limitation:
   - Week 1, Regular pans: $X_{Standard,Regular,1} + X_{Deluxe,Regular,1} \leq 120$
   - Week 1, Premium pans: $X_{Standard,Premium,1} + X_{Deluxe,Premium,1} \leq 80$
   - Week 2, Regular pans: $X_{Standard,Regular,1} + X_{Deluxe,Regular,1} + X_{Standard,Regular,2} + X_{Deluxe,Regular,2} \leq 120 + 100$
   - Week 2, Premium pans: $X_{Standard,Premium,1} + X_{Deluxe,Premium,1} + X_{Standard,Premium,2} + X_{Deluxe,Premium,2} \leq 80 + 90$

**Objective (Cost Minimization):**
$$\min Z_{cost} = 0.50 \cdot 10 \cdot X_{Standard,Regular,1} + 0.60 \cdot 10 \cdot X_{Standard,Premium,1} + \ldots$$

The optimal solution will assign values to all variables that minimize total cost while satisfying all constraints.

### Computational Considerations

The optimization model is implemented in Python using industry-standard solvers like OR-Tools (Google) and various PuLP backends (CBC, GLPK, etc.). The implementation:

1. Dynamically builds the model based on the input data
2. Sets an appropriate time limit and optimality gap tolerance
3. Provides detailed solution information, including:
   - Optimality status
   - Objective value
   - Solution time
   - Solution quality metrics

For large problems, the solver may return a good feasible solution rather than the proven optimal solution if the time limit is reached before proving optimality.

## Usage

### Command Line

Run the main script with arguments to control the optimization:

```bash
python main.py --objective cost --solver cbc --time-limit 60 --output data/output/solution.xlsx
```

Available arguments:
- `--objective`: Choose between `cost` (minimize cost) or `output` (maximize output)
- `--solver`: Solver to use (`cbc`, `glpk`, `pulp_highs`, `ortools`, etc.)
- `--time-limit`: Time limit for optimization in seconds
- `--gap`: Optimality gap tolerance
- `--debug`: Enable debug output
- Data file paths can be specified with `--demand`, `--supply`, `--cost`, `--wpp`, `--combinations`

## License

This project is open-source and available under the MIT License. 