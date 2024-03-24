import numpy as np
import matplotlib.transforms as mtransforms
import matplotlib.colors as mcolors
from matplotlib.collections import PolyCollection # as _PolyCollection

from .bezier_helper import (
    get_overlay_colors,
    PathToSimple3D
)


class FigureDpi72:
    def __init__(self):
        self.dpi = 72



class Poormans3dHelper:
    def __init__(self, p, error, refine_length, recenter=None):
        self.p = p
        self.tr = mtransforms.IdentityTransform()

        error = error if error else 0.1
        self.to3d = PathToSimple3D(p, error, refine_length, recenter=recenter)

    def get_side_polys(self, ls, facecolor,
                       displacement, displacement0=0,
                       direction=1,
                       fraction=0.5,
                       # scale0=None, scale1=None,
                       affine0=None, affine1=None,
                       distance_mode=np.mean):

        rects, normals, projected = self.to3d.get_rects(displacement,
                                                        displacement0=displacement0,
                                                        distance_mode=distance_mode,
                                                        affine0=affine0, affine1=affine1
                                                        # scale0=scale0, scale1=scale1
                                                        )

        facecolor = np.clip(mcolors.to_rgb(facecolor), 0.2, 0.8)
        projected_dists = []  # projected distance along the displacement vector
        polys = []
        colors = []
        for rr, nn, pp in zip(rects, normals, projected):
            msk = np.all(np.isfinite(nn), axis=-1)
            # sometimes we have zero length segment which results in nn of NaN. We
            # exclude these segments.
            rgb2 = get_overlay_colors(ls, nn, facecolor, fraction=fraction)
            polys.extend([_ for _, m in zip(rr, msk) if m])
            colors.extend(rgb2[msk])
            projected_dists.extend(direction * pp[msk])

        return projected_dists, polys, colors

    def get_side_poly_collection(self, ls, facecolor,
                                 displacement, displacement0=0,
                                 direction=1,
                                 fraction=0.5,
                                 # scale0=None, scale1=None,
                                 affine0=None, affine1=None,
                                 distance_mode=np.mean):
        """
        ls : lightsource
        """

        projected_dists, polys, colors = self.get_side_polys(
            ls, facecolor,
            displacement, displacement0=displacement0,
            direction=direction,
            fraction=fraction,
            # scale0=scale0, scale1=scale1,
            affine0=affine0, affine1=affine1,
            distance_mode=distance_mode
        )

        poly_sorted = [p1 for _, _, p1 in sorted(zip(projected_dists,
                                                     range(len(polys)), polys))]
        colors_sorted = [c1 for _, _, c1 in sorted(zip(projected_dists,
                                                       range(len(polys)), colors))]

        # we need to have lines stroked, otherwise you will see boundaries between
        # polygons. Another approach would be draw a separate lines for the
        # touching boundaries between polygons.
        pc = PolyCollection(poly_sorted, closed=True, transform=self.tr,
                            linewidths=1,
                            facecolors=colors_sorted, edgecolors=colors_sorted)

        return pc

    def get_face(self, ls, facecolor,
                 displacement=0,
                 affine=None,
                 fraction=0.5):
        """

        ls : lightsource
        """
        # self.to3d.get_face(displacement=displacement,
        #                    scale=scale)
        # displacement = np.array(displacement)

        # face_displacement = np.array(displacement)

        # if scale is None:
        #     tp2 = MPath(self.p.vertices + face_displacement, codes=self.p.codes)
        # else:
        #     tp2 = MPath(self.p.vertices*scale + face_displacement, codes=self.p.codes)

        tp2 = self.to3d.get_face(displacement=displacement, affine=affine)

        intensity = (ls.shade_normals(np.array([0, 0, 1])) - 0.5) * fraction + 0.5
        if facecolor is not None:
            rgb = np.clip(mcolors.to_rgb(facecolor), 0.1, 0.9)
            rgb2 = ls.blend_overlay(rgb, intensity)
        else:
            rgb2 = None

        return tp2, rgb2


