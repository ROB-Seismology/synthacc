"""
The 'spectral' module.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import matplotlib.pyplot as plt
import numpy as np

from .apy import (Object, is_number, is_pos_number, is_1d_numeric_array,
    is_1d_complex_array)
from .units import MOTION as UNITS, MOTION_SI as SI_UNITS
from .plot import set_space


class DFT(Object):
    """
    A discrete Fourier transform (DFT) that is already normalized (i.e.
    amplitudes must be multiplied by time delta).
    """

    def __init__(self, frequencies, amplitudes, unit, validate=True):
        """
        """
        frequencies = np.asarray(frequencies, dtype=float)
        amplitudes = np.asarray(amplitudes, dtype=complex)

        if validate is True:
            assert(is_1d_numeric_array(frequencies))
            assert(is_1d_complex_array(amplitudes))
            assert(frequencies.shape == amplitudes.shape)
            assert(unit in UNITS)

        self._frequencies = frequencies
        self._amplitudes = amplitudes
        self._unit = unit

    def __len__(self):
        """
        """
        return len(self._frequencies)

    @classmethod
    def from_fas_and_fps(cls, fas, fps, validate=True):
        """
        """
        if validate is True:
            assert(type(fas) == FAS)
            assert(type(fps) == FPS)
            assert(np.array_equal(fas.frequencies, fps.frequencies))

        frequencies, unit = fas.frequencies, fas.unit
        real = np.cos(fps.amplitudes) * fas.amplitudes
        imag = np.sin(fps.amplitudes) * fas.amplitudes
        amplitudes = (real + 1j * imag)

        return cls(frequencies, amplitudes, unit, validate=False)

    @property
    def frequencies(self):
        """
        """
        return np.copy(self._frequencies)

    @property
    def amplitudes(self):
        """
        """
        return np.copy(self._amplitudes)

    @property
    def unit(self):
        """
        """
        return self._unit

    @property
    def real(self):
        """
        """
        return np.copy(self._amplitudes.real)

    @property
    def imag(self):
        """
        """
        return np.copy(self._amplitudes.imag)

    @property
    def magnitudes(self):
        """
        """
        magnitudes = np.sqrt(
            (self._amplitudes.real)**2 +
            (self._amplitudes.imag)**2
            )
        return magnitudes

    @property
    def angles(self):
        """
        """
        angles = np.arctan2(
            self._amplitudes.imag,
            self._amplitudes.real,
            )
        return angles

    @property
    def fas(self):
        """
        Fourier amplitude spectrum (FAS).
        """
        amplitudes = self.magnitudes
        fas = FAS(self.frequencies, amplitudes, self._unit, validate=False)
        return fas

    @property
    def fps(self):
        """
        Fourier phase spectrum (FPS).
        """
        amplitudes = self.angles
        fps = FPS(self.frequencies, amplitudes, validate=False)
        return fps

    @property
    def gmt(self):
        """
        Ground motion type (displacement, velocity or acceleration).

        return: string
        """
        return UNITS[self._unit].quantity

    def get_amplitudes(self, unit=None, validate=True):
        """
        """
        if validate is True:
            if unit is not None:
                assert(UNITS[unit].quantity == self.gmt)

        if unit is None or unit == self._unit:
            return self.amplitudes
        else:
            return self._amplitudes * (UNITS[self._unit] / UNITS[unit])

    def inverse(self, time_delta, validate=True):
        """
        """
        return ifft(self._frequencies, self._amplitudes, time_delta, validate)

    def get_seismogram(self, time_delta, validate=True):
        """
        """
        from .recordings import Seismogram

        amplitudes = self.inverse(time_delta, validate=validate)

        return Seismogram(time_delta, amplitudes, unit=self._unit)


class AccDFT(DFT):
    """
    """

    def __init__(self, frequencies, amplitudes, unit, validate=True):
        """
        """
        if validate is True:
            assert(UNITS[unit].quantity == 'acceleration')

        super(AccDFT, self).__init__(frequencies, amplitudes, unit, validate)

    @classmethod
    def from_dft(cls, dft, validate=True):
        """
        """
        if validate is True:
            assert(type(dft) is DFT)

        acc_dft = cls(
            dft.frequencies,
            dft.amplitudes,
            dft.unit,
            validate=False,
            )

        return acc_dft

    def get_response(self, frequency, damping, gmt, validate=True):
        """
        Get response of SDOF oscillator with frequency response function (FRF).
        """
        from .response import frf

        amplitudes = self.get_amplitudes(unit='m/s2') * frf(
            self.frequencies, frequency, damping, gmt, validate=validate)
        unit = SI_UNITS[gmt]

        return DFT(self.frequencies, amplitudes, unit)


class FAS(Object):
    """
    Fourier amplitude spectrum (FAS) that is already normalized (i.e.
    amplitudes must be multiplied by time delta).
    """

    def __init__(self, frequencies, amplitudes, unit, validate=True):
        """
        """
        frequencies = np.asarray(frequencies, dtype=float)
        amplitudes = np.asarray(amplitudes, dtype=float)

        if validate is True:
            assert(is_1d_numeric_array(frequencies))
            assert(is_1d_numeric_array(amplitudes))
            assert(frequencies.shape == amplitudes.shape)
            assert(unit in UNITS)

        self._frequencies = frequencies
        self._amplitudes = amplitudes
        self._unit = unit

    def __len__(self):
        """
        """
        return len(self._frequencies)

    def __mul__(self, value, validate=True):
        """
        """
        if validate is True:
            assert(is_number(value) or (
                is_1d_numeric_array(value) and len(value) == len(self)
            ))

        fas = self.__class__(
            self.frequencies, self._amplitudes * value, self.unit)

        return fas

    @property
    def frequencies(self):
        """
        """
        return np.copy(self._frequencies)

    @property
    def amplitudes(self):
        """
        """
        return np.copy(self._amplitudes)

    @property
    def unit(self):
        """
        """
        return self._unit

    @property
    def gmt(self):
        """
        Ground motion type (displacement, velocity or acceleration).

        return: string
        """
        return UNITS[self._unit].quantity

    def get_amplitudes(self, unit=None, validate=True):
        """
        """
        if validate is True:
            if unit is not None:
                assert(UNITS[unit].quantity == self.gmt)

        if unit is None or unit == self._unit:
            return self.amplitudes
        else:
            return self.amplitudes * (UNITS[self._unit] / UNITS[unit])

    def plot(self, color=None, style=None, width=None, unit=None, space='loglog', min_frequency=None, max_frequency=None, min_amplitude=None, max_amplitude=None, title=None, size=None, filespec=None):
        """
        """
        labels, colors, styles, widths = None, None, None, None
        if color is not None:
            colors = [color]
        if style is not None:
            styles = [style]
        if width is not None:
            widths = [width]

        plot_fass([self], labels, colors, styles, widths, unit, space,
            min_frequency, max_frequency, min_amplitude, max_amplitude, title,
            size, filespec)


class FPS(Object):
    """
    A Fourier phase spectrum (FPS).
    """

    def __init__(self, frequencies, amplitudes, validate=True):
        """
        """
        frequencies = np.asarray(frequencies, dtype=float)
        amplitudes = np.asarray(amplitudes, dtype=float)

        if validate is True:
            assert(is_1d_numeric_array(frequencies))
            assert(is_1d_numeric_array(amplitudes))
            assert(frequencies.shape == amplitudes.shape)

        self._frequencies = frequencies
        self._amplitudes = amplitudes

    def __len__(self):
        """
        """
        return len(self._frequencies)

    @property
    def frequencies(self):
        """
        """
        return np.copy(self._frequencies)

    @property
    def amplitudes(self):
        """
        """
        return np.copy(self._amplitudes)


def fft(time_delta, amplitudes):
    """
    Fast Fourier Transform (FFT).
    """
    frequencies = np.fft.rfftfreq(len(amplitudes), time_delta)
    amplitudes = np.fft.rfft(amplitudes) * time_delta

    return frequencies, amplitudes


def ifft(frequencies, amplitudes, time_delta, validate=True):
    """
    Inverse Fast Fourier Transform (iFFT).
    """
    n = int(round(1 / (frequencies[1] * time_delta)))

    if validate is True:
        assert(len(amplitudes) == (n//2 + 1))

    amplitudes = np.fft.irfft(amplitudes / time_delta, n)

    return amplitudes


def plot_fass(fass, labels=None, colors=None, styles=None, widths=None, unit=None, space='loglog', min_frequency=None, max_frequency=None, min_amplitude=None, max_amplitude=None, title=None, size=None, filespec=None):
    """
    """
    if unit is None:
        unit = fass[0].unit

    _, ax = plt.subplots(figsize=size)

    for i, fas in enumerate(fass):

        kwargs = {}
        if labels is not None:
            kwargs['label'] = labels[i]
        if colors is not None:
            kwargs['c'] = colors[i]
        if styles is not None:
            kwargs['ls'] = styles[i]
        if widths is not None:
            kwargs['lw'] = widths[i]

        ax.plot(fas.frequencies, fas.get_amplitudes(unit), **kwargs)

    ax.grid()

    if labels is not None:
        ax.legend()

    set_space(ax, space)

    ax.set_xlim([min_frequency, max_frequency])
    ax.set_ylim([min_amplitude, max_amplitude])

    x_label = 'Frequency (1/s)'
    y_label = 'Amplitude (%s * s)' % unit

    ax.xaxis.set_label_text(x_label)
    ax.yaxis.set_label_text(y_label)

    if title is not None:
        ax.set_title(title)

    if filespec is not None:
        plt.savefig(filespec)
    else:
        plt.show()
