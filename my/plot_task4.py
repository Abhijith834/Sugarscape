# (Add this to sugarscape4.py or a separate analysis script)
import matplotlib.pyplot as plt

turns = []
total_agents = []
emp_agents = []
non_emp_agents = []
avg_emp_energy = []
avg_non_emp_energy = []

with open("task4_empowerment_data.csv","r") as f:
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
