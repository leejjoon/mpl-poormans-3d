import bezier
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.transforms as mtransforms

from matplotlib.text import TextPath
from matplotlib.patches import PathPatch

from poormans_3d_demo import demo

fig, axs_ = plt.subplots(1, 2, num=1, clear=True, figsize=(8, 4))
axs = axs_.flat
fig.subplots_adjust(wspace=0.4)

ax = axs[0]
frequency = [120,120,380,240,200]
pie = ax.pie(frequency,
       startangle=90,
       counterclock=False,
       wedgeprops=dict(width=0.3)
       )

patch_list = pie[0]
for patch in patch_list:
    patch.set_visible(False)

demo(ax, patch_list,
     displacement=(0.15, 0.05),
     direction=1, azdeg=135, fraction=1)


ax = axs[1]
# ax.set_aspect(1.)
tp = TextPath((0.1, 0.2), "Hi", size=0.7,
              prop=dict(family="serif"))
p = PathPatch(tp, ec="none",
              fc="y",
              clip_on=False,
              transform=ax.transData)
# ax.add_artist(p)

patch_list = [p]

demo(ax, patch_list,
     displacement=(-15, -5),
     base_zorder=10, direction=-1, fraction=1.,
     transformed=True,
     refine_factor=1)

plt.show()
