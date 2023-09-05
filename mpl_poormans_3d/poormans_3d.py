import numpy as np

import matplotlib.colors as mcolors
import matplotlib.transforms as mtransforms

from matplotlib.text import TextPath
from matplotlib.patches import Polygon
from matplotlib.patches import PathPatch

from bezier_helper import (path_to_simple_3d,
                           get_overlay_colors)

from matplotlib.colors import LightSource


def demo(ax, patch_list,
         displacement, error=None,
         transformed=False, clip_on=None,
         direction=1,
         draw_face=True, base_zorder=10,
         face_location=None,
         fraction=0.5,
         azdeg=315,
         refine_factor=10):


    ls = LightSource(azdeg=azdeg)
    if error is None:
        if transformed:
            error = 0.5
        else:
            error = 0.001

    displacement = np.array(displacement)

    projected_dists = []  # projected distance along the displacement vector
    polys = []
    for i, p in enumerate(patch_list):
        if transformed:
            tp = p.get_path()
            tr = p.get_transform()
            tp = tp.transformed(tr)
            tr = mtransforms.IdentityTransform()
        else:
            tp = p.get_path()
            tr = p.get_transform()

        facecolor = p.get_fc()
        rects, normals, projected = path_to_simple_3d(tp,
                                                      displacement, error,
                                                      refine_factor=refine_factor)

        for rr, nn, pp in zip(rects, normals, projected):
            rgb2 = get_overlay_colors(ls, nn, facecolor, fraction=fraction)
            # print(rgb2)
            # # print(len(pp), len(nn))
            # for p1, n1 in zip(pp, nn):
            #     vv = np.array([p1[0], p1[0] + n1])
            #     ax.plot(vv[:, 0], vv[:, 1], "-")

            for p1, color in zip(rr, rgb2):
                pol = Polygon(p1, fc=color, ec=color, clip_on=clip_on,
                              zorder=base_zorder, transform=tr)
                # print(p1)
                polys.append(pol)

            # projected_dists = .extend(pp)
            projected_dists.append(pp)

    # projected = np.concatenate(projected_dists, axis=-1)
    # simple z-sorting
    # range is to make the sort stable without comparing the polygons
    for z, _, rect in sorted(zip(direction * np.concatenate(projected_dists,
                                                            axis=-1),
                                 range(len(polys)), polys)):
        ax.add_patch(rect)

    if not draw_face:
        return

    for i, p in enumerate(patch_list):
        if transformed:
            tp = p.get_path()
            tr = p.get_transform()
            tp = tp.transformed(tr)
            tr = mtransforms.IdentityTransform()
        else:
            tp = p.get_path()
            tr = p.get_transform()
        facecolor = p.get_fc()

        from matplotlib.path import Path as MPath
        if face_location == "front":
            face_displacement = displacement * (1 - direction) * 0.5
        elif face_location == "back":
            face_displacement = displacement * (direction + 1) * 0.5
        else:
            if direction == -1:
                face_displacement = displacement
            else:
                face_displacement = 0

        tp2 = MPath(tp.vertices + face_displacement, codes=tp.codes)

        intensity = (ls.shade_normals(np.array([0, 0, 1])) - 0.5) * fraction + 0.5
        rgb = np.array(mcolors.to_rgb(facecolor))
        rgb2 = ls.blend_overlay(rgb, intensity)

        p2 = PathPatch(tp2, ec="none", lw=1, fc=rgb2, clip_on=clip_on,
                       zorder=base_zorder+1, transform=tr)
        ax.add_artist(p2)
