import warnings

import numpy as np

import matplotlib.colors as mcolors
from matplotlib.transforms import Affine2D
from matplotlib.patches import Polygon
from matplotlib.path import Path as MPath

# from .bezier_lite import Curve
# from .bezier_lite.hazmat_geometric_intersection import linearization_error
from bezier import Curve
from bezier.hazmat.geometric_intersection import linearization_error

# linearization_error = bezier_lite.hazmat_geometric_intersection.linearization_error

def linearize0(curve, e):
    if linearization_error(curve.nodes) > e:
        c1, c2 = curve.subdivide()
        l1 = linearize0(c1, e)
        l2 = linearize0(c2, e)
        return l1 + l2
    else:
        return [curve.nodes[:, -1]]

def linearize(curve, e):
    return [curve.nodes[:, 0]] + linearize0(curve, e)

def linearize_bezier_list(bl, e):
    verts = [bl[0].nodes[:, 0]]
    for b in bl:
        verts.append(linearize0(b, e))

    verts = np.vstack(verts)
    return verts


def bezier2mpl(curve, no_start_node=True):
    if curve.degree == 3:
        codes = [MPath.CURVE4] * 3
        verts = curve.nodes
    elif curve.degree == 2:
        codes = [MPath.CURVE3] * 2
        verts = curve.nodes
    elif curve.degree == 1:
        codes = [MPath.LINETO]
        verts = curve.nodes
    else:
        raise ValueError()

    if no_start_node:
        return verts[:, 1:], codes
    else:
        return verts, [MPath.MOVETO] + codes


def mpl2bezier(mpl_path, transform=None):
    if transform is not None:
        mpl_path = transform.transform_path(mpl_path)

    ci = iter(mpl_path.codes)
    vi = iter(mpl_path.vertices)

    beziers = [[]]
    nodes = []

    for c in ci:
        if c == MPath.MOVETO:
            nodes = [next(vi)]
            continue
        elif c == MPath.LINETO:
            degree = 1
            verts = nodes + [next(vi)]
        elif c == MPath.CURVE3:
            degree = 2
            verts = nodes + [next(vi), next(vi)]
            next(ci)
        elif c == MPath.CURVE4:
            degree = 3
            verts = nodes + [next(vi), next(vi), next(vi)]
            next(ci)
            next(ci)
        elif c == MPath.CLOSEPOLY:
            verts = nodes + [beziers[-1][0].nodes[:, 0]]
            # skip if last node is already equal to the first node.
            if np.any(verts[0] - verts[-1]):
                p = Curve(np.array(verts).T, degree=1)
                beziers[-1].append(p)
            beziers.append([])
            nodes = []
            next(vi)
            continue
        else:
            raise ValueError()

        p = Curve(np.array(verts).T, degree=degree)
        beziers[-1].append(p)
        nodes = [p.nodes[:, -1]]

    if beziers[-1]:
        return beziers
    else:
        return beziers[:-1]


