"""
====================
Simple engraved example
====================
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from matplotlib.colors import LightSource
from mpl_poormans_3d import Poormans3d, Poormans3dFace
from mpl_visual_context.patheffects import Offset, Affine
import mpl_visual_context.patheffects as pe

fig, ax = plt.subplots(num=1, clear=True)

t = ax.text(0.5, 0.5, "a", ha="center", va="center", size=200, color='C4')

ls = LightSource(azdeg=0)
ls2 = LightSource(azdeg=180+35)
kw = dict(fraction=0.6)
pe3d = Poormans3d(ls, (0, -10), direction=1, **kw)
pe3d_face = Poormans3dFace(ls2, (0, -10), **kw)
pe_affine = pe.Affine().scale(1, 0.6)
t.set_path_effects([pe_affine | pe.ClipPathSelf() | pe3d_face,
                    pe_affine | pe.ClipPathSelf() | pe3d,
                    ])
plt.show()
