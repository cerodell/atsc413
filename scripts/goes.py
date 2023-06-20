from goes2go import GOES
from goes2go.data import goes_nearesttime
from goes2go.rgb import normalize, TrueColor, NaturalColor

import matplotlib.pyplot as plt


# # Get an ABI Dataset
# G = GOES().latest()

# # Create RGB and plot
# plt.imshow(G.rgb.TrueColor())

g = goes_nearesttime("2023-05-21 18:00", satellite=18, product="ABI", domain="F")

# Original TrueColor
tc = TrueColor(g, night_IR=False)

# Rick Kohrs's Natural Color
nc = NaturalColor(g, night_IR=False)

#%config InlineBackend.print_figure_kwargs = {'facecolor' : 'k'}
# %config InlineBackend.print_figure_kwargs = {'facecolor' : 'none'}
#%config InlineBackend.print_figure_kwargs = {'facecolor' : 'w'}
fig = plt.figure(figsize=(14, 6))
ax = fig.add_subplot(1, 1, 1)
ax.imshow(g.rgb.NaturalColor(), **g.rgb.imshow_kwargs)
ax.set_title("Natural Color", color="w")
ax.axis("off")
plt.subplots_adjust(wspace=0.01)
fig.set_facecolor("k")

# fig, (ax1, ax2) = plt.subplots(
#     1, 2, figsize=[20, 10], subplot_kw=dict(projection=g.rgb.crs)
# )

# for ax in [ax1, ax2]:
#     common_features(ax=ax, STATES=True)


# ax1.imshow(g.rgb.TrueColor(), **g.rgb.imshow_kwargs)
# ax1.set_title("True Color", color="w")
# ax1.axis("off")

# ax2.imshow(g.rgb.NaturalColor(), **g.rgb.imshow_kwargs)
# ax2.set_title("Natural Color", color="w")
# ax2.axis("off")

# plt.subplots_adjust(wspace=0.01)
# fig.set_facecolor("k")

# plt.savefig("../docs/_static/True-vs-Natural_color", bbox_inches="tight")
