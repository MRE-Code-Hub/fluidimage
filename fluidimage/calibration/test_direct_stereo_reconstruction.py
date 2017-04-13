
import unittest
import os

import h5py
import matplotlib.pyplot as plt

from fluidimage.calibration.util import get_plane_equation
from fluidimage.calibration import DirectStereoReconstruction, CalibDirect

plt.show = lambda: 0

here = os.path.abspath(os.path.dirname(__file__))
path_fluidimage = os.path.split(os.path.split(here)[0])[0]

pathbase = os.path.join(path_fluidimage,
                        'image_samples', '4th_PIV-Challenge_Case_E')

long_test = False


def get_piv_field(path):

    try:
        with h5py.File(path, 'r') as f:
            keyspiv = [key for key in f.keys() if key.startswith('piv')]
            keyspiv.sort()
            key = keyspiv[-1]
            X = f[key]['xs'].value
            Y = f[key]['ys'].value
            dx = f[key]['deltaxs_final'].value
            dy = f[key]['deltays_final'].value
    except Exception:
        print(path)
        raise

    return X, Y, dx, dy


class TestCalib(unittest.TestCase):
    """Test fluidimage.calibration DirectStereoReconstruction, CalibDirect."""

    def test(self):

        nb_pixelx, nb_pixely = 1024, 1024

        nbline_x, nbline_y = 32, 32

        path_cam1 = os.path.join(pathbase, 'E_Calibration_Images', 'Camera_01')
        path_cam3 = os.path.join(pathbase, 'E_Calibration_Images', 'Camera_03')

        path_calib1 = os.path.join(path_cam1, 'calib1.npy')
        path_calib3 = os.path.join(path_cam3, 'calib3.npy')

        calib = CalibDirect(os.path.join(path_cam1, 'img*'),
                            (nb_pixelx, nb_pixely))
        calib.compute_interpolents()
        calib.compute_interppixel2line((nbline_x, nbline_y), test=False)
        calib.save(path_calib1)

        if long_test:
            calib.check_interp_lines_coeffs()
            calib.check_interp_lines()
            calib.check_interp_levels()

        calib3 = CalibDirect(os.path.join(path_cam3, 'img*'),
                             (nb_pixelx, nb_pixely))

        calib3.compute_interpolents()
        calib3.compute_interppixel2line((nbline_x, nbline_y), test=False)
        calib3.save(path_calib3)

        postfix = '.piv'
        name = 'piv_00001-00002.h5'
        path_im = os.path.join(pathbase, 'E_Particle_Images')

        path_piv1 = os.path.join(path_im, 'Camera_01' + postfix, name)
        path_piv3 = os.path.join(path_im, 'Camera_03' + postfix, name)

        z0 = 0
        alpha = 0
        beta = 0
        a, b, c, d = get_plane_equation(z0, alpha, beta)

        Xl, Yl, dxl, dyl = get_piv_field(path_piv1)
        Xr, Yr, dxr, dyr = get_piv_field(path_piv3)

        stereo = DirectStereoReconstruction(path_calib1, path_calib3)
        X0, X1, d0cam, d1cam = stereo.project2cam(
            Xl, Yl, dxl, dyl, Xr, Yr, dxr, dyr, a, b, c, d, check=False)
        X, Y, Z = stereo.find_common_grid(X0, X1, a, b, c, d)

        dx, dy, dz, erx, ery, erz = stereo.reconstruction(
            X0, X1, d0cam, d1cam, a, b, c, d, X, Y, check=False)

        dt = 0.001
        dx, dy, dz, erx, ery, erz = dx/dt, dy/dt, dz/dt, erx/dt, ery/dt, erz/dt

if __name__ == "__main__":
    unittest.main()
