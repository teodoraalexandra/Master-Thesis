from plots.independent.processFile import Price
from plots.independent.computeMetrics import compute_metrics
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import multiprocessing
import sys


def task(counter, mean_PIN_list, mean_assortativity_list, mean_bipartivity_list,
         mean_spectral_list, mean_connected_list, y_axis, list_lock):
    PIN_results = []
    assortativity_results = []
    bipartivity_results = []
    spectral_results = []
    connected_results = []
    intermediate_y = []

    with pd.read_csv("plots/csvs/prices" + str(counter + 1) + ".csv", chunksize=300, delimiter=";") as reader:
        for chunk in reader:
            price_array = []
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

                # Add the price to the intermediate array
                price_array.append(price_object)

            # Add the prices to y-axis -> Average of all prices from chunk
            average = 0
            items = 0
            for price_object in price_array:
                average += price_object.price
                items += 1
            intermediate_y.append(average / items)

            PIN, assortativity, bipartivity, spectralBipartivity, conn = compute_metrics(price_array)
            PIN_results.append(PIN)
            assortativity_results.append(assortativity)
            bipartivity_results.append(bipartivity)
            spectral_results.append(spectralBipartivity)
            connected_results.append(conn)

    with list_lock:
        y_axis.append(intermediate_y)
        mean_PIN_list.append(PIN_results)
        mean_assortativity_list.append(assortativity_results)
        mean_bipartivity_list.append(bipartivity_results)
        mean_spectral_list.append(spectral_results)
        mean_connected_list.append(connected_results)


def mean_with_padding(a):
    max_len = max([len(row) for row in a])
    mask = np.array([row + [np.nan] * (max_len - len(row)) for row in a])
    return np.nanmean(mask, axis=0)


if __name__ == '__main__':
    # Create a PIN list
    mean_PIN_results = multiprocessing.Manager().list()
    mean_assortativity_results = multiprocessing.Manager().list()
    mean_bipartivity_results = multiprocessing.Manager().list()
    mean_spectral_results = multiprocessing.Manager().list()
    mean_connected_results = multiprocessing.Manager().list()
    y_price_axis = multiprocessing.Manager().list()
    lock = multiprocessing.Lock()

    # Create three processes for each task using a for loop
    processes = []
    for simulationIndex in range(int(sys.argv[1])):
        process = multiprocessing.Process(target=task, args=(simulationIndex, mean_PIN_results,
                                                             mean_assortativity_results, mean_bipartivity_results,
                                                             mean_spectral_results, mean_connected_results,
                                                             y_price_axis, lock))
        processes.append(process)

    # Start all processes
    for process in processes:
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

    print('Monte Carlo done. Start generating plots!\n')
    x_axis = []
    plt.figure().set_figheight(5)
    plt.figure().set_figwidth(20)
    for simulationIndex in range(int(sys.argv[1])):
        for priceIndex in range(len(y_price_axis[simulationIndex])):
            x_axis.append(priceIndex)
        plt.plot(x_axis, y_price_axis[simulationIndex], label="Simulation" + str(simulationIndex + 1))
        x_axis = []
    plt.title('Price evolution')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.savefig("price_evolution.png")

    # Mean PIN
    mean_PIN_results = mean_with_padding(mean_PIN_results)

    # Mean Assortativity
    mean_assortativity_results = mean_with_padding(mean_assortativity_results)

    # Mean Bipartivity
    mean_bipartivity_results = mean_with_padding(mean_bipartivity_results)

    # Mean Density
    mean_spectral_results = mean_with_padding(mean_spectral_results)

    # Mean Connected Components
    mean_connected_results = mean_with_padding(mean_connected_results)

    # CORRELATION PLOTS
    x_axis_PIN = np.array(mean_PIN_results)
    y_axis_assortativity = np.array(mean_assortativity_results)
    y_axis_bipartivity = np.array(mean_bipartivity_results)
    y_axis_spectral = np.array(mean_spectral_results)
    y_axis_connected = np.array(mean_connected_results)

    x_axis = []
    for index in range(len(x_axis_PIN)):
        x_axis.append(index)

    # Plot first
    plt.close()
    plt.title('Correlation between PIN and assortativity')
    plt.plot(x_axis, x_axis_PIN, label="PIN")
    plt.plot(x_axis, y_axis_assortativity, label="ASSORTATIVITY")
    plt.legend()
    plt.xlabel('PIN')
    plt.ylabel('Assortativity')
    plt.savefig("plot_PIN_assortativity.png")

    # Plot second
    plt.close()
    plt.title('Correlation between PIN and density')
    plt.plot(x_axis, x_axis_PIN, label="PIN")
    plt.plot(x_axis, y_axis_bipartivity, label="DENSITY")
    plt.legend()
    plt.xlabel('PIN')
    plt.ylabel('Density')
    plt.savefig("plot_PIN_density.png")

    # Plot third
    plt.close()
    plt.title('Correlation between PIN and spectral bipartivity')
    plt.plot(x_axis, x_axis_PIN, label="PIN")
    plt.plot(x_axis, y_axis_spectral, label="BIPARTIVITY")
    plt.legend()
    plt.xlabel('PIN')
    plt.ylabel('Bipartivity')
    plt.savefig("plot_PIN_spectral_bipartivity.png")

    # Plot fourth
    plt.close()
    plt.title('Correlation between PIN and connected')
    plt.plot(x_axis, x_axis_PIN, label="PIN")
    plt.plot(x_axis, y_axis_connected, label="CONNECTED")
    plt.legend()
    plt.xlabel('PIN')
    plt.ylabel('Connected')
    plt.savefig("plot_PIN_spectral_connected.png")

    plt.close()
