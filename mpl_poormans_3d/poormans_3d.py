from itertools import cycle

import numpy as np

import matplotlib.colors as mcolors
import matplotlib.transforms as mtransforms
from matplotlib.path import Path as MPath
from matplotlib.artist import Artist

from matplotlib.text import TextPath
from matplotlib.patches import Polygon
from matplotlib.patches import PathPatch
from matplotlib.colors import LightSource

from matplotlib.patheffects import AbstractPathEffect
from matplotlib.collections import PolyCollection # as _PolyCollection

from mpl_visual_context.patheffects_base import ChainablePathEffect

# from .bezier_helper import (
#     #path_to_simple_3d,
#     get_overlay_colors,
#     PathToSimple3D
# )

from .poormans_3d_helper import FigureDpi72, Poormans3dHelper


class Poormans3d(AbstractPathEffect):
    def __init__(
            self,
            lightsource,
            displacement, displacement0=(0, 0), error=None,
            direction=1,
            fraction=0.5,
            refine_factor=10):

        self.lightsource = lightsource
        self.displacement = displacement
        self.displacement0 = displacement0
        self.error = error
        self.direction = direction
        self.fraction = fraction
        self.refine_factor = refine_factor

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        dpi_cor = renderer.points_to_pixels(1)
        col = get_3d(rgbFace, tpath, affine, self.lightsource,
                     [self.displacement[0]*dpi_cor,
                      self.displacement[1]*dpi_cor],
                     displacement0=[self.displacement0[0]*dpi_cor,
                                    self.displacement0[1]*dpi_cor],
                     error=self.error,
                     direction=self.direction,
                     fraction=self.fraction,
                     refine_factor=self.refine_factor)

        # set clip on the col using gc information
        clip_path, tr = gc.get_clip_path()
        clip_rect = gc.get_clip_rectangle()

        if clip_path or clip_rect:
            col.set_clip_on(True)
            col.set_clip_box(clip_rect)
            col.set_clip_path(clip_path, tr)

        col.figure = FigureDpi72()  # draw method require self.figure.dpi. The
                                    # value does not matter unless size is set.
        col.draw(renderer)


class Poormans3dFace(ChainablePathEffect):
    def __init__(
            self,
            lightsource,
            displacement,
            fraction=0.5):

        self.lightsource = lightsource
        self.displacement = displacement
        self.fraction = fraction

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        tp = tpath.transformed(affine)
        tr = mtransforms.IdentityTransform()
        facecolor = rgbFace

        dpi_cor = renderer.points_to_pixels(1)

        displacement = np.array(self.displacement)

        tp2, rgb2 = get_3d_face(facecolor, tp, tr, self.lightsource,
                                displacement=displacement*dpi_cor,
                                fraction=self.fraction)

        # We need the stroke of the face to hide some of the stoke from get_3d.
        if gc.get_linewidth() == 0:
            gc.set_linewidth(1)
        if rgb2 is not None:
            gc.set_foreground(rgb2)

        return renderer, gc, affine.inverted().transform_path(tp2), affine, rgb2


class Catch(ChainablePathEffect):
    def __init__(self, do_not_draw=True):
        super().__init__()
        self._catched = []
        self._do_not_draw = do_not_draw

    def get_catched(self):
        return self._catched

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        self._catched.append((gc, tpath, affine, rgbFace))
        renderer = None if self._do_not_draw else renderer
        # renderer == None prevent the drawing of the path
        return renderer, gc, tpath, affine, rgbFace


# class ArtistListWithPE(Artist):
class ArtistListWithPoormans3d(Artist):
    """A simple container to filter multiple artists at once."""

    # def __init__(self, artist_list, pe):
    #     super().__init__()
    #     self._artist_list = artist_list
    #     self._pe = pe

    def __init__(self, artist_list, *kl, pe_chain=None, **kwargs):
        super().__init__()
        self._artist_list = artist_list

        # self._respect_child_patheffects = kwargs.pop("respect_child_patheffects", False)
        # set zorder
        self.set_zorder(min(a.get_zorder() for a in artist_list) - 0.01)

        self._poormans3d = Poormans3d(*kl, **kwargs)
        self._pe_chain = pe_chain

        # self._use_artist_pe = use_artist_pe

    def draw(self, renderer):
        catch = Catch()

        pe_chain_list = self._pe_chain
        if pe_chain_list is None:
            pe_chain_list = cycle([None])
        elif isinstance(pe_chain_list, ChainablePathEffect):
            pe_chain_list = cycle([pe_chain_list])

        for a, pe_chain in zip(self._artist_list, pe_chain_list):
            pe0 = a.get_path_effects()
            pe = [pe_chain | catch] if pe_chain else [catch]
            # pe = pe0 + pe if self._respect_child_patheffects else pe
            a.set_path_effects(pe)
            a.draw(renderer)
            a.set_path_effects(pe0)

        p3d = self._poormans3d
        projected_dists, polys, colors = [], [], []

        dpi_cor = renderer.points_to_pixels(1)

        for _, tpath, affine, rgbFace in catch.get_catched():

            projected_dists1, polys1, colors1 = _get_3d(
                rgbFace, tpath, affine, p3d.lightsource,
                np.array(p3d.displacement)*dpi_cor,
                displacement0=np.array(p3d.displacement0)*dpi_cor,
                error=p3d.error,
                direction=p3d.direction,
                fraction=p3d.fraction,
                refine_factor=p3d.refine_factor)

            projected_dists.extend(projected_dists1)
            polys.extend(polys1)
            colors.extend(colors1)

        poly_sorted = [p1 for _, _, p1 in sorted(zip(projected_dists,
                                                     range(len(polys)), polys))]
        colors_sorted = [c1 for _, _, c1 in sorted(zip(projected_dists,
                                                       range(len(polys)), colors))]

        tr = mtransforms.IdentityTransform()
        pc = PolyCollection(poly_sorted, closed=True, transform=tr,
                            facecolors=colors_sorted, edgecolors=colors_sorted)

        # set clip on the col using gc information
        # clip_path, tr = gc.get_clip_path()
        # clip_rect = gc.get_clip_rectangle()

        # if clip_path or clip_rect:
        #     col.set_clip_on(True)
        #     col.set_clip_box(clip_rect)
        #     col.set_clip_path(clip_path, tr)

        pc.figure = FigureDpi72()  # draw method require self.figure.dpi. The value
                               # does not matter unless size is set.
        pc.draw(renderer)


