import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------
# utilities
# --------------------------------------------------
def mpl2html(fig, title="Figure"):
    """ Converts a matplotlib fig into an IPython HTML Core object for display 
    compatibility in widgets."""
    from IPython.core.pylabtools import print_figure
    import base64

    fdata64 = base64.b64encode(print_figure(fig))
    html_tpl = '<img alt="{title}" src="data:image/png;base64,{fdata64}">'
    return html_tpl.format(**locals())


class SamplePlotter(object):
    def __init__(self,
                 nbin=1,
                 elements=[],
                 bounds=[],
                 ratio=0.2,
                 width=6.5,
                 xoffset=0.2,
                 grid=True,
                 closefig=True):

        self.nbin = nbin
        self.elements = elements
        self.bounds = bounds

        self._ratio = ratio
        self._width = width
        self._xoffset = xoffset

        self._grid = grid
        self._closefig = closefig

        self._samples = []

    @property
    def nbin(self):
        return self._nbin

    @nbin.setter
    def nbin(self, val):
        self._nbin = val
        self.nullify_fig()

    @property
    def ncomp(self):
        return len(self.elements)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._width * self._ratio * self.ncomp

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self,val):
        self._elements = val

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, bounds):
        if bounds is None:
            self._bounds = [(0.0, 1.0) for _ in range(self.ncomp)]
        else:
            assert len(bounds) == self.ncomp
            if None in bounds:
                L = []
                for x in bounds:
                    if x in None:
                        val = (0.0, 1.0)
                    else:
                        val = x
                    L.append(x)
                self._bounds = L
            else:
                self._bounds = bounds

    def nullify_fig(self):
        if hasattr(self,'_fig'):
            del self._fig
        if hasattr(self,'_ax'):
            del self._ax
        if hasattr(self,'_spines'):
            del self._spines

    def nullify_all(self):
        self.nullify_fig()
        self._samples = []

    @property
    def ax(self):
        if not hasattr(self,'_ax'):
            self._get_figure()
        return self._ax

    @property
    def fig(self):
        if not hasattr(self,'_fig'):
            self._get_figure()
        return self._fig

    @property
    def spines(self):
        if not hasattr(self,'_spines'):
            self._get_figure()
        return self._spines


    def _get_figure(self):

        self._fig, self._ax = plt.subplots(figsize=(self.width, self.height))
        self._fig.subplots_adjust(right=0.8)

        # close figure?
        if self._closefig:
            plt.close(self._fig)

        self._adjust_ax()

    

        self._spines = []
        for i in range(self.ncomp):
            new = self._ax.twiny()
            self._adjust_spine(new, i - 0.5, self.bounds[i])
            self._spines.append(new)

        self._spines[0].set_xlabel('mass fraction')
        self._spines[0].xaxis.set_label_position('bottom')

    def _adjust_ax(self):
        ax = self._ax

        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        #despine
        for k in ['right', 'top']:
            ax.spines[k].set_visible(False)

        #adjust
        ax.spines['left'].set_position(('axes', -0.1))

        #bottom

        #x spacing
        ticks = np.linspace(0.0, 1.0, self.nbin + 1)
        ticks = [ticks[0] - self._xoffset] + list(ticks) + [ticks[-1] +
                                                            self._xoffset]

        ax.set_xlim(ticks[0], ticks[1])

        # positioning
        ax.spines['bottom'].set_position(('axes', -0.5))
        ax.xaxis.set_ticks(ticks)

        ax.spines['bottom'].set_visible(False)
        ax.xaxis.set_ticks([])

        #setup base axis
        ax.yaxis.set_ticks(range(self.ncomp))
        ax.set_ylim(-0.5, self.ncomp - 0.5)

        ax.yaxis.set_ticklabels(self.elements)

        #grid
        if self._grid:
            for x in ticks[1:-1]:
                self._ax.axvline(x=x, linestyle=':', color='k')

    def _adjust_spine(self, ax, ypos, xlim=(0, 1)):
        ax.xaxis.set_ticks_position('bottom')
        for k in ['right', 'top', 'left']:
            ax.spines[k].set_visible(False)

        ax.spines['bottom'].set_position(('data', ypos))

        ticks = np.linspace(xlim[0], xlim[1], self.nbin + 1)
        delta = (ticks[-1] - ticks[0]) * self._xoffset
        ticks = [ticks[0] - delta] + list(ticks) + [ticks[-1] + delta]
        ax.set_xlim(ticks[0], ticks[1])
        ax.xaxis.set_ticks(ticks)

        tick_labels = ['' for _ in ticks]
        tick_labels[0] = r'$-\infty$'
        tick_labels[1] = xlim[0]
        tick_labels[-2] = xlim[1]
        tick_labels[-1] = r'$\infty$'
        ax.xaxis.set_ticklabels(tick_labels)

    def _scale(self, index, x):
        """scale absolute to relative"""
        bounds = self.bounds[index]
        val = (x - bounds[0]) / (bounds[1] - bounds[0])

        LB = -self._xoffset * 0.9
        UB = 1.0 + self._xoffset * 0.9
        if val < LB:
            val = LB
        elif val > UB:
            val = UB

        return val

    def _scale_masses(self, masses):

        if isinstance(masses, dict): 
            # convert dict to list in order of elements
            masses = [masses[k] for k in self.elements]

        mass_scaled = []
        for i, x in enumerate(masses):
            mass_scaled.append(self._scale(i, x))
        return mass_scaled

    def add_sample(self, masses):
        self._samples.append(self._scale_masses(masses))


    def pcolor(self):
        x = np.concatenate(([-self._xoffset], np.linspace(
            0, 1, self.nbin + 1), [1.0 + self._xoffset]))
        y = np.arange(-0.5, self.ncomp, 1.0)
        X, Y = np.meshgrid(x, y)

        Z = np.zeros((self.ncomp, self.nbin + 2), dtype=bool)

        for masses in self._samples:
            bins = np.digitize(masses, x) - 1
            Z[range(self.ncomp), bins] = True

        self._hit_table = Z
        self.ax.pcolor(X, Y, self._hit_table, cmap=plt.cm.Greys, vmin=0.0, vmax=10.0)

    def plot_masses(self):
        for i, x in enumerate(self._samples):
            self.ax.plot(x, range(self.ncomp), marker='o', label=i)

    def add_legend(self):
        if len(self._samples) > 0:
            self.ax.legend(loc='center left', bbox_to_anchor=(1.1, 0.5))


    def plot_all(self):
        self.plot_masses()
        self.pcolor()
        self.add_legend()

    def to_html(self):
        return mpl2html(self._fig)
