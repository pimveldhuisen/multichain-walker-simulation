import matplotlib.pyplot as plt
import numpy as np

with open("blocks.dat") as f:
	data = np.loadtxt(f)

timestamps = data[:,0]
values = data[:,1:]
averages = np.average(values, axis=1)

plt.clf()
plt.boxplot(values.transpose(), showmeans=True, showfliers=False)
plt.savefig('blocks.png')
