import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

with open("blocks.dat") as f:
    data = np.loadtxt(f)

timestamps = data[:, 0]
values = data[:, 1:]
averages = np.average(values, axis=1)

plt.figure(figsize=(20, 20))
plt.boxplot(values.transpose(), showmeans=True, showfliers=False)
plt.xlabel('Time (minutes)')
plt.ylabel('Number of blocks discovered')
plt.savefig('blocks.png', dpi=100)
