import numpy as np
from matplotlib.transforms import Affine2D

from matplotlib.textpath import text_to_path, FontProperties
from matplotlib.text import TextPath as _TextPath
from matplotlib.path import Path

# Variation of mpl's TextPath that support ha & va.

class TextPath(_TextPath):
    """
    Create a path from the text.
    """

    def __init__(self, xy, s, size=None, prop=None,
                 _interpolation_steps=1, usetex=False,
                 ha="left", va="baseline"):
        r"""
        Create a path from the text. Note that it simply is a path,
        not an artist. You need to use the `.PathPatch` (or other artists)
        to draw this path onto the canvas.

        Parameters
        ----------
        xy : tuple or array of two float values
            Position of the text. For no offset, use ``xy=(0, 0)``.

        s : str
            The text to convert to a path.

        size : float, optional
            Font size in points. Defaults to the size specified via the font
            properties *prop*.

        prop : `matplotlib.font_manager.FontProperties`, optional
            Font property. If not provided, will use a default
            ``FontProperties`` with parameters from the
            :ref:`rcParams<customizing-with-dynamic-rc-settings>`.

        _interpolation_steps : int, optional
            (Currently ignored)

        usetex : bool, default: False
            Whether to use tex rendering.

        Examples
        --------
        The following creates a path from the string "ABC" with Helvetica
        font face; and another path from the latex fraction 1/2::

            from matplotlib.text import TextPath
            from matplotlib.font_manager import FontProperties

            fp = FontProperties(family="Helvetica", style="italic")
            path1 = TextPath((12, 12), "ABC", size=12, prop=fp)
            path2 = TextPath((0, 0), r"$\frac{1}{2}$", size=12, usetex=True)

        Also see :doc:`/gallery/text_labels_and_annotations/demo_text_path`.
        """
        # Circular import.
        from matplotlib.text import Text

        prop = FontProperties._from_any(prop)
        if size is None:
            size = prop.get_size_in_points()

        self._xy = xy
        self.set_size(size)

        self._cached_vertices = None
        s, ismath = Text(usetex=usetex)._preprocess_math(s)
        # test path is created using FONT_SCALE
        v, c = text_to_path.get_text_path(prop, s, ismath=ismath)
        # whd is calculated using prop.get_size_in_points()
        # *100/prop.get_size_in_points()
        _whd = text_to_path.get_text_width_height_descent(s, prop, ismath)

        prop_size = prop.get_size_in_points()
        self.whd = [_*text_to_path.FONT_SCALE/prop_size for _ in _whd]
        Path.__init__(
            self, np.array(v) , c,
            _interpolation_steps=_interpolation_steps,
            readonly=True)
        self._should_simplify = False

        self._ha = ha
        self._va = va

    def _revalidate_path(self):
        """
        Update the path if necessary.

        The path for the text is initially create with the font size of
        `.FONT_SCALE`, and this path is rescaled to other size when necessary.
        """
        if self._invalid or self._cached_vertices is None:
            w, h, d = self.whd
            dx = dict(left=0, right=-w, center=-w/2)[self._ha]
            dy = dict(baseline=0, top=-h, bottom=d, center=d -h/2.)[self._va]
            tr = (Affine2D()
                  # ha=va=center! Should be an option
                  .translate(dx, dy)
                  .scale(self._size / text_to_path.FONT_SCALE)
                  .translate(*self._xy)
                  )
            self._cached_vertices = tr.transform(self._vertices)
            self._cached_vertices.flags.writeable = False
            self._invalid = False
