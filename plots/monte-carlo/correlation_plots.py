import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import csv

with open("PIN_mean.csv", "r") as f:
    reader = csv.reader(f)
    data = list(reader)

# Convert the data to a numpy array
data = np.array(data, dtype=float)

# Compute the average of each column
PIN_results = np.mean(data, axis=0)

with open("assortativity_mean.csv", "r") as f:
    reader = csv.reader(f)
    data = list(reader)

# Convert the data to a numpy array
data = np.array(data, dtype=float)

# Compute the average of each column
assortativity_results = np.mean(data, axis=0)

with open("bipartivity_mean.csv", "r") as f:
    reader = csv.reader(f)
    data = list(reader)

# Convert the data to a numpy array
data = np.array(data, dtype=float)

# Compute the average of each column
bipartivity_results = np.mean(data, axis=0)

# CORRELATION PLOTS
x_axis_PIN = np.array(PIN_results)
y_axis_assortativity = np.array(assortativity_results)
y_axis_bipartivity = np.array(bipartivity_results)

# This returns the correlation matrix
# -> a two-dimensional array with the correlation coefficients
correlation_matrix_assortativity = np.corrcoef(x_axis_PIN, y_axis_assortativity)
print("Correlation matrix PIN-assortativity: \n", correlation_matrix_assortativity)
correlation_matrix_bipartivity = np.corrcoef(x_axis_PIN, y_axis_bipartivity)
print("Correlation matrix PIN-bipartivity: \n", correlation_matrix_bipartivity)

# The red squares represent the observations
# The blue line is the regression line

plt.style.use('ggplot')

# Plot first
fig1, ax1 = plt.subplots()
ax1.plot(x_axis_PIN, y_axis_assortativity, linewidth=0, marker='s', label='Data points')
ax1.set_xlabel('PIN')
ax1.set_ylabel('ASSORTATIVITY')
ax1.legend(facecolor='white')
plt.savefig("plot_correlation_1.png")

# Plot second
fig2, ax2 = plt.subplots()
ax2.plot(x_axis_PIN, y_axis_bipartivity, linewidth=0, marker='s', label='Data points')
ax2.set_xlabel('PIN')
ax2.set_ylabel('BIPARTIVITY')
ax2.legend(facecolor='white')
plt.savefig("plot_correlation_2.png")

