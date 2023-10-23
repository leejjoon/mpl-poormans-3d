"""
====================
Cylinder bar chart
====================

"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.transforms import Affine2D

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

max_height=6000
colors=[None, "w", None, "w"] * 8
rgbFace=None
# affines=[(Affine2D().translate(10, -10).scale(0.5), Affine2D().translate(10, -10)),
#          (Affine2D(), Affine2D().scale(0.5))]
affines=[(Affine2D().translate(0, 0), Affine2D().translate(0, 0)),
         (Affine2D().translate(5, 0), Affine2D().translate(5, 0)),
         (Affine2D().translate(0, 0), Affine2D().translate(0, 0)),
         (Affine2D().translate(-5, 0), Affine2D().translate(-5, 0)),
         ] * 8

segment_params = (ax, max_height, colors, rgbFace, affines)
segment_params = None

bar_to_prism = BarToPrism(ls, 4, scale=0.9, rotate_deg=20)
# bar_to_prism = BarToCylinder(ls, scale=0.8, segment_params=segment_params,
#                              fraction=0.3)

for i, p in enumerate(ax.containers[0]):
    p.set_path_effects([bar_to_prism])

for i, p in enumerate(ax.containers[1]):
    p.set_path_effects([bar_to_prism])

plt.show()
