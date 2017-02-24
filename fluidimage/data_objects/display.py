from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt

from fluiddyn.util import run_from_ipython

if run_from_ipython():
    plt.ion()


class DisplayPIV(object):

    def __init__(self, im0, im1, piv_results=None, show_interp=False,
                 scale=0.2, show_error=True, pourcent_histo=99, hist=False,
                 show_correl=True):

        self.piv_results = piv_results

        if show_correl and hasattr(piv_results, 'correls'):
            self.show_correl = True
        else:
            self.show_correl = False

        fig = plt.figure()
        fig.event_handler = self

        if self.show_correl:
            ax1 = plt.subplot(121)
            ax2 = plt.subplot(122)
            self.ax2 = ax2
        else:
            ax1 = plt.gca()

        self.fig = fig
        self.ax1 = ax1

        if im0 is not None:
            p0 = np.percentile(
                np.reshape(im0, (1, np.product(im0.shape))).transpose(),
                pourcent_histo)
            p1 = np.percentile(
                np.reshape(im1, (1, np.product(im1.shape))).transpose(),
                pourcent_histo)

            im0[im0 > p0] = p0
            im1[im1 > p1] = p1

            self.image0 = ax1.imshow(
                im0, interpolation='nearest', cmap=plt.cm.gray, origin='upper',
                extent=[0, im0.shape[1], im0.shape[0], 0],
                vmin=0, vmax=0.99*im0.max())

            self.image1 = ax1.imshow(
                im1, interpolation='nearest', cmap=plt.cm.gray, origin='upper',
                extent=[0, im0.shape[1], im0.shape[0], 0],
                vmin=0, vmax=0.99*im1.max())
            self.image1.set_visible(False)
        else:
            self.image0 = None

        l, = ax1.plot(0, 0, 'oy')
        l.set_visible(False)

        ax1.set_title('im 0 (alt+s to switch)')

        t = fig.text(0.1, 0.05, '')

        self.t = t
        self.l = l

        if im0 is not None:
            ax1.set_xlim(0, im0.shape[1])
            ax1.set_ylim(im0.shape[0], 0)

        ax1.set_xlabel('pixels')
        ax1.set_ylabel('pixels')

        if piv_results is not None:
            if show_interp:
                if hasattr(piv_results, 'deltaxs_approx'):
                    deltaxs = piv_results.deltaxs_approx
                    deltays = piv_results.deltays_approx
                    xs = piv_results.ixvecs_approx
                    ys = piv_results.iyvecs_approx
                else:
                    deltaxs = piv_results.deltaxs_final
                    deltays = piv_results.deltays_final
                    xs = piv_results.ixvecs_final
                    ys = piv_results.iyvecs_final
            else:
                deltaxs = piv_results.deltaxs
                deltays = piv_results.deltays
                xs = piv_results.xs
                ys = piv_results.ys
                
            if im0 is None:
                deltays *= -1

            self.q = ax1.quiver(
                xs, ys,
                deltaxs, -deltays,
                picker=20, color='g',  scale=scale)

            self.inds_error = inds_error = piv_results.deltays_wrong.keys()

            if show_error:
                xs_wrong = xs[inds_error]
                ys_wrong = ys[inds_error]
                dxs_wrong = np.array(
                    [piv_results.deltaxs_wrong[i] for i in inds_error])
                dys_wrong = np.array(
                    [piv_results.deltays_wrong[i] for i in inds_error])

                if im0 is None:
                    dys_wrong *= -1

                self.q_wrong = ax1.quiver(
                    xs_wrong, ys_wrong,
                    dxs_wrong, -dys_wrong,
                    picker=20, color='r', scale_units='xy', scale=scale)

        if hist:
            fig2 = plt.figure()
            ax3 = plt.gca()
            ind = np.isnan(deltaxs) + np.isnan(deltays) + np.isinf(deltaxs) + \
                np.isinf(deltays)
            deltaxs2 = deltaxs[~ind]
            deltays2 = deltays[~ind]
            # histx = np.histogram(deltaxs2, bins='fd')
            # histy = np.histogram(deltays2, bins='fd')
            # incr = 1
            # ax3.plot(histx[1][0:-1:incr], histx[0][0::incr],'b+')
            # ax3.plot(histy[1][0:-1:incr], histy[0][0::incr],'r+')
            ax3.hist(deltaxs2, 'fd', color='b')
            ax3.hist(deltays2, 'fd', color='r')

            ax3.set_xlabel('displacement x (blue) and y (red) (pixels)')
            ax3.set_ylabel('histogram')
            fig2.show()

        self.ind = 0
        fig.canvas.mpl_connect('pick_event', self.onpick)
        fig.canvas.mpl_connect('key_press_event', self.onclick)

        print('press alt+h for help')

        plt.show()

    def onclick(self, event):
        if event.key == 'alt+h':
            print('\nclick on a vector to show information\n'
                  'alt+s\t\t\t switch between images\n'
                  'alt+left or alt+right\t change vector.')

        if event.inaxes != self.ax1:
            return

        if event.key == 'alt+s':
            self.switch()

        if event.key == 'alt+left':
            self.select_arrow(self.ind - 1)

        if event.key == 'alt+right':
            self.select_arrow(self.ind + 1)

    def onpick(self, event):
        if not (event.artist == self.q or event.artist == self.q_wrong):
            return True

        # the click locations
        # x = event.mouseevent.xdata
        # y = event.mouseevent.ydata
        ind = event.ind
        self.select_arrow(ind, event.artist)

    def select_arrow(self, ind, artist=None):
        try:
            ind = ind[0]
        except (TypeError, IndexError):
            pass

        if artist is None:
            if ind in self.piv_results.errors.keys():
                artist = self.q_wrong
                ind = self.inds_error.index(ind)
            else:
                artist = self.q

        if artist == self.q:
            ind_all = ind
            q = self.q
        elif artist == self.q_wrong:
            ind_all = self.inds_error[ind]
            q = self.q_wrong

        if ind >= len(q.X) or ind < 0:
            return

        self.ind = ind_all

        ix = q.X[ind]
        iy = q.Y[ind]
        self.l.set_visible(True)
        self.l.set_data(ix, iy)

        correl_max = self.piv_results.correls_max[ind_all]
        text = (
            'vector at ix = {} : iy = {} ; '
            'U = {:.3f} ; V = {:.3f}, C = {:.3f}').format(
                ix, iy, q.U[ind], q.V[ind], correl_max)

        if ind_all in self.piv_results.errors:
            text += ', error: ' + self.piv_results.errors[ind_all]

        self.t.set_text(text)

        if self.show_correl:
            ax2 = self.ax2
            ax2.cla()
            alphac = self.piv_results.correls[ind_all]
            alphac_max = alphac.max()
            correl = correl_max/alphac_max * alphac

            ax2.imshow(correl, origin='lower', interpolation='none', vmin=0)

            i0, i1 = np.unravel_index(correl.argmax(), correl.shape)
            ax2.plot(i1, i0, 'xr')

            ax2.axis('scaled')
            ax2.set_xlim(-0.5, correl.shape[1]-0.5)
            ax2.set_ylim(-0.5, correl.shape[0]-0.5)
        self.fig.canvas.draw()

    def switch(self):
        if self.image0 is not None:
            self.image0.set_visible(not self.image0.get_visible())
            self.image1.set_visible(not self.image1.get_visible())

            self.ax1.set_title('im {} (alt+s to switch)'.format(
                int(self.image1.get_visible())))

            self.fig.canvas.draw()


