import bezier
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.transforms as mtransforms

from matplotlib.text import TextPath
from matplotlib.patches import Polygon

from bezier_helper import (linearize_bezier_list,
                           lines_to_rects,
                           lines_to_normals,
                           refine,
                           mpl2bezier,
                           path_to_simple_3d,
                           get_overlay_colors)


# patch.set_fc("none")

def patches_to_simple_3d(patches):
    pass


from matplotlib.patches import PathPatch

from matplotlib.colors import LightSource


def demo(ax, patch_list, transformed=False, clip_on=None,
         direction=1,
         draw_face=True, base_zorder=10,
         face_location=None,
         fraction=0.5,
         azdeg=315,
         refine_factor=10):


    if transformed:
        ls = LightSource(azdeg=azdeg)
        displacement = np.array((15, 10))
        # direction=1
        error = 1
        if clip_on is None:
            clip_on = True
    else:
        ls = LightSource(azdeg=azdeg)
        displacement = np.array((-0.05, -0.05))
        # direction=-1
        error = 0.001
        if clip_on is None:
            clip_on = False

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

# ax.plot(tp.vertices[:, 0], tp.vertices[:, 1], "o")

# l2 = np.vstack(linearize(curve2, 0.005))
# ax.plot(l2[:, 0], l2[:, 1], "o-")

fig, axs = plt.subplots(1, 3, num=1, clear=True, figsize=(12, 4))
fig.subplots_adjust(wspace=0.4)

ax = axs[0]
ax.set_aspect(1.)
tp = TextPath((0, 0), "Hi", size=0.7, prop=dict(family="serif"))
p = PathPatch(tp, ec="none",
              # fc=(0.8, 0, 0),
              fc="y",
              clip_on=False,
              transform=ax.transData)
patch_list = [p]

demo(ax, patch_list, base_zorder=10, direction=-1, fraction=1.,
     refine_factor=1)

import seaborn as sns
df = sns.load_dataset("penguins")
ax = axs[1]

sns.barplot(data=df, x="island", y="body_mass_g", hue="sex", ax=ax)
ax.set_xlim(-0.7, 2.7)
patch_list_bar = [p for p in ax.patches]
for patch in patch_list:
    patch.set_visible(False)
ax.legend_.remove()

ax.patch.set_visible(False)
ax.patch.set(fc="0.8", alpha=1)

# outer box
demo(ax, [ax.patch], transformed=True, clip_on=False,
     draw_face=False, base_zorder=-20, face_location="back",
     fraction=.7, azdeg=135)
# inner box
demo(ax, [ax.patch], transformed=True, clip_on=True,
     draw_face=True, base_zorder=-20, face_location="back",
     fraction=0.3, azdeg=315)

demo(ax, patch_list_bar, transformed=True, clip_on=True, base_zorder=-10,
     azdeg=135, fraction=.5)


# ax = axs[1]
# ax.patch.set(fc=(0.5, 0.5, 0.5), visible=False)
# patch_list = [ax.patch]
# demo(ax, patch_list, transformed=True, clip_on=False, draw_face=False)

# sns.barplot(data=df, x="island", y="body_mass_g", ax=ax)



# the normal vector direction is sensitive to the direction of the path. So, for the path below, we invert its direction, which becomes clockwise...?

# tp = Polygon(np.array([[0.1, 0.4, 0.4, 0.1],
#                        [0.1, 0.1, 0.4, 0.4]]).T[::-1])

# ax = axs[1]
# ax.set_aspect(1)
# ax.add_patch(tp)

ax = axs[2]
frequency = [120,120,380,240,200]
pie = ax.pie(frequency,
       startangle=90,
       counterclock=False,
       wedgeprops=dict(width=0.3)
       )
patch_list = pie[0]
for patch in patch_list:
    patch.set_visible(False)

demo(ax, patch_list, direction=-1, azdeg=135, fraction=1)

plt.show()
