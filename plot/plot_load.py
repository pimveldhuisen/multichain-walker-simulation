import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

with open("load.dat") as f:
    data = np.loadtxt(f)

number_of_bins = max(10, len(data)/10)
plt.hist(data, normed=True, histtype='bar')
plt.savefig('load.png', dpi=50)
