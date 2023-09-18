import numpy as np
from mpl_visual_context.patheffects_transform import Skew


# Because of its dependency on mpl_visual_context, we place this module
# in mpl_poormans_3d, not in mpl_axisline_newapi.

class SkewedLabel:
    """
        skewed = SkewedLabel(transform_from_aux)

        axis.label.set_path_effects([skewed.label(direction)])
        axis.major_ticklabels.set_path_effects([skewed.ticklabel(direction)])

    """
    def __init__(self, transform_from_aux):
        tr = transform_from_aux
        x0, y0 = tr.transform_point([0, 0])
        x1, y1 = tr.transform_point([1, 0])
        x2, y2 = tr.transform_point([0, 1])

        angle_x = np.arctan2(x1 - x0, y1 - y0) / np.pi * 180
        angle_y = np.arctan2(x2 - x0, y2 - y0) / np.pi * 180

        self.shear = (angle_y - angle_x - 90)
        # self.yShear = (angle_y - angle_x - 90)

    def label(self, loc):
        if loc in ["bottom", "top"]:
            return Skew(self.shear, 0)
        else:
            return Skew(-self.shear, 0)

    def ticklabel(self, loc):
        if loc in ["bottom", "top"]:
            return Skew(0, self.shear)
        else:
            return Skew(self.shear, 0)


def skew_labels_n_ticklabels(floating_axes, floating_axis,
                             transform_from_aux):
    orig_axis_dict = dict(left=floating_axes.yaxis,
                          right=floating_axes.yaxis,
                          bottom=floating_axes.xaxis,
                          top=floating_axes.xaxis)

    skewed = SkewedLabel(transform_from_aux)

    # This is to support floating axis in the form of ax.axis["left", "right"]
    # which is from axisartist.
    if hasattr(floating_axis, "_objects"):
        floating_axis = dict((axis._axis_direction, axis)
                             for axis in floating_axis._objects)

    for direction, axis in floating_axis.items():

        # axis = floating_axes.axis[direction]
        axis.label.set_path_effects([skewed.label(direction)])
        axis.major_ticklabels.set_path_effects([skewed.ticklabel(direction)])
