"""
====================
Demo area chart
====================
"""

# We start from MPL's stackplot_demo.py.

import matplotlib.pyplot as plt
import numpy as np

# data from United Nations World Population Prospects (Revision 2019)
# https://population.un.org/wpp/, license: CC BY 3.0 IGO
year = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2018]
population_by_continent = {
    'africa': [228, 284, 365, 477, 631, 814, 1044, 1275],
    'americas': [340, 425, 519, 619, 727, 840, 943, 1006],
    'asia': [1394, 1686, 2120, 2625, 3202, 3714, 4169, 4560],
    'europe': [220, 253, 276, 295, 310, 303, 294, 293],
    'oceania': [12, 15, 19, 22, 26, 31, 36, 39],
}

fig, ax = plt.subplots(num=1, clear=True)
ax.stackplot(year, population_by_continent.values(),
             labels=population_by_continent.keys(), alpha=0.8)
ax.legend(loc='upper left', reverse=True)
ax.set_title('World population')
ax.set_xlabel('Year')
ax.set_ylabel('Number of people (millions)')

ax.set_xlim(1943, 2022)
ax.set_ylim(-100, 8300)

# Now we add 3d effects.
from mpl_poormans_3d import Poormans3d, Poormans3dFace
from mpl_visual_context.patheffects import Offset

from matplotlib.colors import LightSource
ls = LightSource(azdeg=35)

pe3d = Poormans3d(ls, (-10, 10))
pe3dface = Poormans3dFace(ls, (0, 0))
for i, col in enumerate(ax.collections):
    offset = Offset(0, i*5) # we are adding offset between areas.
    col.set_path_effects([offset | pe3d, offset | pe3dface])

plt.show()

