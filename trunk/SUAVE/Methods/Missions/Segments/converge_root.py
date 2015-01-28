
# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# Scipy
import scipy
import scipy.optimize

from SUAVE.Plugins.VyPy.tools import array_type

# ----------------------------------------------------------------------
#  Converge Root
# ----------------------------------------------------------------------

def converge_root(segment,state):
    
    unknowns = state.unknowns.pack_array()
    
    try:
        root_finder = segment.settings.root_finder
    except AttributeError:
        root_finder = scipy.optimize.fsolve 
    
    unknowns = root_finder( iterate,
                            unknowns,
                            args = [segment,state],
                            xtol = state.numerics.tolerance_solution)
    
    return

    
# ----------------------------------------------------------------------
#  Helper Functions
# ----------------------------------------------------------------------
    
def iterate(unknowns,(segment,state)):

    if isinstance(unknowns,array_type):
        state.unknowns.unpack_array(unknowns)
    else:
        state.unknowns = unknowns
        
    segment.process.iterate(segment,state)
    
    residuals = state.residuals.pack_array()
        
    return residuals 

