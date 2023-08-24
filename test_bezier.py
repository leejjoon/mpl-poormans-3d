import bezier
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from matplotlib.text import TextPath
from matplotlib.patches import Polygon

from bezier_helper import (linearize_bezier_list,
                           lines_to_rects,
                           lines_to_normals,
                           refine,
                           mpl2bezier)


# patch.set_fc("none")

def patches_to_simple_3d(patches):
    pass

def path_to_simple_3d(ls, p, facecolor, displacement, error,
                      refine_factor=0.5):
    # displacement = [-0.05, -0.03]
    # error = 0.001
    rr = []
    projected = []
    bb = mpl2bezier(p)

    for b in bb:
        # b = bb[1]
        cc = linearize_bezier_list(b, error)

        # long lines are divided for better z-ordering.
        cc = refine(cc, np.power(displacement, 2).sum()**.5 * refine_factor)


        # cc = np.array([ccx, ccy]).T
        # ax.plot(cc[:, 0], cc[:, 1], "o")

        cc2 = cc + displacement
        # ax.plot(cc2[:, 0], cc2[:, 1], "ko", zorder=100)

        pp = lines_to_rects(cc, cc2)
        nn = lines_to_normals(cc)
        nnn = np.concatenate([nn, np.zeros(shape=(len(nn), 1),
                                           dtype=nn.dtype)], axis=-1)
        fraction = 1.
        intensity = (ls.shade_normals(nnn).reshape((-1, 1)) - 0.5) * fraction + 0.5
        rgb = np.zeros((len(nnn), 3))
        rgb[:] = mcolors.to_rgb(facecolor)

        rgb2 = ls.blend_overlay(rgb, intensity)

        # print(rgb2)
        # # print(len(pp), len(nn))
        # for p1, n1 in zip(pp, nn):
        #     vv = np.array([p1[0], p1[0] + n1])
        #     ax.plot(vv[:, 0], vv[:, 1], "-")

        for p1, color in zip(pp, rgb2):
            rect = Polygon(p1, fc=color, ec=color, clip_on=False,
                           zorder=10, transform=tr)
            # print(p1)
            rr.append(rect)

        # mean
        oo1 = np.dot(cc, displacement)
        oo2 = np.dot(cc2, displacement)
        # oo = np.sum([oo1[:-1], oo1[1:], oo2[:-1], oo2[1:]], axis=0)
        oo = np.mean([oo1[:-1], oo1[1:], oo2[:-1], oo2[1:]], axis=0)
        # oo = np.dot(cc[:-1], displacement)
        projected.append(-oo)

    return projected, rr

fig, ax = plt.subplots(num=1, clear=True)
from matplotlib.patches import PathPatch

# tp = TextPath((0, 0), "fi", size=0.5)
# p = PathPatch(tp, ec="none", lw=1, fc=(0.8, 0, 0), clip_on=False,
#               transform=ax.transData)
# path_list = [p]

# the normal vector direction is sensitive to the direction of the path. So, for the path below, we invert its direction, which becomes clockwise...?

# tp = Polygon(np.array([[0.1, 0.4, 0.4, 0.1],
#                        [0.1, 0.1, 0.4, 0.4]]).T[::-1]).get_path()

frequency = [120,120,380,240,200]
pie = ax.pie(frequency,
       startangle=90,
       counterclock=False,
       wedgeprops=dict(width=0.3)
       )
path_list = pie[0]

from matplotlib.colors import LightSource
ls = LightSource(azdeg=315)

displacement0 = (-0.05, -0.05)
error = 0.001

projected = []
rr = []
for i, p in enumerate(path_list):
    # displacement = displacement0[0] * (i+1), displacement0[1] * (i+1)
    displacement = displacement0 #[0] * (7-i+1), displacement0[1] * (7-i+1)
    tp = p.get_path()
    tr = p.get_transform()
    facecolor = p.get_fc()
    _projected, _rr = path_to_simple_3d(ls, tp, facecolor,
                                        displacement, error,
                                        refine_factor=0.1)
    projected.extend(_projected)
    rr.extend(_rr)

# simple z-sorting
# range is to make the sort stable without comparing the polygons
for z, _, rect in sorted(zip(np.concatenate(projected), range(len(rr)), rr)):
    ax.add_patch(rect)

for i, p in enumerate(path_list):
    displacement = displacement0# [0]  * (7-i+1), displacement0[1] * (7-i+1)
    tp = p.get_path()
    tr = p.get_transform()
    facecolor = p.get_fc()

    # tp = Polygon(np.array([[0.1, 0.4, 0.4, 0.1, 0.1],
    #                        [0.1, 0.1, 0.4, 0.4, 0.1]]).T).get_path()
    from matplotlib.path import Path as MPath
    tp2 = MPath(tp.vertices + displacement, codes=tp.codes)
    # tp = TextPath(displacement, "o", size=1)

    fraction = 1.
    intensity = (ls.shade_normals(np.array([0, 0, 1])) - 0.5) * fraction + 0.5
    rgb = np.array(mcolors.to_rgb(facecolor))
    rgb2 = ls.blend_overlay(rgb, intensity)

    p2 = PathPatch(tp2, ec="none", lw=1, fc=rgb2, clip_on=False,
                   zorder=20, transform=tr)
    ax.add_artist(p2)

# ax.plot(tp.vertices[:, 0], tp.vertices[:, 1], "o")

# l2 = np.vstack(linearize(curve2, 0.005))
# ax.plot(l2[:, 0], l2[:, 1], "o-")

plt.show()
