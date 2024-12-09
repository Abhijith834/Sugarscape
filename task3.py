import random
import csv
import statistics

# Parameters
GRID_SIZE = 20
NUM_AGENTS = 20
INITIAL_ENERGY = 10
TURNS = 500

class Agent:
    def __init__(self, x, y, energy=INITIAL_ENERGY, sight=None):
        if sight is None:
            # random initial sight between 2 and 5
            self.sight = random.randint(2,5)
        else:
            self.sight = sight
        self.x = x
        self.y = y
        self.energy = energy
        self.alive = True

class EvolSugarscape:
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
            candidates = [(lx,ly) for (lx,ly) in vis_locs if (lx,ly) not in occupied or (lx,ly) == (agent.x,agent.y)]
            if not candidates:
                continue
            best_sugar = max(self.sugar[lx][ly] for (lx,ly) in candidates)
            best_candidates = [(lx,ly) for (lx,ly) in candidates if self.sugar[lx][ly] == best_sugar]
            new_x, new_y = random.choice(best_candidates)
            occupied.remove((agent.x, agent.y))
            agent.x, agent.y = new_x, new_y
            occupied.add((agent.x, agent.y))
            # consume sugar
            agent.energy += self.sugar[new_x][new_y]
            self.sugar[new_x][new_y] = 0

    def consumption_phase_and_procreation(self):
        # Energy consumption
        occupied = {(a.x,a.y) for a in self.agents if a.alive}
        new_agents = []
        for agent in self.agents:
            if agent.alive:
                agent.energy -= 1
                if agent.energy <= 0:
                    agent.alive = False
                    continue

                # Check procreation
                if agent.energy > 20:
                    # try to find empty neighbor
                    neighbors = [(agent.x+1, agent.y),
                                 (agent.x-1, agent.y),
                                 (agent.x, agent.y+1),
                                 (agent.x, agent.y-1)]
                    neighbors = [(self.wrap(x),self.wrap(y)) for (x,y) in neighbors]
                    empty_neighbors = [n for n in neighbors if n not in occupied]
                    if empty_neighbors:
                        child_x, child_y = random.choice(empty_neighbors)
                        # split energy
                        child_energy = agent.energy // 2
                        agent.energy = agent.energy - child_energy
                        child_sight = agent.sight
                        # mutation
                        m = random.randint(0,10)
                        if m == 0 and child_sight > 2:
                            child_sight -= 1
                        elif m == 1 and child_sight < 5:
                            child_sight += 1

                        child = Agent(child_x, child_y, energy=child_energy, sight=child_sight)
                        new_agents.append(child)
                        occupied.add((child_x, child_y))

        self.agents.extend(new_agents)

    def run_simulation(self, turns=TURNS):
        # Track number of agents and sight distribution each turn
        data = []
        for t in range(1, turns+1):
            self.sugar_growth_phase()
            self.agent_movement_phase()
            self.consumption_phase_and_procreation()

            living_agents = [a for a in self.agents if a.alive]
            count = len(living_agents)
            if count > 0:
                sights = [a.sight for a in living_agents]
                avg_sight = statistics.mean(sights)
            else:
                avg_sight = 0

            data.append((t, count, avg_sight))

        # Write CSV
        with open("task3_evolution_data.csv","w",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Turn","NumAgents","AvgSight"])
            writer.writerows(data)

if __name__ == "__main__":
    s = EvolSugarscape()
    s.run_simulation()
    print("Task 3 simulation completed. Data saved to CSV.")
