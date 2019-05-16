"""
The 'plot' module.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


from .apy import is_string


def set_space(ax, space, validate=True):
    """
    Set space of Matplotlib Axes instance.
    """
    if validate is True:
        assert(is_string(space, 6))
        
    x_space = space[3:6]
    y_space = space[0:3]

    space_map = {'lin': 'linear', 'log': 'log'}

    ax.set_xscale(space_map[x_space])
    ax.set_yscale(space_map[y_space])

    return ax