def refine(cc, thresh, min_refine=100):
    if thresh == 0:
        return cc

    new_cc = [cc[0]]
    for i in range(len(cc) - 1):
        p0 = cc[i]
        p1 = cc[i+1]
        d = ((p0 - p1)**2).sum()**.5
        if d > thresh:
            n = min(int(d // thresh + 1), min_refine) # number of segmentation
            w = np.linspace(1, 0, max(2, n))[1:].reshape((-1, 1))
            pp = p0*w + p1*(1-w)
            new_cc.append(pp)
        else:
            new_cc.append(p1)

    return np.vstack(new_cc)


def lines_to_rects(lines1, lines2):
    pp = []
    for i in range(len(lines1) - 1):
        p1 = lines1[i:i+2]
        p2 = lines2[i:i+2] # [::-1]

        p = np.vstack([p1, p2[::-1]])
        pp.append(p)

    return pp


def lines_to_normals(lines):
    nn = []
    # dd = []
    for i in range(len(lines) - 1):
        dy, dx = lines[i] - lines[i+1]
        # dd.append([dy, dx])
        n = [dx, -dy]
        nn.append(n)

    nn = np.array(nn)
    with warnings.catch_warnings():
        # warnings.filterwarnings('ignore', r'RuntimeWarning: invalid value encountered')
        warnings.filterwarnings('ignore', r'invalid value encountered in divide')
        nn = nn / ((nn**2).sum(axis=1)**.5)[:, np.newaxis]
    return nn  # , np.array(dd)


def get_overlay_colors(ls, normals, facecolor, fraction=1.):
    intensity = (ls.shade_normals(normals).reshape((-1, 1)) - 0.5) * fraction + 0.5
    rgb = np.zeros((len(normals), 3))
    rgb[:] = mcolors.to_rgb(facecolor)

    rgb_overlayed = ls.blend_overlay(rgb, intensity)

    return rgb_overlayed


class PathToSimple3D:
    def __init__(self, p, error, refine_length, recenter=None):
        """
        regine_length : controls the minimum length for the line sementation.
                        We divide long straight lines into segments for better z-ordering.
        recenter : when set, it keeps a recentered path, so that scling works. Later,
                   the path will be tranlsated to the expected position.
        """
        # FIXME Check if we can use Path.to_polygons instead for linearizaion.

        if recenter is None:
            self.recenter = None
        else:
            cx, cy = self.recenter = recenter
            p = Affine2D().translate(-cx, -cy).transform_path(p)

        self.p = p

        bb = mpl2bezier(p)

        self.cc_list = []
        for b in bb:
            # b = bb[1]
            cc = linearize_bezier_list(b, error)

            # FIXME use np.hypot
            cc = refine(cc, refine_length)

            self.cc_list.append(cc)



    def get_rects(self, displacement, displacement0=0,
                  # scale0=None, scale1=None,
                  affine0=None, affine1=None,
                  distance_mode=np.mean):
        """

        returns:

        rects : list of rectangles

        projected : list of distances (for z-ordering)
        """
        rects = []
        normals = []
        projected = []

        for cc in self.cc_list:

            nn = lines_to_normals(cc)
            nnn = np.concatenate([nn, np.zeros(shape=(len(nn), 1),
                                               dtype=nn.dtype)], axis=-1)
            normals.append(nnn)

            oo0 = np.dot(cc, displacement)
            oo1 = np.dot(cc, displacement)
            oo = distance_mode([oo0[:-1], oo0[1:], oo1[:-1], oo1[1:]], axis=0)
            projected.append(oo)

            cc0 = (cc if affine0 is None else affine0.transform(cc)) + np.array(displacement0)
            cc1 = (cc if affine1 is None else affine1.transform(cc)) + np.array(displacement)
            if self.recenter is not None:
                cc0 += self.recenter
                cc1 += self.recenter

            pp = lines_to_rects(cc0, cc1)
            rects.append(pp)

        return rects, normals, projected

    def get_face(self,
                 displacement=0,
                 affine=None):
        """

        ls : lightsource
        """

        displacement = np.array(displacement)

        if self.recenter is not None:
            face_displacement = np.array(displacement) + self.recenter
        else:
            face_displacement = np.array(displacement)

        if affine is None:
            tp2 = MPath(self.p.vertices + face_displacement, codes=self.p.codes)
        else:
            tp2 = MPath(affine.transform(self.p.vertices) + face_displacement, codes=self.p.codes)

        return tp2


def path_to_simple_3d(p, error,
                      displacement,
                      displacement0 = 0,
                      distance_mode=np.mean,
                      refine_factor=0.5):
    """
    ls: lightsource
    p, tr : path and transform
    """
    # displacement = [-0.05, -0.03]
    # error = 0.001
    # rr = []
    refine_length = np.power(displacement, 2).sum()**.5 * refine_factor

    to3d = PathToSimple3D(p, error, refine_length=refine_length)
    rects, normals, projected = to3d.get_rects(displacement, displacement0=displacement0,
                                               distance_mode=distance_mode)

    return rects, normals, projected
