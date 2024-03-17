import itertools

import numpy as np
from scipy.interpolate import LinearNDInterpolator, interp2d
from scipy.ndimage import convolve
from numpy import nan

import matplotlib.pyplot as plt


from fluidimage.calcul.interpolate.griddata import griddata

weights = np.ones([3, 3])


def _smooth(a, for_norm):
    norm = convolve(for_norm, weights, mode="nearest")
    ind = np.where(norm == 0)
    norm[ind] = 1
    return convolve(a, weights, mode="nearest") / norm


# fmt: off
ixvecs = np.array([116, 132, 148, 164, 180, 196, 212, 228, 244, 260, 276, 292, 308,  324, 340, 356, 372, 384])
iyvecs = np.array([ 46,  62,  78,  94, 110, 126, 142, 158, 174, 190, 206, 222, 234])

xs = np.array([116, 132, 148, 164, 180, 196, 212, 228, 244, 260, 276, 292, 308,
       324, 340, 356, 372, 384, 116, 132, 148, 164, 180, 196, 212, 228,
       244, 260, 276, 292, 308, 324, 340, 356, 372, 384, 116, 132, 148,
       164, 180, 196, 212, 228, 244, 260, 276, 292, 308, 324, 340, 356,
       372, 384, 116, 132, 148, 164, 180, 196, 212, 228, 244, 260, 276,
       292, 308, 324, 340, 356, 372, 384, 116, 132, 148, 164, 180, 196,
       212, 228, 244, 260, 276, 292, 308, 324, 340, 356, 372, 384, 116,
       132, 148, 164, 180, 196, 212, 228, 244, 260, 276, 292, 308, 324,
       340, 356, 372, 384, 116, 132, 148, 164, 180, 196, 212, 228, 244,
       260, 276, 292, 308, 324, 340, 356, 372, 384, 116, 132, 148, 164,
       180, 196, 212, 228, 244, 260, 276, 292, 308, 324, 340, 356, 372,
       384, 116, 132, 148, 164, 180, 196, 212, 228, 244, 260, 276, 292,
       308, 324, 340, 356, 372, 384, 116, 132, 148, 164, 180, 196, 212,
       228, 244, 260, 276, 292, 308, 324, 340, 356, 372, 384, 116, 132,
       148, 164, 180, 196, 212, 228, 244, 260, 276, 292, 308, 324, 340,
       356, 372, 384, 116, 132, 148, 164, 180, 196, 212, 228, 244, 260,
       276, 292, 308, 324, 340, 356, 372, 384, 116, 132, 148, 164, 180,
       196, 212, 228, 244, 260, 276, 292, 308, 324, 340, 356, 372, 384])

ys = np.array([ 46,  46,  46,  46,  46,  46,  46,  46,  46,  46,  46,  46,  46,
        46,  46,  46,  46,  46,  62,  62,  62,  62,  62,  62,  62,  62,
        62,  62,  62,  62,  62,  62,  62,  62,  62,  62,  78,  78,  78,
        78,  78,  78,  78,  78,  78,  78,  78,  78,  78,  78,  78,  78,
        78,  78,  94,  94,  94,  94,  94,  94,  94,  94,  94,  94,  94,
        94,  94,  94,  94,  94,  94,  94, 110, 110, 110, 110, 110, 110,
       110, 110, 110, 110, 110, 110, 110, 110, 110, 110, 110, 110, 126,
       126, 126, 126, 126, 126, 126, 126, 126, 126, 126, 126, 126, 126,
       126, 126, 126, 126, 142, 142, 142, 142, 142, 142, 142, 142, 142,
       142, 142, 142, 142, 142, 142, 142, 142, 142, 158, 158, 158, 158,
       158, 158, 158, 158, 158, 158, 158, 158, 158, 158, 158, 158, 158,
       158, 174, 174, 174, 174, 174, 174, 174, 174, 174, 174, 174, 174,
       174, 174, 174, 174, 174, 174, 190, 190, 190, 190, 190, 190, 190,
       190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 206, 206,
       206, 206, 206, 206, 206, 206, 206, 206, 206, 206, 206, 206, 206,
       206, 206, 206, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222,
       222, 222, 222, 222, 222, 222, 222, 222, 234, 234, 234, 234, 234,
       234, 234, 234, 234, 234, 234, 234, 234, 234, 234, 234, 234, 234])


