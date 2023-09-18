"""
====================
Skewed 3d bar chart
====================

"""

import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(num=1, clear=True)

# We start from mpl example "Grouped bar chart with labels". The only change
# we made is to increase the offset slightly so that bars are separated.

species = ("Adelie", "Chinstrap", "Gentoo")
penguin_means = {
    'Bill Depth': (18.35, 18.43, 14.98),
    'Bill Length': (38.79, 48.83, 47.50),
    'Flipper Length': (189.95, 195.82, 217.19),
}

x = np.arange(len(species))  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

for attribute, measurement in penguin_means.items():
    offset = (width+0.1) * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Length (mm)')
ax.set_title('Penguin attributes by species')
ax.set_xticks(x + width, species)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 250)

# we adjust x and ylim to make room for 3d effects.
ax.set_xlim(-0.4, 2.8)
ax.set_ylim(-10, 290)

# We will skew the bar and squeez it a bit along the x-direction
from mpl_visual_context.patheffects import (Recenter, PostAffine,
                                            Offset)

tr_skew = PostAffine().skew_deg(0, 10).scale(0.8, 1)
offset = Offset(0, 5)

for i in range(3):
    tr_recenter = Recenter(ax, i, 0, coords="data")
    skew = tr_recenter | tr_skew | tr_recenter.restore()
    for p in ax.patches[i::3]:
        p.set_path_effects([skew])
    for l in ax.lines[i::3]:
        l.set_path_effects([skew])
    for t in ax.texts[i::3]:
        t.set_path_effects([skew | offset])

# adjust the pe of bar labels.
from mpl_visual_context.patheffects import (GCModify, FillColor, StrokeColor,
                                            HLSModify)

for t, p in zip(ax.texts, ax.patches):
    skew = t.get_path_effects()[0]
    color = p.get_fc()
    t.set_path_effects([
        (skew | StrokeColor(color)
         | HLSModify(l=0.3) | GCModify(linewidth=4)),
        skew | FillColor("w")])

# add 3d effects
from matplotlib.colors import LightSource

from mpl_poormans_3d import Poormans3d, Poormans3dFace

ls = LightSource(azdeg=170)

p3d = Poormans3d(ls, (-20, 7), fraction=0.5)
p3d_face = Poormans3dFace(ls, (0, 0), fraction=0.5)


# we recent the path effects, now with 3d effect
for i in range(3):
    tr_recenter = Recenter(ax, i, 0, coords="data")
    skew = tr_recenter | tr_skew | tr_recenter.restore()
    for z, p in enumerate(ax.patches[i::3]):
        p.set_path_effects([skew | p3d,
                            skew | p3d_face])
        # One may use ArtistListWithPoormans3d, but simply adjusting zorder
        # works in this case.
        p.set_zorder(p.get_zorder() - z*0.01)


# round corner
if True:
    from mpl_visual_context.patheffects import (RoundCorner,)
    rc = RoundCorner(15, i_selector=lambda i: i % 2)
    p3d = Poormans3d(ls, (-10, 5), fraction=0.5)
    p3d_face = Poormans3dFace(ls, (0, 0), fraction=0.5)
    for i in range(3):
        tr_recenter = Recenter(ax, i, 0, coords="data")
        skew = tr_recenter | tr_skew | tr_recenter.restore()
        for z, p in enumerate(ax.patches[i::3]):
            p.set_path_effects([rc | skew | p3d,
                                rc | skew | p3d_face])

plt.show()
