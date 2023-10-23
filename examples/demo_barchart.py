"""
====================
Demo with bar chart
====================
"""

import numpy as np

import matplotlib.pyplot as plt

from mpl_poormans_3d import Poormans3d, Poormans3dFace

import seaborn as sns
df = sns.load_dataset("penguins")

fig1, ax = plt.subplots(1, 1, num=1, clear=True, figsize=(5, 5))
fig1.subplots_adjust(left=0.2)

sns.barplot(data=df, x="island", y="body_mass_g", hue="sex", ax=ax)
ax.set_xlim(-0.7, 2.7)
ax.patch.set(fc="0.7", alpha=1)
# ax.legend_.remove()

# now we turn the figure into 3d.

from matplotlib.colors import LightSource
ls = LightSource(azdeg=105)
ls2 = LightSource(azdeg=180 + 105)

patch_list_bar = [p for p in ax.patches]
for patch in patch_list_bar:
    patch.set_path_effects([
        Poormans3d(ls, (10, 5),
                   fraction=0.3),
        Poormans3dFace(ls, (0, 0)),
    ])

from mpl_visual_context.patheffects import ClipPathSelf

ax.patch.set_path_effects([
    Poormans3d(ls, (10, 5), fraction=0.3), # outer wall
    ClipPathSelf() | Poormans3dFace(ls2, (10, 5), fraction=0.5),
    ClipPathSelf() | Poormans3d(ls2, (10, 5),
                                fraction=0.3), # inner wall
])

plt.show()
