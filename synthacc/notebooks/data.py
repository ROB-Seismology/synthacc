"""
"""


import json
import os

import numpy as np

from robspy.synthacc import API

from synthacc.earth.geo import Path


FOLDER = os.path.join('..', 'Data')


def rauw_fault_surface_trace(proj=None):
    """
    Fault trace of Rauw fault provided by Koen Verbeeck as .TAB. Converted with
    Qgis to .geojson.
    """
    with open(os.path.join(FOLDER, 'Faults', 'Rauw_fault.geojson'), 'r') as f:
        points = json.load(f)['features'][0]['geometry']['coordinates']

    points = np.array(points, dtype=float)
    trace = Path(points[:,0], points[:,1])

    if proj is not None:
        trace = trace.project(proj)

    return trace


def catalog(region=None):
    """
    """
    c = API().get_catalog().query(region=region)

    return c


def balmatt_catalog():
    """
    """
    region = (4.9, 5.3, 51.0, 51.5)
    s_date = '2016-09-01'
    e_date = '2016-10-31'

    c = API().get_catalog(s_date, e_date).query(region)

    return c
