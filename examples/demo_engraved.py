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
from mpl_visual_context.patheffects import Offset, Affine, StrokeColor, StrokeOnly, GCModify
import mpl_visual_context.patheffects as pe

fig, ax = plt.subplots(num=1, clear=True)

t = ax.text(0.5, 0.65, "a", ha="center", va="center", size=500, color='C0')

ls = LightSource(azdeg=0)
ls2 = LightSource(azdeg=180+35)
kw = dict(fraction=0.6)
pe3d = Poormans3d(ls, (0, -15), direction=1, **kw)
pe3d_face = Poormans3dFace(ls2, (0, -15), **kw)
pe_affine = pe.Affine().scale(1, 0.8)
t.set_path_effects([pe_affine | pe.ClipPathSelf() | pe3d_face,
                    pe_affine | pe.ClipPathSelf() | pe3d,
                    pe_affine | StrokeColor("w") | GCModify(linewidth=1)
                    | StrokeOnly()

                    ])
plt.show()
