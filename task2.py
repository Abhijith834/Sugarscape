import csv
import numpy as np
import matplotlib.pyplot as plt

GRID_SIZE = 20

# Read the energy data
turns = []
energies = []
with open("task1_energy_data.csv","r") as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        t = int(row[0])
        E = float(row[1])
        turns.append(t)
        energies.append(E)

# Plot the total energy over time
plt.figure(figsize=(8,6))
plt.plot(turns, energies, label="Total Energy")
plt.xlabel("Turn")
plt.ylabel("Total Energy in Living Agents")
plt.title("Total Agent Energy Over Time (Task 1)")
plt.legend()
plt.savefig("task2_total_energy_plot.png")
plt.close()

# Read agent positions
positions_by_turn = {1:[], 50:[], 500:[]}
with open("task1_agent_positions.csv","r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        t = int(row[0])
        if t in positions_by_turn:
            x = int(row[1])
            y = int(row[2])
            positions_by_turn[t].append((x,y))

# Read sugar levels
sugar_by_turn = {1:np.zeros((GRID_SIZE,GRID_SIZE)),
                 50:np.zeros((GRID_SIZE,GRID_SIZE)),
                 500:np.zeros((GRID_SIZE,GRID_SIZE))}

with open("task1_sugar_levels.csv","r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        t = int(row[0])
        if t in sugar_by_turn:
            x = int(row[1])
            y = int(row[2])
            s_val = float(row[3])
            sugar_by_turn[t][x,y] = s_val

# Visualizations for turns 1, 50, 500
for t in [1, 50, 500]:
    fig, ax = plt.subplots(figsize=(6,6))
    # Show sugar as a heatmap
    im = ax.imshow(sugar_by_turn[t].T, origin="lower", cmap="YlOrBr", interpolation="nearest")
    plt.colorbar(im, ax=ax, label="Sugar level")
    
    # Plot agent positions
    xs = [pos[0] for pos in positions_by_turn[t]]
    ys = [pos[1] for pos in positions_by_turn[t]]
    ax.scatter(xs, ys, c='red', edgecolors='black', label='Agents')

    ax.set_title(f"Turn {t} - Agents (red) and Sugar Distribution")
    ax.set_xlim(-0.5, GRID_SIZE-0.5)
    ax.set_ylim(-0.5, GRID_SIZE-0.5)
    ax.set_xticks(range(0,GRID_SIZE,5))
    ax.set_yticks(range(0,GRID_SIZE,5))
    plt.legend()
    plt.savefig(f"task2_visualization_turn_{t}.png")
    plt.close()

print("Task 2 analysis completed. Plots saved as PNG files.")
