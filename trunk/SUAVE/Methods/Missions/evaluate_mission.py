""" evaluate_mission.py: solve Mission segments in sequence """

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import copy
from evaluate_segment import evaluate_segment
from warnings import warn


# ----------------------------------------------------------------------
#  Methods
# ----------------------------------------------------------------------

def evaluate_mission(mission):

    mission = copy.deepcopy(mission)
    segments = mission.segments
    
    # evaluate each segment 
    for i,segment in enumerate(segments.values()):
        
        if i > 0:
            # link segment final conditions with initial conditions
            segment.initials = segments.values()[i-1].get_final_conditions()
        else:
            segment.initials = None
            
        ## unpack mission wide data
        #for k in ['planet','atmosphere','start_time']:
            #if not mission[k] is None:
                #if not segment[k] is None:
                    #warn('segment.%s will be overwritten by mission.%s'%(k,k),Warning)
                #segment[k] = mission[k]
            
        # run segment
        evaluate_segment(segment)
        
    return mission


# ----------------------------------------------------------------------
#  Helper Methods
# ----------------------------------------------------------------------
