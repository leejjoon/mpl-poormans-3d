import numpy as np
from pathlib import Path
from matplotlib.font_manager import FontManager, FontProperties

from matplotlib.colors import LightSource
from mpl_poormans_3d import BarToPrism, BarToCylinder
from mpl_poormans_3d.prism_3d import BarToPathPrism, BarToCharPrism
import mpl_visual_context.patheffects as pe
import mpl_visual_context.image_effect as ie

from SecretColors import Palette
from itertools import cycle

import matplotlib.pyplot as plt

fig, ax = plt.subplots(num=1, clear=True, figsize=(8, 4))

if True:

    rs = np.random.RandomState(8)
    xnames = list("ABCDEFGHIJ")
    x = np.arange(len(xnames))
    y_ = np.arange(1, 11)
    y = rs.choice(y_, len(y_), replace=False)

    ax.set_ylabel("Qualitative")

    ax.bar(x, y)
    ax.set_xticks(x, xnames)
    ax.set_ylim(-1, 11)

    ls = LightSource(azdeg=25+90)

    material = Palette("material")
    color_names = material._value.get_all_colors().keys()

    for p, cn, c in zip(ax.patches, cycle(color_names), xnames):
        fc = material.get(cn)
        cc = [material.get(cn, shade=shade) for shade in np.arange(20, 90, 10)]
        segment_params = (ax, 10, cc, "w")

        bar_to_prism = BarToCharPrism(ls,
                                      c,
                                      rotate_deg=20,
                                      fraction=0.5,
                                      segment_params=segment_params,
                                      distance_mode=np.mean)

        p.set_path_effects([
            (bar_to_prism.get_pe_face(0)
             | pe.FillColor("k")
             | pe.ImageEffect(ie.Pad(20) | ie.Fill("k") | ie.GaussianBlur(5))),
            pe.FillColor(fc) | bar_to_prism
        ])

plt.show()
