# Geoemtry.py
#

""" SUAVE Methods for Geoemtry Generation
"""


# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy
from math import pi, sqrt
from SUAVE.Core  import Data
from SUAVE.Methods.Geometry.Two_Dimensional.Planform  import wing_planform
#from SUAVE.Attributes import Constants

# ----------------------------------------------------------------------
#  Methods
# ----------------------------------------------------------------------

def vertical_tail_planform_raymer(Vtail, Wing,  l_vt,c_vt):
    """
    by M. Vegh
    Based on a tail sizing correlation from Raymer
    inputs:
    Vtail =vertical stabilizer
    Wing  =main wing
    l_vt  =length from wing mac to vtail mac [m]
    c_vt  =vertical tail coefficient
    
    sample c_ht values: .02=Sailplane, .04=homebuilt, .04=GA single engine, .07 GA twin engine
    .04=agricultural, .08=twin turboprop, .06=flying boat, .06=jet trainer, .07=jet fighter
    .08= military cargo/bomber, .09= jet transport
    """
    
    Vtail.areas.reference=Wing.spans.projected*c_vt*Wing.areas.reference/l_vt
  
    #wing_planform(Vtail)
    return 0
    