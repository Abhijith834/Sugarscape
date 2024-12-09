import random
import csv
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Combined Sugarscape 1 and 2
# ----------------------------

# Parameters for the simulation
GRID_SIZE = 20
NUM_AGENTS = 20
INITIAL_ENERGY = 10
SIGHT = 3
TURNS = 500

class Agent:
    def __init__(self, x, y, energy=INITIAL_ENERGY, sight=SIGHT):
        self.x = x
        self.y = y
        self.energy = energy
        self.sight = sight
        self.alive = True

class Sugarscape:
    def __init__(self, grid_size=GRID_SIZE):
        self.grid_size = grid_size
        self.capacity = [[x+y for y in range(grid_size)] for x in range(grid_size)]
        self.sugar = [[self.capacity[x][y] for y in range(grid_size)] for x in range(grid_size)]
        self.agents = []
        self.place_agents()

    def place_agents(self):
        positions = set()
        while len(positions) < NUM_AGENTS:
            x = random.randint(0, self.grid_size-1)
            y = random.randint(0, self.grid_size-1)
            if (x,y) not in positions:
                positions.add((x,y))
                self.agents.append(Agent(x, y))

    def wrap(self, coord):
        return coord % self.grid_size

    def sugar_growth_phase(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if self.sugar[x][y] < self.capacity[x][y]:
                    self.sugar[x][y] += 1

    def visible_locations(self, agent):
        visible = [(agent.x, agent.y)]
        for i in range(1, agent.sight+1):
            visible.append((self.wrap(agent.x+i), agent.y))
            visible.append((self.wrap(agent.x-i), agent.y))
            visible.append((agent.x, self.wrap(agent.y+i)))
            visible.append((agent.x, self.wrap(agent.y-i)))
        visible = list(set(visible))
        return visible

    def agent_movement_phase(self):
        random.shuffle(self.agents)
        occupied = {(a.x,a.y) for a in self.agents if a.alive}

        for agent in self.agents:
            if not agent.alive:
                continue
            vis_locs = self.visible_locations(agent)
            # Candidate locations can't be currently occupied by another agent (except current)
            candidates = [(lx,ly) for (lx,ly) in vis_locs if (lx,ly) not in occupied or (lx,ly) == (agent.x,agent.y)]
            if not candidates:
                continue
            # Choose location with max sugar
            best_sugar = max(self.sugar[lx][ly] for (lx,ly) in candidates)
            best_candidates = [(lx,ly) for (lx,ly) in candidates if self.sugar[lx][ly] == best_sugar]
            new_x, new_y = random.choice(best_candidates)
            occupied.remove((agent.x, agent.y))
            agent.x, agent.y = new_x, new_y
            occupied.add((agent.x, agent.y))
            # consume sugar
            agent.energy += self.sugar[new_x][new_y]
            self.sugar[new_x][new_y] = 0

    def consumption_phase(self):
        for agent in self.agents:
            if agent.alive:
                agent.energy -= 1
                if agent.energy <= 0:
                    agent.alive = False

    def run_simulation(self, turns=TURNS):
        # For Task 2 data collection
        energy_data = []
        pos_data = {}
        sugar_data = {}

        for t in range(1, turns+1):
            self.sugar_growth_phase()
            self.agent_movement_phase()
            self.consumption_phase()

            # Collect data
            living_agents = [a for a in self.agents if a.alive]
            total_energy = sum(a.energy for a in living_agents)
            energy_data.append((t,total_energy))

            if t in [1,50,500]:
                pos_data[t] = [(a.x,a.y) for a in living_agents]
                sugar_snapshot = [[self.sugar[x][y] for y in range(self.grid_size)] for x in range(self.grid_size)]
                sugar_data[t] = sugar_snapshot

        # Write CSV data
        with open("task1_energy_data.csv","w",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Turn","TotalEnergy"])
            writer.writerows(energy_data)

        with open("task1_agent_positions.csv","w",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Turn","AgentX","AgentY"])
            for t in pos_data:
                for (x,y) in pos_data[t]:
                    writer.writerow([t,x,y])

        with open("task1_sugar_levels.csv","w",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Turn","X","Y","Sugar"])
            for t in sugar_data:
                for x in range(self.grid_size):
                    for y in range(self.grid_size):
                        writer.writerow([t,x,y,sugar_data[t][x][y]])


# ----------------------------
# After simulation, perform the analysis (Task 2)
# ----------------------------

def analyze_results():
    # Load total energy data
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

    # Plot total energy over time
    plt.figure(figsize=(8,6))
    plt.plot(turns, energies, label="Total Energy")
    plt.xlabel("Turn")
    plt.ylabel("Total Energy in Living Agents")
    plt.title("Total Agent Energy Over Time")
    plt.legend()
    plt.savefig("task2_total_energy_plot.png")
    plt.close()

    # Load agent positions
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

    # Load sugar levels
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
        im = ax.imshow(sugar_by_turn[t].T, origin="lower", cmap="YlOrBr", interpolation="nearest")
        plt.colorbar(im, ax=ax, label="Sugar level")

        # Plot agent positions
        xs = [pos[0] for pos in positions_by_turn[t]]
        ys = [pos[1] for pos in positions_by_turn[t]]
        ax.scatter(xs, ys, c='red', edgecolors='black', label='Agents')

        ax.set_title(f"Turn {t} - Agents and Sugar Distribution")
        ax.set_xlim(-0.5, GRID_SIZE-0.5)
        ax.set_ylim(-0.5, GRID_SIZE-0.5)
        ax.set_xticks(range(0,GRID_SIZE,5))
        ax.set_yticks(range(0,GRID_SIZE,5))
        plt.legend()
        plt.savefig(f"task2_visualization_turn_{t}.png")
        plt.close()

    print("Analysis completed. Plots saved as PNG files.")

if __name__ == "__main__":
    # Run the simulation (Task 1)
    s = Sugarscape()
    s.run_simulation()
    print("Task 1 simulation completed. CSV files saved.")

    # Perform the analysis (Task 2)
    analyze_results()
    print("Task 2 analysis completed.")
