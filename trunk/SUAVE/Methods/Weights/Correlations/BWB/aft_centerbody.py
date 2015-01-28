# aft_centerbody.py
# 
# Created:  Tim Momose, June 2014


# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
from SUAVE.Core import Units

# ----------------------------------------------------------------------
#  Method
# ----------------------------------------------------------------------

def aft_centerbody(no_of_engines, aft_centerbody_area, aft_centerbody_taper, TOGW):
    """ aft_wt = SUAVE.Methods.Weights.Correlations.BWB.aft_centerbody(no_of_engines, aft_centerbody_area, aft_centerbody_taper, TOGW)
        Weight estimate for the aft section of a BWB centerbody.
        Regression from FEA by K. Bradley (George Washington University).
        
        Assumptions:
            -The engines are mounted on the aft centerbody
            -The aft centerbody is unpressurized
        
        Inputs:
            no_of_engines - the number of engines mounted on the aft centerbody 
            [dimensionless]
            aft_centerbody_area - the planform area of the aft centerbody. 
            Typcially the area behind 70% chord [meters**2]
            aft_centerbody_taper - the taper ratio of the aft centerbody (exclude
            the chord taken up by the pressurized passenger cabin) [dimensionless]
            TOGW - Takeoff gross weight of the aircraft [kilograms]
        Outputs:
            aft_wt - the estimated structural weight of the BWB aft centerbody
                
        References:
            Bradley, K. R., "A Sizing Methodology for the Conceptual Design of 
            Blended-Wing-Body Transports," NASA/CR-2004-213016, 2004.
    """     
    
    # convert to imperial units and shorten variable names
    n_eng  = no_of_engines
    S_aft  = aft_centerbody_area  / Units.feet ** 2.0
    l_aft  = aft_centerbody_taper
    W      = TOGW                 / Units.pounds
    
    aft_wt = (1.0 + 0.05*n_eng) * 0.53 * S_aft * (W**0.2) * (l_aft + 0.5)
    
    # convert back to base units
    aft_wt = aft_wt * Units.pounds
    
    return aft_wt