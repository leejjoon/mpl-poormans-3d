import itertools
from sys import displayhook
import numpy as np

from matplotlib.path import Path
from matplotlib.transforms import Affine2D, IdentityTransform
import matplotlib.colors as mcolors
from mpl_visual_context.patheffects_base import ChainablePathEffect

from .text_path import TextPath

from .poormans_3d_helper import FigureDpi72, Poormans3dHelper
# from .poormans_3d import (
#     # get_3d, get_3d_face,
#     FigureDpi72,
#     Poormans3dHelper,
#     # Poormans3d
# )

# Not sure if the name of Prism make sense here.
# https://en.wikipedia.org/wiki/Prism_(geometry)

class PrismBase:
    def __init__(self, lightsource, ratio=0.4, scale=1,
                 error=None,
                 direction=-1,
                 fraction=0.5,
                 segment_params=None,
                 distance_mode=np.max):
        """
        segment_params : ax, max_height, colors, facecolor. If colors is None, rgbFace will be used and the max_height parameter will be ignored.
        """
        self.lightsource = lightsource
        self.error = error
        self.direction = direction
        self.fraction = fraction

        self.ratio = ratio
        self.scale = scale

        self.segment_params = segment_params
        self.distance_mode=distance_mode
        # segment_params=(ax, max_height, colors)

    def _get_surface(self, width, height):
        pass
        # return surface, surface_affine

    def _get(self, tpath, affine):

        tpp = affine.transform_path(tpath)
        # we get the height and the width of the bar
        height_vector = 0.5*((tpp.vertices[2]+tpp.vertices[3])
                              - (tpp.vertices[0]+tpp.vertices[1]))
        height = (height_vector**2).sum()**.5
        width = (((tpp.vertices[0]+tpp.vertices[3])
                   - (tpp.vertices[1]+tpp.vertices[2]))**2).sum()**.5*0.5

        surface, surface_affine = self._get_surface(width, height)
        # surface_affine_top = surface_affine.translate(0, 1)

        return surface, surface_affine + affine, height_vector

    def _get_height_in_data(self, screen_to_data, tpath, affine):

        #tpp = tpath
        tpp = affine.transform_path(tpath)
        tpp = screen_to_data.transform_path(tpp)
        # we get the height and the width of the bar
        height_vector = -0.5*((tpp.vertices[2]+tpp.vertices[3])
                              - (tpp.vertices[0]+tpp.vertices[1]))
        height = (height_vector**2).sum()**.5

        return height

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        if tpath != Path.unit_rectangle():
            raise RuntimeError("path much be a unit_rect")

        # The unit_rectangle has (0, 0) at botton left and (1, 1) at top right.
        # We change the path and affine so that the surface has a center at 0,
        # 0 and that corresponds to the bottom center of the bar.
        tpath  = Affine2D().translate(-0.5, 0).transform_path(tpath)
        affine = Affine2D().translate(0.5, 0) + affine

        rgbFace0 = rgbFace
        if self.segment_params:
            ax, max_height, colors, rgbFace_ = self.segment_params[:4]
            if len(self.segment_params) == 5:
                affines = self.segment_params[-1]
            else:
                affines = itertools.repeat((None, None))

            rgbFace = rgbFace if rgbFace_ is None else rgbFace_
            # if colors is None:
            #     colors = itertools.repeat([rgbFace])
            #     n_segment = 1
            # else:
            #     n_segment = len(colors)

            height_in_data = self._get_height_in_data(ax.transData.inverted(),
                                                      tpath, affine)

            n_segment = len(colors)
            # max_height = 20
            max_n = height_in_data / max_height * n_segment

            div = np.floor(max_n)
            v1 = np.arange(0, div + 1, 1)[:n_segment]
            v2 = np.concatenate([v1[:-1] + 1, [max_n]])

            # iter_segment = zip(1-v2/max_n, 1-v1/max_n, colors)
            iter_segment = zip(v1/max_n, v2/max_n, colors, affines)
        else:
            iter_segment = [(0, 1, rgbFace, (None, None))]

        surface, affine, height_vector = self._get(tpath, affine)
        # set clip on the col using gc information
        clip_path, tr = gc.get_clip_path()
        clip_rect = gc.get_clip_rectangle()

        tsurface = affine.transform_path(surface)
        # refine_length = np.power(height_vector, 2).sum()**.5 * self.refine_factor
        # FIXME Not sure if refine_length really matter
        refine_length = 10
        center = affine.transform_point([0, 0])
        to3d = Poormans3dHelper(tsurface, self.error, refine_length=refine_length,
                                recenter=center)

        # print("##", next(iter(iter_segment)))
        for d0, d1, c, (a0, a1) in iter_segment:
            # d1, d2 : distances
            # c : color
            # a0, a1 : affine transfomrs. can be None.
            c = rgbFace0 if c is None else c

            col = to3d.get_side_poly_collection(
                self.lightsource, c,
                height_vector*d1,
                displacement0=height_vector*d0,
                direction=self.direction,
                fraction=self.fraction,
                # scale0=1, scale1=0.5,
                affine0=a0, affine1=a1,
                distance_mode=self.distance_mode)

            if clip_path or clip_rect:
                col.set_clip_on(True)
                col.set_clip_box(clip_rect)
                col.set_clip_path(clip_path, tr)

            col.figure = FigureDpi72()  # draw method require self.figure.dpi. The
                                        # value does not matter unless size is set.
            col.draw(renderer)

            tp2, rgb2 = to3d.get_face(self.lightsource, c,
                                      displacement=height_vector*d1,
                                      affine=a1,
                                      # scale=scale,
                                      fraction=self.fraction)
            # tp2, rgb2 = get_3d_face(rgbFace, surface, affine, self.lightsource,
            #                         displacement=[0, 0],
            #                         fraction=self.fraction)
            # We need the stroke of the face to hide some of the stoke from get_3d.
            gc.set_linewidth(1)
            gc.set_foreground(rgb2)
            renderer.draw_path(gc, tp2, tr, rgb2)

        # if rgbFace is None:
        #     rgbFace = c

        # scale = 0.5
        # if not scale:
        #     return

        # tp2, rgb2 = to3d.get_face(self.lightsource, rgbFace,
        #                           displacement=height_vector,
        #                           affine=a1,
        #                           # scale=scale,
        #                           fraction=self.fraction)
        # # tp2, rgb2 = get_3d_face(rgbFace, surface, affine, self.lightsource,
        # #                         displacement=[0, 0],
        # #                         fraction=self.fraction)
        # # We need the stroke of the face to hide some of the stoke from get_3d.
        # gc.set_linewidth(1)
        # gc.set_foreground(rgb2)
        # renderer.draw_path(gc, tp2, tr, rgb2)
        # # import matplotlib.colors as mcolors
        # # renderer.draw_path(gc, tp2, tr, mcolors.to_rgb(rgbFace))

    class FacePath(ChainablePathEffect):
        def __init__(self, prism, displacement):
            self.prism = prism
            self.displacement = displacement

        def _convert(self, renderer, gc, tpath, affine, rgbFace=None):

            prism = self.prism
            if prism.segment_params:
                ax, max_height, colors, rgbFace = prism.segment_params
                height_in_data = prism._get_height_in_data(ax.transData.inverted(),
                                                           tpath, affine)

                n_segment = len(colors)
                max_n = height_in_data / max_height * n_segment

                div = int(np.floor(max_n))
                rgbFace = mcolors.to_rgb(colors[div])

            # The unit_rectangle has (0, 0) at botton left and (1, 1) at top right.
            # We change the path and affine so that the surface has a center at 0,
            # 0 and that corresponds to the bottom center of the bar.
            tpath  = Affine2D().translate(-0.5, 0).transform_path(tpath)
            affine = Affine2D().translate(0.5, 0) + affine

            surface, affine, height_vector = prism._get(tpath, affine)

            tsurface = affine.transform_path(surface)
            # refine_length = np.power(height_vector, 2).sum()**.5 * self.refine_factor
            # FIXME Not sure if refine_length really matter
            refine_length = 10

            to3d = Poormans3dHelper(tsurface, prism.error, refine_length=refine_length)

            tr = IdentityTransform()

            tp2, rgb2 = to3d.get_face(prism.lightsource, rgbFace,
                                      displacement=height_vector*self.displacement,
                                      fraction=prism.fraction)

            # We need the stroke of the face to hide some of the stoke from get_3d.
            gc2 = renderer.new_gc()  # Don't modify gc, but a copy!
            gc2.copy_properties(gc)

            gc2.set_linewidth(1)
            if rgbFace:
                gc2.set_foreground(rgb2)

            return renderer, gc2, tp2, tr, rgb2

    def get_pe_face(self, displacement=0):
        pe_face = self.FacePath(self, displacement)
        return pe_face


