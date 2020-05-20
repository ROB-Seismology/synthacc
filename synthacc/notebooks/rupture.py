"""
TODO: Implement other slip distributions (truncated exponential).
"""


from functools import partial

from faults import BelgianLowerRhineGrabenFGC
from synthacc.source.rupture.geometry import FaultSegmentCalculator
from synthacc.source.scaling import (WC1994_m2a, WC1994_m2l,
    ThingbaijamEA2017_m2a_n, ThingbaijamEA2017_m2l_n)
from synthacc.source.rupture.slip import (SlipRateCalculator,
    RiseTimeCalculator, MaiBeroza2002RFSDC, CompositeSourceSDC,
    LiuArchuleta2004NSRC, LiuEtAl2006NSRC)
from synthacc.source.rupture.hypo import RandomHCC, MaiEtAl2005HCC
from synthacc.source.rupture.velocity import ConstantVDC, RandomFieldVDC
from synthacc.source.rupture.rake import ConstantRDC, RandomFieldRDC
from synthacc.source.rupture.calculators import KinematicRuptureCalculatorLogicTree


SPACE_DELTA = 100
TIME_DELTA = 0.05


def kinematic_rupture_calculator_logic_tree(space_delta=SPACE_DELTA, time_delta=TIME_DELTA):
    """
    """
    fgc = partial(BelgianLowerRhineGrabenFGC)
    fsc = partial(FaultSegmentCalculator, ar=(1, 2), sd=2)
    src = partial(SlipRateCalculator, time_delta, RiseTimeCalculator())
    lt = KinematicRuptureCalculatorLogicTree(fgc=fgc, fsc=fsc, src=src)

    branches = [('1', 1), ('4', 4)]
    lt.add_level('fgc_n', branches)

    branches = [('20km', 20000), ('25km', 25000)]
    lt.add_level('fgc_mrd', branches)

    branches = [
        ('WC1994a', WC1994_m2a()),
        ('WC1994l', WC1994_m2l()),
        ('Tea2017a', ThingbaijamEA2017_m2a_n()),
        ('Tea2017l', ThingbaijamEA2017_m2l_n()),
        ]
    lt.add_level('fsc_sr', branches)

    branches = [
        ('RF', partial(MaiBeroza2002RFSDC, space_delta, space_delta, sd=0.85)),
        ('CS', partial(CompositeSourceSDC, space_delta, rminf=10, rmaxf=0.5, dimension=2)),
        ]
    lt.add_level('sdc', branches)

    branches = [('Random', RandomHCC), ('Constrained', MaiEtAl2005HCC)]
    lt.add_level('hcc', branches)

    branches = [('LA2004', LiuArchuleta2004NSRC()), ('Lea2006', LiuEtAl2006NSRC())]
    lt.add_level('src_nsrc', branches)

    branches = [
        ('Constant', partial(ConstantVDC, 2400, 3000)),
        ('RF', partial(RandomFieldVDC, 2400, 3000, sd=100)),
        ]
    lt.add_level('vdc', branches)

    branches = [
        ('Constant', ConstantRDC),
        ('RF', partial(RandomFieldRDC, sd=15)),
    ]
    lt.add_level('rdc', branches)

    return lt
