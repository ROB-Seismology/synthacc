"""
synthacc

A Python toolbox for kinematic earthquake ground motion modelling

Author: Bart Vleminckx, Royal Observatory of Belgium
"""

from __future__ import absolute_import, division, print_function, unicode_literals



## Reloading mechanism
try:
	reloading
except NameError:
	## Module is imported for the first time
	reloading = False
else:
	## Module is reloaded
	reloading = True
	try:
		## Python 3
		from importlib import reload
	except ImportError:
		## Python 2
		pass


## Import submodules

## apy (no internal dependencies)
if not reloading:
	from . import apy
else:
	reload(apy)

## units (depends on apy)
if not reloading:
	from . import units
else:
	reload(units)

## time (depends on apy)
if not reloading:
	from . import time
else:
	reload(time)

## plot (depnds on apy)
if not reloading:
	from . import plot
else:
	reload(plot)

## spectral (depends on apy, units, plot)
if not reloading:
	from . import spectral
else:
	reload(spectral)
from .spectral import (DFT, AccDFT, FAS, FPS, fft, ifft, plot_fass)

## response (depends on apy, units, plot, spectral)
if not reloading:
	from . import response
else:
	reload(response)
from .response import (ResponseSpectrum, NewmarkBetaRC, NigamJenningsRC,
						SpectralRC, CartwrightLonguetHiggins1956PC,
						RVTCalculator, frf, plot_response_spectra)

## math (depends on apy)
if not reloading:
	from . import math
else:
	reload(math)

## space2 (depends on apy)
if not reloading:
	from . import space2
else:
	reload(space2)

## space3 (depends on apy, math)
if not reloading:
	from . import space3
else:
	reload(space3)

## earth (depends on apy, space2, space3)
if not reloading:
	from . import earth
else:
	reload(earth)

## recordings (depends on apy, time, units, spectral, response, earth)
if not reloading:
	from . import recordings
else:
	reload(recordings)
from .recordings import (Waveform, Accelerogram, Seismogram, Recording, Pick,
						read, plot_recordings, plot_seismograms, rt_to_ne,
						ne_to_rt, husid_plot)