class BarToPrism(PrismBase):
    def __init__(self, lightsource, numVertices, ratio=0.4, scale=1,
                 shape="polygon", innerCircle=0.5,
                 rotate_deg=0, **kwargs):
        """

        innerCircle : only for shape of star
        """
        super().__init__(lightsource, ratio, scale=scale, **kwargs)
        self.rotate_deg = rotate_deg
        self.numVertices = numVertices
        if shape == "star":
            self._surface = Path.unit_regular_star(numVertices,
                                                   innerCircle)
        elif shape == "asterisk":
            self._surface = Path.unit_regular_asterisk(numVertices)
        elif shape == "polygon":
            self._surface = Path.unit_regular_polygon(numVertices)
        else:
            raise ValueError(f"unknown shape: {shape}")

    def _get_surface(self, width, height):
        # el = Path.unit_circle()
        bar_ratio = width / height

        surface_affine = (Affine2D().scale(self.scale).
                          rotate_deg(self.rotate_deg)
                          .scale(0.5,
                                 0.5*bar_ratio*self.ratio)
                          )

        return self._surface, surface_affine

    # def _get_unit_surface(self, width, height):
    #     # el = Path.unit_circle()
    #     bar_ratio = width / height

    #     surface_affine = (Affine2D().scale(self.scale).
    #                       rotate_deg(self.rotate_deg).translate(1, 0)
    #                       .scale(0.5,
    #                              0.5*bar_ratio*self.ratio)
    #                       ).scale(0.2)

    #     return self._surface, surface_affine

