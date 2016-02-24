
from __future__ import print_function

from time import clock

import numpy as np

from fluidimage.synthetic import make_synthetic_images
from fluidimage.calcul.correl import CorrelScipySignal, CorrelTheano


nx = 32
ny = 32

nx1 = 16
ny1 = 16

displacement_x = 2.
displacement_y = 2.

displacements = np.array([displacement_y, displacement_x])

nb_particles = (nx // 3)**2


print('nx: {} ; ny: {} ; nx1: {} ; ny1: {}'.format(nx, ny, nx1, ny1))

im0, im1 = make_synthetic_images(
    displacements, nb_particles, shape_im0=(ny, nx), shape_im1=(ny1, nx1),
    epsilon=0.)


classes = {'sig': CorrelScipySignal, 'theano': CorrelTheano}


cs = {}
funcs = {}
for k, cls in classes.items():
    calcul_corr = cls(im0.shape, im1.shape, mode='valid')
    funcs[k] = calcul_corr
    t = clock()
    cs[k] = calcul_corr(im0, im1)
    print('calcul correl with {} : {} s'.format(k, clock() - t))
