# -*- coding: iso-Latin-1 -*-

"""
The 'source.moment' module.
"""


from abc import ABCMeta, abstractmethod

import matplotlib.pyplot as plt
import numpy as np

from ..apy import (PRECISION, Object, is_number, is_pos_number,
    is_1d_numeric_array)
from ..math import SquareMatrix


class MomentTensor(Object):
    """
    A general moment tensor following the NED convection (x is north, y is east
    and z is down). Each of the nine Mij elements represents a pair of opposing
    forces, pointing in the i direction and separated in the j direction (force
    couple). The force at positive j points to positive i. To conserve angular
    moment Mij = Mji, leaving only six indepent elements.
    """

    COMPONENTS = ('xx', 'yy', 'zz', 'xy', 'yz', 'zx')

    def __init__(self, xx, yy, zz, xy, yz, zx, validate=True):
        """
        xx, yy, zz, xy, yz and zx: number
        """
        self._m = SquareMatrix(
            [[xx, xy, zx], [xy, yy, yz], [zx, yz, zz]], validate=validate)

    def __repr__(self):
        """
        """
        s = '< Moment Tensor |'
        for c in self.six:
            s += ' {}'.format(c)
        s += ' >'

        return s

    def __getitem__(self, item, validate=True):
        """
        NOTE: Indices start at 1!
        """
        e = self._m.__getitem__(item, validate=validate)

        if e.is_integer():
            return int(e)
        elif abs(e) < 10**-PRECISION:
            return 0
        else:
            return e

    def __add__(self, other):
        """
        return: new instance
        """
        assert(type(other) is MomentTensor)

        xx = self.xx + other.xx
        yy = self.yy + other.yy
        zz = self.zz + other.zz
        xy = self.xy + other.xy
        yz = self.yz + other.yz
        zx = self.zx + other.zx

        mt = self.__class__(xx, yy, zz, xy, yz, zx)

        return mt

    def __mul__(self, other):
        """
        return: new instance
        """
        assert(is_number(other))

        xx = self.xx * other
        yy = self.yy * other
        zz = self.zz * other
        xy = self.xy * other
        yz = self.yz * other
        zx = self.zx * other

        mt = self.__class__(xx, yy, zz, xy, yz, zx)

        return mt

    @property
    def xx(self):
        """
        return: number
        """
        return self[1,1]

    @property
    def yy(self):
        """
        return: number
        """
        return self[2,2]

    @property
    def zz(self):
        """
        return: number
        """
        return self[3,3]

    @property
    def xy(self):
        """
        return: number
        """
        return self[1,2]

    @property
    def yz(self):
        """
        return: number
        """
        return self[2,3]

    @property
    def zx(self):
        """
        return: number
        """
        return self[3,1]

    @property
    def six(self):
        """
        """
        return self.get_six()

    @property
    def trace(self):
        """
        return: number
        """
        return self._m.trace

    @property
    def moment(self):
        """
        Seismic moment (in Nm). See Shearer (2009) p. 247.
        """
        m0 = float(np.sqrt(np.sum(e**2 for e in self._m)) / np.sqrt(2))

        if abs(m0-round(m0)) < 10**-PRECISION:
            m0 = int(round(m0))

        return m0

    @property
    def magnitude(self):
        """
        Moment magnitude from seismic moment.
        """
        return m0_to_mw(self.moment)

    def get_six(self, convention='NED', validate=True):
        """
        The six independent components of the moment tensor in NED or USE.

        NED: (xx, yy, zz, xy, yz and zx) or (nn, ee, dd, ne, ed and dn)
        USE: (rr, tt, pp, rt, tp and pr) or (uu, ss, ee, us, se and eu)

        See Aki and Richards (2002) p. 112. for the NED-USE conversion.
        """
        if validate is True:
            assert(convention in ('NED', 'USE'))

        if convention == 'NED':
            return (+self.xx, +self.yy, +self.zz, +self.xy, +self.yz, +self.zx)
        else:
            return (+self.zz, +self.xx, +self.yy, +self.zx, -self.xy, -self.yz)

    def has_isotropic_part(self):
        """
        return: boolean
        """
        return self.trace != 0


class TimeSeries(Object):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self, time_delta, start_time=0, validate=True):
        """
        time_delta: pos number (in s)
        start_time: number (in s) (default: 0)
        """
        if validate is True:
            assert(is_pos_number(time_delta))
            assert(is_number(start_time))

        self._time_delta = time_delta
        self._start_time = start_time

    @abstractmethod
    def __len__(self):
        """
        """
        pass

    @property
    def time_delta(self):
        """
        return: pos number (in s)
        """
        return self._time_delta

    @property
    def start_time(self):
        """
        return: number (in s)
        """
        return self._start_time

    @property
    def times(self):
        """
        """
        return self.time_delta * np.arange(len(self))


