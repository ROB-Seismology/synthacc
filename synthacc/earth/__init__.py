"""
earth submodule

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

## flat (depends on ..apy, ..space2, ..space3)
if not reloading:
	from . import flat
else:
	reload(flat)

## geo (depends on flat, ..apy, ..space3, ..units)
if not reloading:
	from . import geo
else:
	reload(geo)
