"""
Simple test for HiGHS API.
"""
import highspy
import numpy as np

# Create a simple model: max 2x + 3y s.t. x + y <= 10, x >= 0, y >= 0
h = highspy.Highs()

# Check which methods are available
print("Available methods:")
for method in dir(h):
    if not method.startswith('_'):
        print(f"  - {method}")

print("\nCreating a simple model...")

# Set objective sense to maximize
h.changeObjectiveSense(highspy.ObjSense.kMaximize)

# Add variables: addCol(lower, upper, cost, coltype=None)
print("\nAdding variables...")
h.addCol(0.0, highspy.kHighsInf, 2.0)  # x
h.addCol(0.0, highspy.kHighsInf, 3.0)  # y

# Add constraint: addRow(lower, upper, indices, values)
print("\nAdding constraint...")
h.addRow(0.0, 10.0, [0, 1], [1.0, 1.0])

# Solve the model
print("\nSolving model...")
h.run()

print(f"Status: {h.getModelStatus()}")
print(f"Objective: {h.getObjectiveValue()}")
print(f"Solution: {h.getSolution()}")

# Try with integer variables
print("\n\nCreating an integer model...")
h2 = highspy.Highs()
h2.changeObjectiveSense(highspy.ObjSense.kMaximize)

# Add integer variables
print("\nAdding integer variables...")

# Need to create an empty model first
col_cost = np.array([2.0, 3.0], dtype=np.double)
col_lower = np.array([0.0, 0.0], dtype=np.double)
col_upper = np.array([highspy.kHighsInf, highspy.kHighsInf], dtype=np.double)
row_lower = np.array([0.0], dtype=np.double)
row_upper = np.array([10.0], dtype=np.double)
a_start = np.array([0, 2], dtype=np.int32)
a_index = np.array([0, 0], dtype=np.int32)
a_value = np.array([1.0, 1.0], dtype=np.double)

h2.passModel(len(col_cost), len(row_lower), 0, 0, 0, 0, 0,
             highspy.ObjSense.kMaximize, highspy.ObjOffset.kZero,
             col_cost, col_lower, col_upper,
             row_lower, row_upper,
             a_start, a_index, a_value,
             [None] * len(col_cost), [None] * len(row_lower))

# Set variables to integer
print("\nSetting variables to integer...")
for i in range(len(col_cost)):
    h2.changeColIntegrality(i, highspy.HighsVarType.kInteger)

# Solve the model
print("\nSolving model...")
h2.run()

print(f"Status: {h2.getModelStatus()}")
print(f"Objective: {h2.getObjectiveValue()}")
print(f"Solution: {h2.getSolution()}") 