class MomentFunction(TimeSeries):
    """
    Released moment in function of time.
    """

    def __init__(self, time_delta, moments, start_time=0, validate=True):
        """
        time_delta: (in s)
        moments: (in Nm)
        start_time: (in s)
        """
        super().__init__(time_delta, start_time, validate=validate)

        values = np.asarray(moments, dtype=float)

        if validate is True:
            assert(is_1d_numeric_array(values))
            assert(values[0] == 0)
            assert(np.all(np.diff(values) >= 0))

        self._values = values

    def __len__(self):
        """
        """
        return len(self._values)

    @property
    def moments(self):
        """
        """
        return np.copy(self._values)

    @property
    def moment(self):
        """
        """
        return float(self._values[-1])

    @property
    def magnitude(self):
        """
        return: number
        """
        return m0_to_mw(self.moment)

    def get_duration(self, percentile=5):
        """
        """
        min_moment = self.moment * percentile / 100
        max_moment = self.moment - min_moment

        times = self.times
        min_time = times[self._values >= min_moment][0]
        max_time = times[self._values >= max_moment][0]

        return max_time - min_time

    def plot(self, model=None, title=None, size=None, filespec=None, validate=True):
        """
        """
        _, ax = plt.subplots(figsize=size)

        ax.plot(self.times, self.moments, c='dimgrey', lw=2)
        ax.fill_between(self.times, self.moments, color='lightgrey')

        if model is not None:
            ax.plot(model.times, model.moments, c='red', lw=2)

        ax.set_xlim(ax.get_xaxis().get_data_interval())
        ax.set_ylim((0, None))

        x_label, y_label = 'Time (s)', 'Moment (Nm)'

        ax.xaxis.set_label_text(x_label)
        ax.yaxis.set_label_text(y_label)

        if title is None:
            ax.set_title('Moment function')

        plt.grid()

        if filespec is not None:
            plt.savefig(filespec)
        else:
            plt.show()


class MomentRateFunction(TimeSeries):
    """
    A moment rate function (or source time function (STF)).
    """

    def __init__(self, time_delta, rates, start_time=0, validate=True):
        """
        """
        super().__init__(time_delta, start_time, validate=validate)

        rates = np.asarray(rates, dtype=float)

        if validate is True:
            assert(is_1d_numeric_array(rates))
            assert(np.all(rates >= 0))
            assert(rates[+0] == 0)
            assert(rates[-1] == 0)

        self._rates = rates

    def __len__(self):
        """
        """
        return len(self.rates)

    @property
    def rates(self):
        """
        return: 1d numerical array
        """
        return np.copy(self._rates)

    @property
    def moment(self):
        """
        return: pos number
        """
        return float(np.sum(self._rates) * self._time_delta)

    @property
    def magnitude(self):
        """
        return: number
        """
        return m0_to_mw(self.moment)

    def get_moment_function(self):
        """
        """
        mf = MomentFunction(self._time_delta, np.cumsum(self._rates) * \
            self._time_delta, self._start_time, validate=False)

        return mf

    def plot(self, model=None, title=None, size=None, filespec=None, validate=True):
        """
        """
        _, ax = plt.subplots(figsize=size)

        ax.plot(self.times, self.rates, c='dimgrey', lw=2)
        ax.fill(self.times, self.rates, c='lightgrey')

        if model is not None:
            ax.plot(model.times, model.rates, c='red', lw=2)

        ax.set_ylim((0, None))

        x_label, y_label = 'Time (s)', 'Moment rate (Nm/s)'

        ax.xaxis.set_label_text(x_label)
        ax.yaxis.set_label_text(y_label)

        if title is None:
            ax.set_title('Moment rate function')

        plt.grid()

        if filespec is not None:
            plt.savefig(filespec)
        else:
            plt.show()


