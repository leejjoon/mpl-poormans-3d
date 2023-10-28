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

n_species = len(species)
x = np.arange(len(species))  # the label locations
n = len(penguin_means)

space_between_species = 0.3
space_between_attributes = 0.05

bar_width = (1 - space_between_species - (n-1) * space_between_attributes) / n

offset_between_attributes = np.arange(n) * (bar_width + space_between_attributes)
label_offset = (1 - space_between_species) * 0.5

for o, (attribute, measurement) in zip(offset_between_attributes,
                                       penguin_means.items()):
    rects = ax.bar(x + o + bar_width*0.5,  # bar_width*0.5 is needed as the bar
                                           # is centered at the given position.
                   measurement, bar_width, label=attribute)
    ax.bar_label(rects, padding=3)

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Length (mm)')
ax.set_title('Penguin attributes by species')
ax.set_xticks(x + label_offset, species)
ax.legend(loc='upper left', ncols=n)

for i in range(n_species):
    for z, p in enumerate(ax.patches[i::n_species]):
        p.set_zorder(p.get_zorder() - z*0.01)

ax.set_xlim(-0.4, 3.1)
ax.set_ylim(-25, 290)

import mpl_visual_context.patheffects as pe
from mpl_visual_context.patheffects_image_effect import ImageClipboard
from matplotlib.colors import LightSource
from mpl_poormans_3d import Poormans3d, Poormans3dFace
from mpl_visual_context.artist_helper import ArtistListWithPE
from mpl_visual_context.patheffects_image_effect import ReflectionArtist

def colored_thick_line(c):
    "patheffect to make thick outline with given color with lightness set at 0.3"
    return pe.GCModify(linewidth=4) | pe.StrokeColor(c) | pe.HLSModify(l=0.3)

ic = ImageClipboard()
ic_flipped = ImageClipboard()

tr_skew = pe.PostAffine().skew_deg(0, 10)

ls = LightSource(azdeg=170)

p3d = Poormans3d(ls, displacement=(-10, 7), fraction=0.5)
p3d_face = Poormans3dFace(ls, displacement=(0, 0), fraction=0.5)
rc = pe.RoundCorner(5)

ic= ImageClipboard()
ic_flipped = ImageClipboard()

for i in range(n_species):
    tr_recenter = pe.Recenter(ax, i, 0, coords="data")
    skew = tr_recenter | tr_skew | tr_recenter.restore()
    skew_flipped = (tr_recenter | pe.PostAffine().scale(1, -1)
                    | tr_skew  | tr_recenter.restore() | pe.Offset(0, -5))

    pe_reflection = [
        rc | skew_flipped | p3d | ic_flipped.copy(),
        rc | skew_flipped | p3d_face | ic_flipped.copy(),
        rc | skew | p3d | ic.copy(),
        rc | skew | p3d_face | ic.copy()
    ]

    a_flipped = ArtistListWithPE(ax.patches[i::n_species], pe_reflection)
    a_flipped.set_zorder(0.5)
    ax.add_artist(a_flipped)

    for p, t in zip(ax.patches[i::n_species], ax.texts[i::n_species]):
        p.set_path_effects([skew | rc | p3d,
                            skew | rc | p3d_face,
                            ])

        t.set_path_effects([skew | colored_thick_line(p.get_fc()),
                            skew | pe.FillColor("w")
                            ])

a = ReflectionArtist(ic_flipped, clipboard_alpha=ic,
                     alpha_dist_sigma=20, # image will become transparent about
                                          # 20 points away from the originl
                                          # imge.
                     clear_alpha=True # make sure that clipboard_alpha is cleared after use.
                     )
a.set_zorder(0.7)
ax.add_artist(a)

plt.show()
