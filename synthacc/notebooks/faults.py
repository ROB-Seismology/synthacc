"""
"""


from data import rauw_fault_surface_trace

from synthacc.source.faults import SimpleFault, FaultGeometryCalculator


class BelgianLowerRhineGrabenFGC(FaultGeometryCalculator):
   """
   """

   DIP, USD, LSD = (55, 65), 5000, 20000

   def __init__(self, n, mrd):
       """
       """
       super().__init__(n, mrd, self.DIP, self.USD, self.LSD)


def rauw_simple_fault(mrd=25000, dip=60, upper_sd=5000, lower_sd=20000):
    """
    """
    trace = rauw_fault_surface_trace(proj=3812) ## ETRS89 / Belgian Lambert 2008
    trace = trace.get_simplified(n=1)
    fault = SimpleFault(*trace[0], *trace[1], 0, mrd, dip,
        upper_sd=upper_sd, lower_sd=lower_sd)

    return fault