class BarToCylinder(PrismBase):
    def __init__(self, lightsource, ratio=0.4, scale=1, **kwargs):
        """

        innerCircle : only for shape of star
        """
        super().__init__(lightsource, ratio, scale=scale, **kwargs)

    def _get_surface(self, width, height):
        el = Path.unit_circle()
        bar_ratio = width / height

        ellipse_affine = (Affine2D()
                          .scale(self.scale)
                          .scale(0.5,
                                 0.5*bar_ratio*self.ratio))

        return el, ellipse_affine


class BarToCharPrism(PrismBase):
    def __init__(self, lightsource, ch, ratio=0.4, scale=1,
                 rotate_deg=0, fontprop=None, **kwargs):
        """

        innerCircle : only for shape of star
        """
        super().__init__(lightsource, ratio, scale=scale, **kwargs)
        self.rotate_deg = rotate_deg

        self._surface = TextPath((0, 0), ch, prop=fontprop, size=100,
                                 ha="center", va="center")

        # self.ax = ax

    def _get_surface(self, width, height):
        # el = Path.unit_circle()
        bar_ratio = width / height

        surface_affine = (Affine2D().scale(self.scale/100)
                          .rotate_deg(self.rotate_deg)
                          # .translate(0.5, 0.)
                          .scale(1,
                                 bar_ratio*self.ratio)
                          )

        return self._surface, surface_affine


class BarToPathPrism(PrismBase):
    def __init__(self, lightsource, path, ratio=0.4, scale=1,
                 rotate_deg=0, **kwargs):
        """

        innerCircle : only for shape of star
        """
        super().__init__(lightsource, ratio, scale=scale, **kwargs)
        self.rotate_deg = rotate_deg

        self._surface = path

    def _get_surface(self, width, height):
        # el = Path.unit_circle()
        bar_ratio = width / height

        surface_affine = (Affine2D().scale(self.scale)
                          .rotate_deg(self.rotate_deg)
                          .translate(0.5, 0.)
                          .scale(1,
                                 bar_ratio*self.ratio)
                          )

        return self._surface, surface_affine