class DisplayPreProc(object):

    def __init__(self, im0, im1, im0p, im1p,
                 pourcent_histo=99, hist=False):

        fig = plt.figure()
        fig.event_handler = self

        ax1 = plt.subplot(121)
        ax2 = plt.subplot(122)

        self.fig = fig
        self.ax1 = ax1
        self.ax2 = ax2

        p0 = np.percentile(
            np.reshape(im0, (1, np.product(im0.shape))).transpose(),
            pourcent_histo)
        p1 = np.percentile(
            np.reshape(im1, (1, np.product(im1.shape))).transpose(),
            pourcent_histo)
        p0p = np.percentile(
            np.reshape(im0p, (1, np.product(im0p.shape))).transpose(),
            pourcent_histo)
        p1p = np.percentile(
            np.reshape(im1p, (1, np.product(im1p.shape))).transpose(),
            pourcent_histo)
        im0[im0 > p0] = p0
        im1[im1 > p1] = p1
        im0p[im0p > p0p] = p0p
        im1p[im1p > p1p] = p1p

        self.image0 = ax1.imshow(
            im0, interpolation='nearest', cmap=plt.cm.gray, origin='upper',
            extent=[0, im0.shape[1], im0.shape[0], 0])

        self.image1 = ax1.imshow(
            im1, interpolation='nearest', cmap=plt.cm.gray, origin='upper',
            extent=[0, im0.shape[1], im0.shape[0], 0])
        self.image1.set_visible(False)

        self.image0p = ax2.imshow(
            im0p, interpolation='nearest', cmap=plt.cm.gray, origin='upper',
            extent=[0, im0p.shape[1], im0p.shape[0], 0])

        self.image1p = ax2.imshow(
            im1p, interpolation='nearest', cmap=plt.cm.gray, origin='upper',
            extent=[0, im0p.shape[1], im0p.shape[0], 0])
        self.image1p.set_visible(False)

        if hist:
            fig2 = plt.figure()
            ax3 = plt.subplot(121)
            ax4 = plt.subplot(122)
            hist0 = np.histogram(
                np.reshape(im0, (1, np.product(im0.shape))).transpose(),
                bins='fd')
            hist1 = np.histogram(
                np.reshape(im1, (1, np.product(im1.shape))).transpose(),
                bins='fd')
            hist0p = np.histogram(
                np.reshape(im0p, (1, np.product(im0p.shape))).transpose(),
                bins='fd')
            hist1p = np.histogram(
                np.reshape(im1p, (1, np.product(im1p.shape))).transpose(),
                bins='fd')
            incr = 1
            ax3.plot(hist0[1][0:-1:incr],  hist0[0][0::incr], 'k+')
            ax3.plot(hist0p[1][0:-1:incr], hist0p[0][0::incr], 'r+')
            ax4.plot(hist1[1][0:-1:incr],  hist1[0][0::incr], 'k+')
            ax4.plot(hist1p[1][0:-1:incr], hist1p[0][0::incr], 'r+')

            ax3.set_xlim(-10, max([p0, p0p]))
            ax4.set_xlim(-10, max([p1, p1p]))
            ax3.set_ylim(0, max(hist0[0]))
            ax4.set_ylim(0, max(hist1[0]))
            fig2.show()

        l, = ax1.plot(0, 0, 'oy')
        l.set_visible(False)

        ax1.set_title('im 0 (alt+s to switch)')

        ax1.set_xlim(0, im0.shape[1])
        ax1.set_ylim(im0.shape[0], 0)
        ax1.set_xlabel('pixels')
        ax1.set_ylabel('pixels')

        ax1.set_xlim(0, im0.shape[1])
        ax1.set_ylim(im0.shape[0], 0)

        ax1.set_xlabel('pixels')
        ax1.set_ylabel('pixels')

        l, = ax2.plot(0, 0, 'oy')
        l.set_visible(False)

        ax2.set_title('im 0p (alt+s to switch)')

        ax2.set_xlim(0, im0p.shape[1])
        ax2.set_ylim(im0p.shape[0], 0)
        ax2.set_xlabel('pixels')
        ax2.set_ylabel('pixels')

        self.ind = 0
        fig.canvas.mpl_connect('key_press_event', self.onclick)
        print('press alt+h for help')

        plt.show()

    def onclick(self, event):
        if event.key == 'alt+s':
            self.switch()

    def switch(self):
        self.image0.set_visible(not self.image0.get_visible())
        self.image1.set_visible(not self.image1.get_visible())

        self.ax1.set_title('im {} (alt+s to switch)'.format(
            int(self.image1.get_visible())))

        self.fig.canvas.draw()

        self.image0p.set_visible(not self.image0p.get_visible())
        self.image1p.set_visible(not self.image1p.get_visible())

        self.ax2.set_title('im {}p (alt+s to switch)'.format(
            int(self.image1p.get_visible())))
        self.fig.canvas.draw()
