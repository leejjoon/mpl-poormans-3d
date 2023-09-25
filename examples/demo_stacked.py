"""
====================
Labeled Stacked Barchart
====================
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

np.random.seed(16)

x = ["a","b","c","d"]
yy = np.random.random((5, len(x)))

yy = yy / yy.sum(axis=0) * 100

fig, ax = plt.subplots(num=1, clear=True)
bottom = np.zeros_like(yy[0])
for y in yy:
    ax.bar(x, y, bottom=bottom)
    bottom += y

from matplotlib.colors import LightSource
from mpl_poormans_3d import BarToPrism, BarToCylinder
from mpl_poormans_3d import Poormans3d, Poormans3dFace
from mpl_visual_context.patheffects import (Offset, Affine, ClipPathSelf,
                                            GCModify, StrokeOnly,
                                            StrokeColorFromFillColor,
                                            HLSModify)

ax.set_ylim(-7, 140)
ls = LightSource(azdeg=40)
# ls2 = LightSource(azdeg=180+20)

# bar_to_prism = BarToPrism(ls, 4, ratio=0.3, rotate_deg=10)
bar_to_prism = BarToCylinder(ls, ratio=0.3)

for i, container in enumerate(ax.containers):
    offset = Offset(0, i*10)
    for p in container.patches:
        p.set_path_effects([offset | bar_to_prism])

pe_engraved = ClipPathSelf() | Poormans3d(ls, (0, -2))
pe3d_face = Poormans3dFace(ls, (0, 0))

for i, c in enumerate(x):
    t = ax.text(i, 100, c, ha="center", va="baseline", size=60,
                color=ax.containers[-1].patches[0].get_fc())
    scale = Affine().translate(0, 15).scale(1, 0.3).translate(0, -15)
    t.set_path_effects([
        scale | offset,
        scale | offset | pe_engraved,
        scale | offset | pe3d_face
        | StrokeColorFromFillColor()
        | StrokeOnly()
    ])

ax.set_yticks([])

plt.show()