def get_3d(facecolor, p, tr, ls,
           displacement, displacement0=0, error=None,
           direction=1,
           fraction=0.5,
           refine_factor=10,
           distance_mode=np.mean):

    projected_dists, polys, colors = _get_3d(facecolor, p, tr, ls,
                                             displacement,
                                             displacement0=displacement0,
                                             error=error,
                                             direction=direction,
                                             fraction=fraction,
                                             refine_factor=refine_factor,
                                             distance_mode=distance_mode)

    poly_sorted = [p1 for _, _, p1 in sorted(zip(projected_dists,
                                                 range(len(polys)), polys))]
    colors_sorted = [c1 for _, _, c1 in sorted(zip(projected_dists,
                                                   range(len(polys)), colors))]

    tr = mtransforms.IdentityTransform()
    # we need to have lines stroked, otherwise you will se boundaries between
    # polygons. Another approach would be draw a separate lines for the
    # touching boundaries between polygons.
    pc = PolyCollection(poly_sorted, closed=True, transform=tr,
                        linewidths=1,
                        facecolors=colors_sorted, edgecolors=colors_sorted)

    return pc


def _get_3d(facecolor, p, tr, ls,
            displacement, displacement0=0, error=None,
            direction=1,
            fraction=0.5,
            refine_factor=10,
            distance_mode=np.mean):

    if error is None:
        error = 0.1

    displacement = np.array(displacement)

    tp = p.transformed(tr)
    refine_length = np.power(displacement, 2).sum()**.5 * refine_factor

    to3d = Poormans3dHelper(tp, error, refine_length=refine_length)
    projected_dists, polys, colors = to3d.get_side_polys(ls, facecolor, displacement,
                                                         displacement0=displacement0,
                                                         direction=direction,
                                                         fraction=fraction,
                                                         distance_mode=distance_mode)

    return projected_dists, polys, colors


def add_3d(ax, patch, ls,
           displacement, displacement0=0, error=0.1,
           direction=1,
           fraction=0.5,
           refine_factor=10):

    p = patch.get_path()
    tr = patch.get_transform()
    tp = p.transformed(tr)
    tr = mtransforms.IdentityTransform()
    facecolor = patch.get_fc()

    col = get_3d(facecolor, tp, tr, ls,
                 displacement=displacement, displacement0=displacement0,
                 error=error,
                 direction=direction,
                 fraction=fraction,
                 refine_factor=refine_factor)

    ax.add_collection(col)


def get_3d_face(facecolor, p, tr, ls,
                displacement=0,
                fraction=0.5):

    displacement = np.array(displacement)

    tp = p.transformed(tr)
    tr = mtransforms.IdentityTransform()

    from matplotlib.path import Path as MPath

    face_displacement = np.array(displacement)

    tp2 = MPath(tp.vertices + face_displacement, codes=tp.codes)

    intensity = (ls.shade_normals(np.array([0, 0, 1])) - 0.5) * fraction + 0.5
    if facecolor is not None:
        rgb = np.clip(mcolors.to_rgb(facecolor), 0.2, 0.8)
        rgb2 = ls.blend_overlay(rgb, intensity)
    else:
        rgb2 = None

    return tp2, rgb2


def add_3d_face(ax, patch, ls,
                displacement,
                fraction=0.5):

    p = patch.get_path()
    tr = patch.get_transform()
    tp = p.transformed(tr)
    tr = mtransforms.IdentityTransform()
    facecolor = patch.get_fc()

    displacement = np.array(displacement)

    tp2, rgb2 = get_3d_face(facecolor, p, tr, ls,
                            displacement=0,
                            fraction=0.5)

    p2 = PathPatch(tp2, ec="none", lw=1, fc=rgb2, transform=tr)

    ax.add_artist(p2)


def demo_barchart():
    import numpy as np

    import matplotlib.pyplot as plt

    # import seaborn as sns
    # df = sns.load_dataset("penguins")

    fig1, ax = plt.subplots(1, 1, num=1, clear=True, figsize=(4, 4))
    fig1.subplots_adjust(left=0.2)

    from matplotlib.patches import Circle

    t = plt.text(0.5, 0.5, "MAT", size=150, ha="center", va="center",
                 color="g")

    azdeg = 315
    ls = LightSource(azdeg=azdeg)

    t.set_path_effects([
        # Poormans3d(ls, (30, 30), displacement0=(20, 20)),
        # Poormans3d(ls, (20, 20), displacement0=(10, 10),
        #            fraction=0.3),
        Poormans3d(ls, (10, 10), displacement0=(0, 0),
                   fraction=0.3),
        # Poormans3d(ls, (20, 20), refine_factor=1),
        Poormans3dFace(ls, (0, 0)),
    ])

    plt.show()

# if True:
#     demo_barchart()

if __name__ == '__main__':
    demo_barchart()
