import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

with open("load.dat") as f:
    data = np.loadtxt(f)

number_of_bins = max(10, len(data)/10)
plt.hist(data, normed=True, histtype='bar')
plt.savefig('load_histogram.png', dpi=50)

sorted_data = np.sort(data)

plt.clf()
plt.plot(sorted_data, 'o', color='r', mec='r')
plt.xlabel('Nodes')
plt.ylabel('Number of incoming requests')
plt.savefig('load_dots.png', dpi=300)
