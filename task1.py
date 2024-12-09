import random
import csv

# Parameters
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
        # capacity and sugar arrays
        self.capacity = [[x+y for y in range(grid_size)] for x in range(grid_size)]
        self.sugar = [[self.capacity[x][y] for y in range(grid_size)] for x in range(grid_size)]
        # Place agents randomly
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
        # Agent can see up to SIGHT steps N, S, E, W, plus current
        visible = []
        # include current location
        visible.append((agent.x, agent.y))
        for i in range(1, agent.sight+1):
            visible.append((self.wrap(agent.x+i), agent.y)) # East
            visible.append((self.wrap(agent.x-i), agent.y)) # West
            visible.append((agent.x, self.wrap(agent.y+i))) # South
            visible.append((agent.x, self.wrap(agent.y-i))) # North
        # Remove duplicates if any
        visible = list(set(visible))
        return visible

    def agent_movement_phase(self):
        # Move agents in random order
        random.shuffle(self.agents)
        occupied = {(ag.x, ag.y) for ag in self.agents if ag.alive}

        for agent in self.agents:
            if not agent.alive:
                continue
            vis_locs = self.visible_locations(agent)
            # choose location with highest sugar, ties random
            # cannot choose location with another agent
            candidates = [(lx,ly) for (lx,ly) in vis_locs if (lx,ly) not in occupied or (lx,ly) == (agent.x, agent.y)]
            if not candidates:
                # If no candidates, stay put
                continue
            best_sugar = max(self.sugar[lx][ly] for (lx,ly) in candidates)
            best_candidates = [(lx,ly) for (lx,ly) in candidates if self.sugar[lx][ly] == best_sugar]
            new_x, new_y = random.choice(best_candidates)
            # Update occupied set
            occupied.remove((agent.x, agent.y))
            agent.x, agent.y = new_x, new_y
            occupied.add((agent.x, agent.y))
            # Consume sugar
            agent.energy += self.sugar[new_x][new_y]
            self.sugar[new_x][new_y] = 0

    def consumption_phase(self):
        # Each agent loses 1 energy, if <=0 dies
        for agent in self.agents:
            if agent.alive:
                agent.energy -= 1
                if agent.energy <= 0:
                    agent.alive = False

    def run_simulation(self, turns=TURNS):
        # For Task 2 data: 
        # 1) sum of energy each turn
        # 2) positions of agents at turn 1,50,500
        # 3) sugar at each location at turn 1,50,500
        energy_data = []
        pos_data = {}
        sugar_data = {}

        for t in range(1, turns+1):
            # phases
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

        # Write to CSV
        # Energy over turns
        with open("task1_energy_data.csv","w",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Turn","TotalEnergy"])
            writer.writerows(energy_data)

        # Agent positions
        with open("task1_agent_positions.csv","w",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Turn","AgentX","AgentY"])
            for t in pos_data:
                for (x,y) in pos_data[t]:
                    writer.writerow([t,x,y])

        # Sugar levels
        with open("task1_sugar_levels.csv","w",newline='') as f:
            writer = csv.writer(f)
            # Format: Turn, X, Y, Sugar
            writer.writerow(["Turn","X","Y","Sugar"])
            for t in sugar_data:
                for x in range(self.grid_size):
                    for y in range(self.grid_size):
                        writer.writerow([t,x,y,sugar_data[t][x][y]])


if __name__ == "__main__":
    s = Sugarscape()
    s.run_simulation()
    print("Task 1 simulation completed. Data saved to CSV files.")
