"""
Minimal test for HiGHS API.
"""
import highspy

# Create a simple model
h = highspy.Highs()
print("Creating a simple model...")

# Create variable and print its index
idx = h.addCol()
print(f"Added variable with index: {idx}")

# Set variable bounds and cost
h.changeColBounds(idx, 0.0, 10.0)
print("Set variable bounds: [0, 10]")

h.changeColCost(idx, 2.0)
print("Set variable cost: 2.0")

# Set variable type to integer
h.changeColIntegrality(idx, highspy.HighsVarType.kInteger)
print("Set variable type to integer")

# Add constraint
h.addRow(0.0, 5.0, [idx], [1.0])
print("Added constraint: 0 <= x <= 5")

# Set objective sense to maximize
h.changeObjectiveSense(highspy.ObjSense.kMaximize)
print("Set objective to maximize")

# Solve the model
print("\nSolving model...")
h.run()

print(f"Status: {h.getModelStatus()}")
print(f"Objective: {h.getObjectiveValue()}")
print(f"Solution: {h.getSolution()}") 