deltaxs = np.array([-1., -1., -1.,  0.,  0.,  0.,  0.,  0.,  1.,  1.,  1.,  1.,  1.,
        2.,  2.,  2.,  2.,  2., -1., -1., -1., -1.,  0.,  0.,  0.,  0.,
        1.,  1.,  1.,  1.,  2.,  2.,  2.,  2.,  2.,  2., -1., -1., -1.,
        0.,  0.,  0.,  0.,  0.,  1.,  1.,  1.,  2.,  2.,  2.,  3.,  3.,
        3.,  2., -2., -1., -1., -1.,  0.,  0.,  0.,  0.,  1.,  1.,  1.,
        2.,  2.,  3.,  3.,  3.,  3.,  2., -1., -1., -1.,  0.,  0.,  0.,
        0.,  0.,  1.,  1.,  1.,  2.,  2.,  2.,  3.,  3.,  3.,  2., nan,
       nan, -1.,  0.,  0.,  0.,  0.,  0.,  0., nan, nan, nan, nan,  2.,
        3.,  2.,  2.,  2., nan, nan, nan,  0.,  0.,  0.,  0.,  0.,  0.,
       nan, nan, nan, nan,  1.,  1.,  1.,  1.,  1., nan, nan, nan,  0.,
        0.,  0.,  0.,  0.,  0., nan, nan, nan, nan,  0., -1., -1., -1.,
       -1., nan, nan,  0.,  0.,  0.,  0.,  0.,  0.,  0., nan, nan, nan,
       nan, -2., -2., -2., -2., -2.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,
        0.,  0., -1., -1., nan, -2., -2., -3., -3., -3., -2.,  2.,  1.,
        1.,  0.,  0.,  0.,  0.,  0., -1., -1., -1., -2., -2., -3., -3.,
       -3., -3., -2.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0., -1., -1.,
       -1., -2., -2., -2., -3., -3., -3., -2.,  1.,  1.,  1.,  0.,  0.,
        0.,  0.,  0.,  0., -1., -1., -2., -2., -2., -2., -2., -2., -2.],
      dtype=np.float32)

deltays = np.array([-2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2.,
       -1., -1., -1.,  0.,  0., -2., -2., -2., -2., -2., -2., -2., -2.,
       -2., -2., -2., -2., -2., -1., -1., -1.,  0.,  0., -2., -2., -3.,
       -3., -3., -2., -2., -3., -3., -3., -3., -2., -2., -2., -1.,  0.,
        0.,  0., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3.,
       -3., -3., -2., -1.,  0.,  0.,  1., -3., -3., -3., -3., -3., -3.,
       -3., -3., -3., -3., -3., -3., -3., -3., -1.,  0.,  1.,  2., nan,
       nan, -3., -3., -3., -3., -3., -3., -3., nan, nan, nan, nan, -3.,
       -1.,  0.,  1.,  2., nan, nan, nan, -3., -3., -3., -3., -3., -3.,
       nan, nan, nan, nan, -3., -2.,  0.,  1.,  2., nan, nan, nan, -3.,
       -3., -3., -3., -3., -3., nan, nan, nan, nan, -3., -2.,  0.,  1.,
        2., nan, nan, -3., -3., -3., -3., -3., -3., -3., nan, nan, nan,
       nan, -3., -2.,  0.,  1.,  2., -3., -3., -3., -3., -3., -3., -3.,
       -3., -3., -3., -3., nan, -3., -3., -2.,  0.,  1.,  1., -3., -3.,
       -3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -2., -1.,
        0.,  0.,  1., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3.,
       -3., -3., -2., -2., -1., -1.,  0.,  1., -2., -2., -2., -2., -2.,
       -3., -2., -2., -2., -2., -2., -2., -2., -2., -1., -1.,  0.,  0.],
      dtype=np.float32)
# fmt: on

threshold = 8


# def smooth_clean(xs, ys, deltaxs, deltays, iyvecs, ixvecs, threshold):
nx = len(ixvecs)
ny = len(iyvecs)

shape = [ny, nx]
for_norm = np.ones(shape)

selection = ~(np.isnan(deltaxs) | np.isnan(deltays))
if not selection.any():
    raise RuntimeError

centers = np.vstack([xs[selection], ys[selection]])
dxs_select = deltaxs[selection]
dys_select = deltays[selection]
dxs = griddata(centers, dxs_select, (ixvecs, iyvecs)).reshape([ny, nx])
dys = griddata(centers, dys_select, (ixvecs, iyvecs)).reshape([ny, nx])

dxs2 = _smooth(dxs, for_norm)
dys2 = _smooth(dys, for_norm)

inds = (abs(dxs2 - dxs) + abs(dys2 - dys) > threshold).nonzero()

dxs[inds] = 0
dys[inds] = 0
for_norm[inds] = 0

dxs_smooth = _smooth(dxs, for_norm)
dys_smooth = _smooth(dys, for_norm)

# come back to the unstructured grid

xy = list(itertools.product(ixvecs, iyvecs))
interpolator_x = LinearNDInterpolator(xy, dxs_smooth.T.flat)
interpolator_y = LinearNDInterpolator(xy, dys_smooth.T.flat)
out_dxs_new = interpolator_x(xs, ys)
out_dys_new = interpolator_y(xs, ys)

fxs = interp2d(ixvecs, iyvecs, dxs_smooth, kind="linear")
fys = interp2d(ixvecs, iyvecs, dys_smooth, kind="linear")
out_dxs = np.empty_like(deltaxs)
out_dys = np.empty_like(deltays)
for i, (x, y) in enumerate(zip(xs, ys)):
    out_dxs[i] = fxs(x, y)[0]
    out_dys[i] = fys(x, y)[0]


fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.scatter(xs, ys, deltaxs, 'o', color='k', s=20)

ax.scatter(xs, ys, out_dxs, 'o', color='r', s=20)

ax.scatter(xs, ys, out_dxs_new, 'o', color='g', s=20)
