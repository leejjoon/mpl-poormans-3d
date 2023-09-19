"""
====================
Cylinder bar chart
====================

"""

import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns

penguins = sns.load_dataset("penguins")

# Draw a nested barplot by species and sex
g = sns.catplot(
    data=penguins, kind="bar",
    x="species", y="body_mass_g", hue="sex",
    errorbar=None,
    height=6,
)
g.despine(left=True)
g.set_axis_labels("", "Body mass (g)")

g.legend.set_title("")

# Now we convert bars to prisms.

from matplotlib.colors import LightSource
from mpl_poormans_3d import BarToPrism, BarToCylinder

ax = g.ax
ax.set_ylim(ymin=-300)

ls = LightSource(azdeg=25)

bar_to_prism = BarToPrism(ls, 4, scale=0.9, rotate_deg=0)

for i, p in enumerate(ax.containers[0]):
    p.set_path_effects([bar_to_prism])

for i, p in enumerate(ax.containers[1]):
    p.set_path_effects([bar_to_prism])

plt.show()
