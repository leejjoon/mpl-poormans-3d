from matplotlib.path import Path
from matplotlib.transforms import Affine2D

from .poormans_3d import (get_3d, get_3d_face,
                          FigureDpi72, Poormans3d)

# Not sure if the name of Prism make sense here.
# https://en.wikipedia.org/wiki/Prism_(geometry)

class PrismBase(Poormans3d):
    def __init__(self, lightsource, ratio=0.4, scale=1, **kwargs):
        super().__init__(lightsource, [0, 0], **kwargs)
        self.ratio = ratio
        self.scale = scale

    def get_surface(self, width, height):
        pass
        # return surface, surface_affine

    def _get(self, tpath, affine):
        if tpath != Path.unit_rectangle():
            raise RuntimeError("path much be a unit_rect")

        tpp = affine.transform_path(tpath)
        # we get the height and the width of the bar
        height_vector = -0.5*((tpp.vertices[2]+tpp.vertices[3])
                              - (tpp.vertices[0]+tpp.vertices[1]))
        height = (height_vector**2).sum()**.5
        width = (((tpp.vertices[0]+tpp.vertices[3])
                   - (tpp.vertices[1]+tpp.vertices[2]))**2).sum()**.5*0.5

        surface, surface_affine = self.get_surface(width, height)
        surface_affine_top = surface_affine.translate(0, 1)

        return surface, surface_affine_top + affine, height_vector

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        surface, affine, height_vector = self._get(tpath, affine)

        col = get_3d(rgbFace, surface, affine, self.lightsource,
                     height_vector,
                     displacement0=[0, 0],
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

        tp2, rgb2 = get_3d_face(rgbFace, surface, affine, self.lightsource,
                                displacement=[0, 0],
                                fraction=self.fraction)
        # We need the stroke of the face to hide some of the stoke from get_3d.
        gc.set_linewidth(1)
        gc.set_foreground(rgb2)
        renderer.draw_path(gc, tp2, tr, rgb2)


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

    def get_surface(self, width, height):
        # el = Path.unit_circle()
        bar_ratio = width / height

        surface_affine = (Affine2D().scale(self.scale).
                          rotate_deg(self.rotate_deg).translate(1, 0)
                          .scale(0.5,
                                 0.5*bar_ratio*self.ratio)
                          )

        return self._surface, surface_affine

class BarToCylinder(PrismBase):
    def __init__(self, lightsource, ratio=0.4, scale=1, **kwargs):
        """

        innerCircle : only for shape of star
        """
        super().__init__(lightsource, ratio, scale=scale, **kwargs)

    def get_surface(self, width, height):
        el = Path.unit_circle()
        bar_ratio = width / height

        ellipse_affine = (Affine2D()
                          .scale(self.scale)
                          .translate(1, 0)
                          .scale(0.5,
                                 0.5*bar_ratio*self.ratio))

        return el, ellipse_affine

