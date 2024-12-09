import random
import csv
import matplotlib.pyplot as plt
import numpy as np

# ------------------------
# TASK 3: Evolution in Sugarscape Setup
# ------------------------

GRID_SIZE = 20
NUM_AGENTS = 20
INITIAL_ENERGY = 10
TURNS = 500

# Initialize capacity and sugar arrays
capacity = [[x + y for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
sugar = [[capacity[x][y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

# Agents have random sight between 2 and 5
agents = []

def wrap(n):
    return n % GRID_SIZE

# Place agents at random distinct locations
all_positions = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
random.shuffle(all_positions)
for _ in range(NUM_AGENTS):
    x, y = all_positions.pop()
    sight = random.randint(2, 5)  # random sight
    agents.append({"x": x, "y": y, "energy": INITIAL_ENERGY, "sight": sight})

def sugar_growth_phase():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if sugar[x][y] < capacity[x][y]:
                sugar[x][y] += 1

def visible_cells(agent):
    s = agent["sight"]
    x, y = agent["x"], agent["y"]
    cells = [(x, y)]
    for i in range(1, s + 1):
        cells.append((x, wrap(y - i)))  # Up
    for i in range(1, s + 1):
        cells.append((x, wrap(y + i)))  # Down
    for i in range(1, s + 1):
        cells.append((wrap(x - i), y))  # Left
    for i in range(1, s + 1):
        cells.append((wrap(x + i), y))  # Right
    return cells

def agent_movement_phase():
    random.shuffle(agents)
    occupied = {(a["x"], a["y"]) for a in agents}

    for agent in agents:
        vis_cells = visible_cells(agent)
        free_cells = [(cx, cy) for (cx, cy) in vis_cells if (cx, cy) == (agent["x"], agent["y"]) or (cx, cy) not in occupied]

        if not free_cells:
            # No free cell visible, agent stays put
            continue

        # Choose cell with max sugar
        max_sug = max(sugar[cx][cy] for cx, cy in free_cells)
        candidates = [(cx, cy) for (cx, cy) in free_cells if sugar[cx][cy] == max_sug]
        chosen = random.choice(candidates)

        old_pos = (agent["x"], agent["y"])
        if chosen != old_pos:
            occupied.remove(old_pos)
            occupied.add(chosen)
        agent["x"], agent["y"] = chosen[0], chosen[1]

        # Consume sugar
        agent["energy"] += sugar[chosen[0]][chosen[1]]
        sugar[chosen[0]][chosen[1]] = 0

def consumption_phase(agents_list):
    survivors = []
    for ag in agents_list:
        ag["energy"] -= 1
        if ag["energy"] > 0:
            survivors.append(ag)
    return survivors

def reproduction_phase(agents_list):
    occupied = {(a["x"], a["y"]) for a in agents_list}
    new_agents = []
    for ag in agents_list:
        if ag["energy"] > 20:
            neighbors = [
                (wrap(ag["x"]), wrap(ag["y"] - 1)), # Up
                (wrap(ag["x"]), wrap(ag["y"] + 1)), # Down
                (wrap(ag["x"] - 1), wrap(ag["y"])), # Left
                (wrap(ag["x"] + 1), wrap(ag["y"]))  # Right
            ]
            free_neighbors = [(nx, ny) for (nx, ny) in neighbors if (nx, ny) not in occupied]
            if free_neighbors:
                child_pos = random.choice(free_neighbors)
                parent_energy = ag["energy"]
                parent_new_energy = parent_energy // 2
                child_energy = parent_energy - parent_new_energy
                ag["energy"] = parent_new_energy

                child_sight = ag["sight"]
                # Mutation
                mutation = random.randint(0, 10)
                if mutation == 0:
                    child_sight -= 1
                    if child_sight < 1:
                        child_sight = 1
                elif mutation == 1:
                    child_sight += 1

                child = {
                    "x": child_pos[0],
                    "y": child_pos[1],
                    "energy": child_energy,
                    "sight": child_sight
                }
                new_agents.append(child)
                occupied.add(child_pos)

    agents_list.extend(new_agents)
    return agents_list

# Data collection
evolution_file = open('evolution_data.csv', 'w', newline='')
evolution_writer = csv.writer(evolution_file)
sight_range_to_track = range(1, 11)
header = ["turn", "num_agents"] + [f"sight_{s}" for s in sight_range_to_track]
evolution_writer.writerow(header)

for turn in range(1, TURNS + 1):
    sugar_growth_phase()
    agent_movement_phase()
    # Consumption and death
    agents = consumption_phase(agents)
    # Reproduction
    agents = reproduction_phase(agents)

    num_agents = len(agents)
    sight_counts = {s:0 for s in sight_range_to_track}
    for a in agents:
        if a["sight"] in sight_counts:
            sight_counts[a["sight"]] += 1

    row = [turn, num_agents] + [sight_counts[s] for s in sight_range_to_track]
    evolution_writer.writerow(row)

evolution_file.close()

# Example plotting (not required, but helpful)
# Plot number of agents over time
turns = []
counts = []
with open('evolution_data.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        t = int(row[0])
        n = int(row[1])
        turns.append(t)
        counts.append(n)

plt.figure()
plt.plot(turns, counts, linestyle='-')
plt.xlabel("Turn")
plt.ylabel("Number of Agents")
plt.title("Number of Agents Over Time (Evolutionary Sugarscape)")
plt.show()

# Plot average sight over time
turns = []
avg_sight = []
with open('evolution_data.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    # header: turn, num_agents, sight_1, sight_2, ...
    for row in reader:
        t = int(row[0])
        n = int(row[1])
        if n > 0:
            total_sight = 0
            idx_offset = 2
            for i, s_val in enumerate(sight_range_to_track):
                count_s = int(row[i+idx_offset])
                total_sight += s_val * count_s
            a_sight = total_sight / n
            turns.append(t)
            avg_sight.append(a_sight)

plt.figure()
plt.plot(turns, avg_sight, linestyle='-')
plt.xlabel("Turn")
plt.ylabel("Average Sight")
plt.title("Average Sight Over Time (Evolutionary Sugarscape)")
plt.show()
