import random

from plots.independent.processFile import Price
from plots.independent.network import create_graph
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import numpy as np
import pandas as pd
import multiprocessing
import sys


def read_prices_in_chunk(chunk):
    price_array = []
    noise_only = True
    informed_length = 0
    for row in chunk.itertuples():
        # Create price object
        price_object = Price()

        # Append the properties
        price_object.price = row[row._fields.index("price")]
        price_object.quantity = row[row._fields.index("quty")]
        price_object.direction = row[row._fields.index("dirTrigger")]
        price_object.first_agent = row[row._fields.index("AgTrigger")]
        price_object.second_agent = row[row._fields.index("ag2")]
        price_object.best_ask = row[row._fields.index("bestask")]
        price_object.best_bid = row[row._fields.index("bestbid")]

        if price_object.first_agent.startswith('Overvalued') or price_object.second_agent.startswith('Overvalued'):
            noise_only = False
            informed_length += 1

        # Add the price to the intermediate array
        price_array.append(price_object)
    return price_array, noise_only, informed_length


def task(counter, mean_laplacian_noise_list, mean_laplacian_informed_list, list_lock):
    laplacian_noise = []
    laplacian_informed = []
    laplacian_granularity = 3000

    with pd.read_csv("plots/csvs/prices" + str(counter + 1) + ".csv",
                     chunksize=laplacian_granularity, delimiter=";") as reader:
        for chunk in reader:
            price_array, noise_only, informed_length = read_prices_in_chunk(chunk)
            if noise_only:
                g_noise = create_graph(price_array)
                laplacian_noise.append(nx.laplacian_spectrum(g_noise))
            elif informed_length > 100:
                g_informed = create_graph(price_array)
                laplacian_informed.append(nx.laplacian_spectrum(g_informed))

    laplacian_informed.pop(0)
    laplacian_informed.pop()
    with list_lock:
        mean_laplacian_noise_list.append(random.choice(laplacian_noise))
        mean_laplacian_informed_list.append(random.choice(laplacian_informed))


if __name__ == '__main__':
    # Create a PIN list
    mean_laplacian_noise = multiprocessing.Manager().list()
    mean_laplacian_informed = multiprocessing.Manager().list()
    lock = multiprocessing.Lock()

    # Create three processes for each task using a for loop
    processes = []
    for simulationIndex in range(int(sys.argv[1])):
        process = multiprocessing.Process(target=task, args=(simulationIndex, mean_laplacian_noise,
                                                             mean_laplacian_informed, lock))
        processes.append(process)

    # Start all processes
    for process in processes:
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

    print('Monte Carlo done. Start generating plots!\n')
    fig, ax1 = plt.subplots(figsize=(8, 8))
    # Plot the Laplacian spectrum of Noise
    for noise in mean_laplacian_noise:
        number_of_bins_noise = (max(noise) - min(noise)) / (3.5 * np.std(noise) / pow(len(noise), (1 / 3)))
        print(number_of_bins_noise)
        for i in range(len(noise)):
            noise[i] = float("{:.4f}".format(float(noise[i])))
        print(noise, "\n")
        plt.hist(noise, alpha=0.5, color='blue', label='Noise')
        sns.kdeplot(ax=ax1, data=noise, color='blue', alpha=.3, linewidth=0, fill=True, label='Noise')

    # Plot the Laplacian spectrum of Informed
    for informed in mean_laplacian_informed:
        number_of_bins_informed = (max(informed) - min(informed)) / (3.5 * np.std(informed) / pow(len(informed), (1 / 3)))
        print(number_of_bins_informed)
        for i in range(len(informed)):
            informed[i] = float("{:.4f}".format(float(informed[i])))
        print(informed)
        print('\n')
        ax1.hist(informed, alpha=0.5, color='red', label='Informed')
        sns.kdeplot(ax=ax1, data=informed, color='red', alpha=.3, linewidth=0, fill=True, label='Informed')

    # Add title, labels, and legend to the plot
    fig.suptitle('Laplacian Spectrum')
    ax1.set_xlabel('Eigenvalue')
    ax1.set_ylabel('Frequency')
    fig.savefig("laplacian.png")