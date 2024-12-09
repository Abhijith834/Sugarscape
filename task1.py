import random
import csv
import matplotlib.pyplot as plt

# ------------------------
# TASK 1: Simulation Setup
# ------------------------

GRID_SIZE = 20
NUM_AGENTS = 20
INITIAL_ENERGY = 10
SIGHT_RANGE = 3
TURNS = 500

# Initialize capacity and sugar arrays
capacity = [[x + y for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
sugar = [[capacity[x][y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

# Set up agents as dictionaries
agents = []

# Wrap-around function
def wrap(n):
    return n % GRID_SIZE

# Place agents at random distinct locations
all_positions = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
random.shuffle(all_positions)
for _ in range(NUM_AGENTS):
    x, y = all_positions.pop()
    agents.append({"x": x, "y": y, "energy": INITIAL_ENERGY, "sight": SIGHT_RANGE})

def sugar_growth_phase():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if sugar[x][y] < capacity[x][y]:
                sugar[x][y] += 1

def visible_cells(agent):
    # Cells visible to the agent: itself and up to 'sight' steps in the four directions
    x, y = agent["x"], agent["y"]
    cells = [(x, y)]
    # Up
    for i in range(1, agent["sight"] + 1):
        cells.append((x, wrap(y - i)))
    # Down
    for i in range(1, agent["sight"] + 1):
        cells.append((x, wrap(y + i)))
    # Left
    for i in range(1, agent["sight"] + 1):
        cells.append((wrap(x - i), y))
    # Right
    for i in range(1, agent["sight"] + 1):
        cells.append((wrap(x + i), y))
    return cells

def agent_movement_phase():
    random.shuffle(agents)
    occupied = {(a["x"], a["y"]) for a in agents}

    for agent in agents:
        vis_cells = visible_cells(agent)

        # Agent can’t move into a cell with another agent, except its own cell
        free_cells = []
        for (cx, cy) in vis_cells:
            if (cx, cy) == (agent["x"], agent["y"]) or (cx, cy) not in occupied:
                free_cells.append((cx, cy))

        # Choose the cell with the max sugar
        max_sug = max(sugar[cx][cy] for cx, cy in free_cells)
        candidates = [(cx, cy) for (cx, cy) in free_cells if sugar[cx][cy] == max_sug]
        chosen = random.choice(candidates)

        # Move agent
        old_pos = (agent["x"], agent["y"])
        occupied.remove(old_pos)
        occupied.add(chosen)
        agent["x"], agent["y"] = chosen[0], chosen[1]

        # Consume sugar
        agent["energy"] += sugar[chosen[0]][chosen[1]]
        sugar[chosen[0]][chosen[1]] = 0

def consumption_phase():
    survivors = []
    for agent in agents:
        agent["energy"] -= 1
        if agent["energy"] > 0:
            survivors.append(agent)
    return survivors

# ------------------------
# TASK 2: Data Collection
# ------------------------

# CSV files:
# 1. total_energy.csv: total energy per turn
# 2. agent_positions.csv: agent positions at turns 1, 50, 500
# 3. sugar_levels.csv: sugar values at turns 1, 50, 500

total_energy_file = open('total_energy.csv', 'w', newline='')
total_energy_writer = csv.writer(total_energy_file)
total_energy_writer.writerow(["turn", "total_energy"])

agent_positions_file = open('agent_positions.csv', 'w', newline='')
agent_positions_writer = csv.writer(agent_positions_file)
agent_positions_writer.writerow(["turn", "agent_id", "x", "y", "energy"])

sugar_levels_file = open('sugar_levels.csv', 'w', newline='')
sugar_levels_writer = csv.writer(sugar_levels_file)

def record_agent_positions(turn):
    for i, a in enumerate(agents):
        agent_positions_writer.writerow([turn, i, a["x"], a["y"], a["energy"]])

def record_sugar_levels(turn):
    for y in range(GRID_SIZE):
        row_data = [turn]
        for x in range(GRID_SIZE):
            row_data.append(sugar[x][y])
        sugar_levels_writer.writerow(row_data)

# Run the simulation
for turn in range(1, TURNS + 1):
    sugar_growth_phase()
    agent_movement_phase()
    agents = consumption_phase()

    # Record total energy every turn
    total_energy = sum(a["energy"] for a in agents)
    total_energy_writer.writerow([turn, total_energy])

    # Record agent positions and sugar levels at specified turns
    if turn in [1, 50, 500]:
        record_agent_positions(turn)
        record_sugar_levels(turn)

total_energy_file.close()
agent_positions_file.close()
sugar_levels_file.close()

# Example: Reading back total energy and plotting
turns = []
energies = []
with open('total_energy.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        turns.append(int(row[0]))
        energies.append(int(row[1]))

plt.figure()
plt.plot(turns, energies, linestyle='-')
plt.xlabel("Turn")
plt.ylabel("Total Energy of All Agents")
plt.title("Total Agent Energy Over Time")
plt.show()
