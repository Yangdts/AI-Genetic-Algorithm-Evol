import glob
import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_charts(csv_folders, labels):
    all_max_fitnesses = []

    for csv_folder, label in zip(csv_folders, labels):
        csv_files = glob.glob(f"{csv_folder}/generation_*.csv")

        if not csv_files:
            print(f"No CSV files found in {csv_folder}.")
            continue
        
        max_fitnesses = []
        generations = []

        for file in csv_files:
            try:
                df = pd.read_csv(file)
                
                # Extract generation number from filename
                generation_number = int(file.split('_')[-1].split('.')[0])
                generations.append(generation_number)
                
                # Calculate max fitness for this generation
                max_fitness = df['fitness'].max()
                max_fitnesses.append(max_fitness)
            except Exception as e:
                print(f"Error processing {file}: {e}")

        # Sort generations and corresponding fitnesses
        sorted_indices = sorted(range(len(generations)), key=lambda k: generations[k])
        generations = [generations[i] for i in sorted_indices]
        max_fitnesses = [max_fitnesses[i] for i in sorted_indices]

        all_max_fitnesses.append(max_fitnesses)

    # Plot the data
    plt.figure(figsize=(10, 6))  # Adjust figure size as needed
    for i, max_fitnesses in enumerate(all_max_fitnesses):
        generations = range(1, len(max_fitnesses) + 1)  # Assuming one CSV per generation
        plt.plot(generations, max_fitnesses, marker='o', label=labels[i])

    plt.xlabel('Generation')
    plt.ylabel('Max Fitness')
    plt.title('Max Fitness over Generations')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    csv_folders = [
        "simulation_results/experimenta",
        "simulation_results/experimenta1",
        #"simulation_results/control_batch"
    ]
    labels = [
        #"Mutation rate 0.05",
        #"Mutation rate 0.20",
        "Control Batch (0.10)",
        "Mutation rate 0.3"
    ]
    plot_charts(csv_folders, labels)
