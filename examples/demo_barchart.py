import bezier
import numpy as np

import matplotlib.pyplot as plt

from poormans_3d_demo import demo

import seaborn as sns
df = sns.load_dataset("penguins")

fig1, ax = plt.subplots(1, 1, num=1, clear=True, figsize=(4, 4))
fig1.subplots_adjust(left=0.2)

sns.barplot(data=df, x="island", y="body_mass_g", hue="sex", ax=ax)
ax.set_xlim(-0.7, 2.7)
ax.patch.set(fc="0.8", alpha=1)
ax.legend_.remove()
ax.set_title("Turn this ...")

fig2, ax = plt.subplots(1, 1, num=2, clear=True, figsize=(4, 4))
fig2.subplots_adjust(left=0.2)

sns.barplot(data=df, x="island", y="body_mass_g", hue="sex", ax=ax)
ax.set_xlim(-0.7, 2.7)
ax.patch.set(fc="0.8", alpha=1)
ax.legend_.remove()
ax.set_title("to this.")

# now we turn the figure into 3d.
patch_list_bar = [p for p in ax.patches]
for patch in patch_list_bar:
    patch.set_visible(False)
ax.patch.set_visible(False)

# outer box
demo(ax, [ax.patch],
     displacement=(15, 5),
     transformed=True, clip_on=False,
     draw_face=False, base_zorder=-20, face_location="back",
     fraction=.7, azdeg=135)
# inner box
demo(ax, [ax.patch],
     displacement=(15, 5),
     transformed=True, clip_on=True,
     draw_face=True, base_zorder=-20, face_location="back",
     fraction=0.3, azdeg=315)

demo(ax, patch_list_bar,
     displacement=(15, 5),
     transformed=True, clip_on=True, base_zorder=-10,
     azdeg=135, fraction=.5)

plt.show()
