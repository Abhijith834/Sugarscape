import random
import csv
import statistics
import matplotlib.pyplot as plt

# Parameters
GRID_SIZE = 20
NUM_AGENTS = 20
INITIAL_ENERGY = 10
TURNS = 500

class Agent:
    def __init__(self, x, y, energy=INITIAL_ENERGY, sight=None, uses_empowerment=None):
        if sight is None:
            sight = random.randint(2,5)
        if uses_empowerment is None:
            uses_empowerment = (random.random() < 0.5) # 50% chance
        self.x = x
        self.y = y
        self.energy = energy
        self.sight = sight
        self.alive = True
        self.uses_empowerment = uses_empowerment

class EmpoweredSugarscape:
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

    def empowerment(self, x, y, sight, occupied):
        # Compute how many moves are possible next turn from (x,y)
        # Next turn, the agent can choose from visible locations again.
        # For approximation, we just count how many distinct locations are visible next turn that are not occupied.
        vis = []
        vis.append((x,y))
        for i in range(1, sight+1):
            vis.append((self.wrap(x+i),y))
            vis.append((self.wrap(x-i),y))
            vis.append((x,self.wrap(y+i)))
            vis.append((x,self.wrap(y-i)))
        vis = set(vis)
        # Consider that no other agent moves now, so we just count how many are free
        free_spots = [loc for loc in vis if loc not in occupied or loc == (x,y)]
        return len(free_spots)

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
            
            # If uses empowerment:
            # Choose location to maximize: sugar(lx,ly) + alpha * empowerment(lx,ly)
            # Let's pick alpha = 0.5 just as an example
            # If not uses empowerment: just choose by sugar.

            if agent.uses_empowerment:
                best_score = None
                best_candidates = []
                for (cx,cy) in candidates:
                    # Evaluate sugar
                    s_val = self.sugar[cx][cy]
                    # Evaluate empowerment at that location
                    # Temporarily assume this location is agent's location next turn
                    # The set of occupied must remove agent's old position and include new
                    new_occupied = set(occupied)
                    if (agent.x,agent.y) in new_occupied:
                        new_occupied.remove((agent.x,agent.y))
                    # We do not add the new spot yet because we are evaluating it
                    emp_val = self.empowerment(cx, cy, agent.sight, new_occupied)
                    score = s_val + 0.5 * emp_val
                    if best_score is None or score > best_score:
                        best_score = score
                        best_candidates = [(cx,cy)]
                    elif score == best_score:
                        best_candidates.append((cx,cy))
                new_x, new_y = random.choice(best_candidates)
            else:
                # normal sugar-based decision
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
        occupied = {(a.x,a.y) for a in self.agents if a.alive}
        new_agents = []
        for agent in self.agents:
            if agent.alive:
                agent.energy -= 1
                if agent.energy <= 0:
                    agent.alive = False
                    continue
                # Procreate if energy >20
                if agent.energy > 20:
                    neighbors = [(agent.x+1, agent.y),
                                 (agent.x-1, agent.y),
                                 (agent.x, agent.y+1),
                                 (agent.x, agent.y-1)]
                    neighbors = [(self.wrap(x),self.wrap(y)) for (x,y) in neighbors]
                    empty_neighbors = [n for n in neighbors if n not in occupied]
                    if empty_neighbors:
                        child_x, child_y = random.choice(empty_neighbors)
                        child_energy = agent.energy // 2
                        agent.energy = agent.energy - child_energy
                        child_sight = agent.sight
                        # mutation
                        m = random.randint(0,10)
                        if m == 0 and child_sight > 2:
                            child_sight -= 1
                        elif m == 1 and child_sight < 5:
                            child_sight += 1

                        # Inherit uses_empowerment
                        child_ue = agent.uses_empowerment
                        child = Agent(child_x, child_y, energy=child_energy, sight=child_sight, uses_empowerment=child_ue)
                        new_agents.append(child)
                        occupied.add((child_x, child_y))

        self.agents.extend(new_agents)

    def run_simulation(self, turns=TURNS):
        # Track number of agents using empowerment vs not
        # Track avg energy of both groups
        data = []
        for t in range(1, turns+1):
            self.sugar_growth_phase()
            self.agent_movement_phase()
            self.consumption_phase_and_procreation()

            living_agents = [a for a in self.agents if a.alive]
            emp_agents = [a for a in living_agents if a.uses_empowerment]
            non_emp_agents = [a for a in living_agents if not a.uses_empowerment]

            num_emp = len(emp_agents)
            num_non_emp = len(non_emp_agents)
            avg_emp_energy = statistics.mean([a.energy for a in emp_agents]) if num_emp>0 else 0
            avg_non_emp_energy = statistics.mean([a.energy for a in non_emp_agents]) if num_non_emp>0 else 0

            data.append((t, len(living_agents), num_emp, num_non_emp, avg_emp_energy, avg_non_emp_energy))

        with open("task4_empowerment_data.csv","w",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Turn","TotalAgents","EmpAgents","NonEmpAgents","AvgEmpEnergy","AvgNonEmpEnergy"])
            writer.writerows(data)

def plot_csv(file):
    turns = []
    total_agents = []
    emp_agents = []
    non_emp_agents = []
    avg_emp_energy = []
    avg_non_emp_energy = []

    with open(file,"r") as f:
        import csv
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            t = int(row[0])
            turns.append(t)
            total_agents.append(int(row[1]))
            emp_agents.append(int(row[2]))
            non_emp_agents.append(int(row[3]))
            avg_emp_energy.append(float(row[4]))
            avg_non_emp_energy.append(float(row[5]))

    plt.figure()
    plt.plot(turns, emp_agents, label="Empowered Agents")
    plt.plot(turns, non_emp_agents, label="Non-Empowered Agents")
    plt.xlabel("Turn")
    plt.ylabel("Number of Agents")
    plt.title("Empowered vs Non-Empowered Agents Over Time")
    plt.legend()
    plt.savefig("task4_emp_nonemp_agents.png")
    plt.close()

    plt.figure()
    plt.plot(turns, avg_emp_energy, label="Avg Energy (Empowered)")
    plt.plot(turns, avg_non_emp_energy, label="Avg Energy (Non-Empowered)")
    plt.xlabel("Turn")
    plt.ylabel("Average Energy")
    plt.title("Average Energy of Empowered vs Non-Empowered Agents")
    plt.legend()
    plt.savefig("task4_energy_comparison.png")
    plt.close()

    print("Task 4 analysis completed. Plots saved.")


if __name__ == "__main__":
    s = EmpoweredSugarscape()
    s.run_simulation()
    print("Task 4 simulation with empowerment completed. Data saved to CSV.")
    plot_csv("task4_empowerment_data.csv")