class NormalizedMomentRateFunction(TimeSeries):
    """
    A normalized moment rate function (normalized source time function (STF)).
    """

    def __init__(self, time_delta, rates, start_time=0, validate=True):
        """
        time_delta: (in s)
        rates: (in 1/s)
        start_time: (in s)
        """
        super().__init__(time_delta, start_time, validate=validate)

        rates = np.asarray(rates)

        if validate is True:
            assert(is_1d_numeric_array(rates))
            assert(np.all(rates >= 0))
            assert(rates[+0] == 0)
            assert(rates[-1] == 0)
            assert(np.abs((np.sum(rates) * self.time_delta) - 1)
            <= 10**-PRECISION)

        self._rates = rates

    def __len__(self):
        """
        """
        return len(self._rates)

    @property
    def rates(self):
        """
        return: 1d numerical array
        """
        return np.copy(self._rates)

    def __mul__(self, moment):
        """
        return: 'moment.MomentRateFunction' instance
        """
        assert(is_pos_number(moment))

        mrf = MomentRateFunction(
            self.time_delta,
            self._rates * moment,
            self.start_time,
            )

        return mrf

    def plot(self, model=None, title=None, size=None, filespec=None, validate=True):
        """
        """
        _, ax = plt.subplots(figsize=size)

        ax.plot(self.times, self.rates, c='dimgrey', lw=2)
        ax.fill(self.times, self.rates, c='lightgrey')

        if model is not None:
            ax.plot(model.times, model.rates, c='red', lw=2)

        ax.set_ylim((0, None))

        x_label, y_label = 'Time (s)', 'Normalized moment rate (1/s)'

        ax.xaxis.set_label_text(x_label)
        ax.yaxis.set_label_text(y_label)

        if title is None:
            ax.set_title('Normalized moment rate function')

        plt.grid()

        if filespec is not None:
            plt.savefig(filespec)
        else:
            plt.show()


class TriangularRateGenerator(Object):
    """
    Gives a (normalized) moment rate function with the shape of an isosceles
    triangle. The height of the triangle (i.e. the maximum rate) is equal to
    the inverse of half its base (i.e. the half duration).
    """

    def get_nmrf(self, time_delta, half_duration, offset=None, validate=True):
        """
        return: 'moment.NormalizedMomentRateFunction' instance
        """
        if validate is True:
            assert(is_pos_number(time_delta))
            assert(is_pos_number(half_duration))
            assert(offset is None or is_pos_number(offset))

        n = int(round(half_duration / time_delta))
        assert(abs((n * time_delta) - half_duration) <= 10**-PRECISION)

        rates = np.zeros(2*n+1)
        rates[:n+1] = np.linspace(0, 1 / half_duration, n+1)
        rates[n+1:] = rates[:n][::-1]

        if offset is not None:
            rates = np.concatenate(
                (np.zeros(int(round(offset / time_delta))), rates))

        nmrf = NormalizedMomentRateFunction(time_delta, rates)

        return nmrf


def calculate(area, slip, rigidity, validate=True):
    """
    area: (in m²)
    slip: (in m)
    rigidity: (in Pa)

    return: seismic moment (in Nm)
    """
    if validate is True:
        assert(is_pos_number(area))
        assert(is_pos_number(slip))
        assert(is_pos_number(rigidity))

    return area * slip * rigidity


def m0_to_mw(m0, precise=True, validate=True):
    """
    Convert seismic moment in J (Nm) to moment magnitude. 1 dyne-cm = 10**-7
    Nm. The factor 10.7 can also be written as (2/3) * 16.1, which is more
    precise. Both are used. The difference in moment magnitude can be 0.1. The
    Global CMT Catalog for example uses (2/3) * 16.1 from February 1, 2006. See
    the "Note on calculation of moment magnitude" section on
    http://www.globalcmt.org/CMTsearch.html (last accessed on 10/10/2017). The
    rounding occurs in Hanks and Kanamori (1979).

    precise: bool, use precise factor or not (default: True)

    return: number, mw
    """
    if validate is True:
        assert(is_pos_number(m0))

    if precise is True:
        factor = (2/3) * 16.1
    else:
        factor = 10.7

    return float((2/3) * np.log10(float(m0)*10**7) - factor)


def mw_to_m0(mw, precise=True, validate=True):
    """
    Convert moment magnitude to seismic moment in J (Nm). 1 dyne-cm = 10**-7
    Nm. The factor 10.7 can also be written as (2/3) * 16.1, which is more
    precise. Both are used. The difference in moment magnitude can be 0.1. The
    Global CMT Catalog for example uses (2/3) * 16.1 from February 1, 2006. See
    the "Note on calculation of moment magnitude" section on
    http://www.globalcmt.org/CMTsearch.html (last accessed on 10/10/2017). The
    rounding occurs in Hanks and Kanamori (1979).

    precise: bool, use precise factor or not (default: True)

    return: number, m0 in J (Nm)
    """
    if validate is True:
        assert(is_number(mw))

    if precise is True:
        factor = (2/3) * 16.1
    else:
        factor = 10.7

    return float(10**((3/2) * (mw + factor)) / 10**7)
