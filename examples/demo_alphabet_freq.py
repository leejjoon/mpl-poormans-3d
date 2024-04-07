"""
====================
Demo with alphabet freqeuncy
====================
"""

import numpy as np
from pathlib import Path
from matplotlib.font_manager import FontProperties

from matplotlib.colors import LightSource
from mpl_poormans_3d import BarToCharPrism
import mpl_visual_context.patheffects as pe
import mpl_visual_context.image_effect as ie

import matplotlib.pyplot as plt

from SecretColors import Palette

fig, axs = plt.subplots(2, 1, num=1, clear=True, figsize=(15, 6), layout="constrained")

# alphabet frequency data from wikipedia : https://en.wikipedia.org/wiki/Letter_frequency

abcd = [chr(ord("A") + i) for i in range(26)]  # A - Z
freq = [8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4, 6.7, 7.5, 1.9,
        0.095, 6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074]

ax = axs[0]

x = np.arange(len(abcd))
ax.bar(x, freq)
ax.set_xticks(x, abcd)
ax.set_ylim(-1.5, 15)
ax.set_ylabel("Frequency [%]")

ls = LightSource(azdeg=25+90)

fp = FontProperties("sans serif")

import seaborn as sns
cc = sns.color_palette("husl", 26)

rs = np.random.RandomState(8)
idx = rs.choice(len(cc), len(cc), replace=False)
cc = np.array(cc)[idx]

for p, fc, c in zip(ax.patches, cc, abcd):
    # p.set_fc(color)
    bar_to_prism = BarToCharPrism(ls, c,
                                  ratio=0.6,
                                  rotate_deg=10,
                                  fraction=0.5,
                                  scale=1.2,
                                  # fontprop=fp,
                                  distance_mode=np.mean)

    p.set_path_effects([#pe.FillOnly(),
        (bar_to_prism.get_pe_face(0)
         | pe.FillColor("k")
         | pe.ImageEffect(ie.Pad(20) | ie.Fill("k") | ie.GaussianBlur(5))),
        pe.FillColor(fc) | bar_to_prism,
        (bar_to_prism.get_pe_face(1)
         | pe.FillColor("w")
         ),
    ])

# from https://story.pxd.co.kr/958, w/o double consonant
hangul_consonant = "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
hangul_freq = [11.3, 7.3, 8.0, 6.6, 5.6, 4.8, 9.1, 21.4, 8.3, 2.3, 1.6, 2.2, 1.5, 6.8]

ax = axs[1]

import mplfonts
from mplfonts.conf import FONT_DIR # , RC_DIR
from pathlib import Path
# fname = Path(FONT_DIR) / "NotoSansMonoCJKsc-Regular.otf"
fname = Path(FONT_DIR) / "NotoSerifCJKsc-Regular.otf"
# fname = Path(FONT_DIR) / "SourceHanSerifSC-Regular.otf"
fp = FontProperties(fname=fname)

x = np.arange(len(hangul_consonant))
ax.bar(x, hangul_freq)
ax.set_xticks(x, hangul_consonant, fontproperties=fp)
ax.set_ylim(-3, 25)
ax.set_ylabel("Frequency [%]")

ls = LightSource(azdeg=25+90)

import seaborn as sns

palette = Palette("material")
cnames = list(c for c in palette.colors.keys() if c not in ["black", "white"])
rs = np.random.RandomState(8)
cnames = rs.choice(cnames, len(cnames), replace=False)

for p, cn, c in zip(ax.patches, cnames, hangul_consonant):
    cc = [palette.get(cn, shade=shade) for shade in np.linspace(20, 90, 50)]
    segment_params = (ax, 25, cc, None)

    bar_to_prism = BarToCharPrism(ls, c,
                                  ratio=0.6,
                                  rotate_deg=10,
                                  fraction=0.5,
                                  scale=1.2,
                                  fontprop=fp,
                                  segment_params=segment_params,
                                  distance_mode=np.mean)

    p.set_path_effects([#pe.FillOnly(),
        (bar_to_prism.get_pe_face(0)
         | pe.FillColor("k")
         | pe.ImageEffect(ie.Pad(20) | ie.Fill("k") | ie.GaussianBlur(10))),
        pe.FillColor(fc) | bar_to_prism,
        (bar_to_prism.get_pe_face(1)
         | pe.FillColor("w")
         ),
    ])

plt.show()
