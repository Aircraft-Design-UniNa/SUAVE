# Supersonic_Zero.py
# 
# Created:  Tim MacDonald, based on Fidelity_Zero
# Modified: Tim MacDonald, 1/29/15
#
# Updated for new optimization structure


# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
import SUAVE

from SUAVE.Core import Data
from SUAVE.Core import Units

from SUAVE.Methods.Aerodynamics.Supersonic_Zero.Lift import weissinger_vortex_lattice
from SUAVE.Methods.Aerodynamics.Supersonic_Zero.Lift import compute_aircraft_lift
from SUAVE.Methods.Aerodynamics.Supersonic_Zero.Lift.linear_supersonic_lift import linear_supersonic_lift
from SUAVE.Methods.Aerodynamics.Supersonic_Zero.Drag import compute_aircraft_drag
#from SUAVE.Attributes.Aerodynamics.Aerodynamics_1d_Surrogate import Aerodynamics_1d_Surrogate


# local imports
#from Aerodynamics_Surrogate import Aerodynamics_Surrogate
#from Configuration   import Configuration
#from Conditions      import Conditions
#from Geometry        import Geometry
from Aerodynamics import Aerodynamics
from Results import Results

# python imports
import os, sys, shutil
from copy import deepcopy
from warnings import warn

# package imports
import numpy as np
import scipy as sp


# ----------------------------------------------------------------------
#  Class
# ----------------------------------------------------------------------

class Supersonic_Zero(Aerodynamics):
    """ SUAVE.Attributes.Aerodynamics.Fidelity_Zero
        aerodynamic model that builds a surrogate model for clean wing 
        lift, using vortex lattic, and various handbook methods
        for everything else
        
        this class is callable, see self.__call__
        
    """
    
    def __defaults__(self):
        
        self.tag = 'Fidelity_Zero_Supersonic'
        
        #self.geometry      = Geometry()
        #self.configuration = Configuration()
        self.geometry = Data()
        self.settings = Data()

        # correction factors
        #self.configuration.fuselage_lift_correction           = 1.14
        #self.configuration.trim_drag_correction_factor        = 1.02
        #self.configuration.wing_parasite_drag_form_factor     = 1.1
        #self.configuration.fuselage_parasite_drag_form_factor = 2.3
        #self.configuration.aircraft_span_efficiency_factor    = 0.78
        self.settings.fuselage_lift_correction           = 1.14
        self.settings.trim_drag_correction_factor        = 1.02
        self.settings.wing_parasite_drag_form_factor     = 1.1
        self.settings.fuselage_parasite_drag_form_factor = 2.3
        self.settings.aircraft_span_efficiency_factor    = 0.78
        self.settings.drag_coefficient_increment         = 0.0000
        
        # vortex lattice configurations
        #self.configuration.number_panels_spanwise  = 5
        #self.configuration.number_panels_chordwise = 1
        self.settings.number_panels_spanwise = 5
        self.settings.number_panels_chordwise = 1
        
        #self.conditions_table = Conditions(
            #angle_of_attack = np.array([-10,-5,0,5,10.0]) * Units.deg ,
        #)
        self.training = Data()        
        self.training.angle_of_attack  = np.array([-10.,-5.,0.,5.,10.]) * Units.deg
        self.training.lift_coefficient = None
        
        #self.models = Data()
        # surrogoate models
        self.surrogates = Data()
        self.surrogates.lift_coefficient = None    
        
        
    def evaluate(self,conditions):
        """ process vehicle to setup geometry, condititon and configuration
            
            Inputs:
                conditions - DataDict() of aerodynamic conditions
                
            Outputs:
                CL - array of lift coefficients, same size as alpha 
                CD - array of drag coefficients, same size as alpha
                
            Assumptions:
                linear intperolation surrogate model on Mach, Angle of Attack 
                    and Reynolds number
                locations outside the surrogate's table are held to nearest data
                no changes to initial geometry or configuration
                
        """
        
        # unpack
        #configuration = self.configuration
        #geometry      = self.geometry
        #q             = conditions.freestream.dynamic_pressure
        #Sref          = geometry.reference_area
        settings   = self.settings
        geometry   = self.geometry
        surrogates = self.surrogates
                
        q    = conditions.freestream.dynamic_pressure
        AoA  = conditions.aerodynamics.angle_of_attack
        M = conditions.freestream.mach_number
        Sref = geometry.reference_area
        
        wings_lift_model_sub = surrogates.lift_coefficient_sub
        wings_lift_model_sup = surrogates.lift_coefficient_sup
        
        # inviscid lift of wings only
        inviscid_wings_lift = np.array([[0.0]] * len(M))
        inviscid_wings_lift[M <= 1.05] = wings_lift_model_sub(AoA[M <= 1.05])
        inviscid_wings_lift[M > 1.05] = wings_lift_model_sup(AoA[M > 1.05])
        
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift = inviscid_wings_lift
                
        # lift needs to compute first, updates data needed for drag
        CL = compute_aircraft_lift(conditions,settings,geometry)
        
        # drag computes second
        CD = compute_aircraft_drag(conditions,settings,geometry)
        
        
        # pack conditions
        conditions.aerodynamics.lift_coefficient = CL
        conditions.aerodynamics.drag_coefficient = CD        

        # pack results
        results = Data()
        results.lift_coefficient = CL
        results.drag_coefficient = CD
        
        N = q.shape[0]
        L = np.zeros([N,3])
        D = np.zeros([N,3])
        
        L[:,2] = ( -CL * q * Sref )[:,0]
        D[:,0] = ( -CD * q * Sref )[:,0]      

        results.lift_force_vector = L
        results.drag_force_vector = D        
        
        return results 
        
    def finalize(self):
        
        # sample training data
        self.sample_training_sub()
        
        # build surrogate
        self.build_surrogate_sub()
        
        self.sample_training_sup()
        self.build_surrogate_sup()
        
    def sample_training_sub(self):
        
        # unpack
        geometry = self.geometry
        settings = self.settings
        training = self.training
        
        AoA = training.angle_of_attack
        CL  = np.zeros_like(AoA)

        # condition input, local, do not keep
        konditions              = Data()
        konditions.aerodynamics = Data()

        # calculate aerodynamics for table
        for i,_ in enumerate(AoA):
            
            # overriding conditions, thus the name mangling
            konditions.aerodynamics.angle_of_attack = AoA[i]
            
            # these functions are inherited from Aerodynamics() or overridden
            CL[i] = calculate_lift_vortex_lattice(konditions, settings, geometry)

        # store training data
        training.lift_coefficient = CL

        return
    
    def sample_training_sup(self):
        
        # unpack
        geometry = self.geometry
        settings = self.settings
        training = self.training
        
        AoA = training.angle_of_attack
        CL  = np.zeros_like(AoA)

        # condition input, local, do not keep
        konditions              = Data()
        konditions.aerodynamics = Data()

        # calculate aerodynamics for table
        for i,_ in enumerate(AoA):
            
            # overriding conditions, thus the name mangling
            konditions.aerodynamics.angle_of_attack = AoA[i]
            
            # these functions are inherited from Aerodynamics() or overridden
            CL[i] = calculate_lift_linear_supersonic(konditions, settings, geometry)

        # store training data
        training.lift_coefficient = CL

        return    
        
  
    def build_surrogate_sub(self):
        
        # unpack data
        training = self.training
        AoA_data = training.angle_of_attack
        #
        CL_data  = training.lift_coefficient
        
        # pack for surrogate
        X_data = np.array([AoA_data]).T        
        
        # assign models
        X_data = np.reshape(X_data,-1)
        # assign models
        #Interpolation = Aerodynamics_1d_Surrogate.Interpolation(X_data,CL_data)
        Interpolation = np.poly1d(np.polyfit(X_data, CL_data ,1))
        
        #Interpolation = Fidelity_Zero.Interpolation
        self.surrogates.lift_coefficient_sub = Interpolation
                
        return
    
    def build_surrogate_sup(self):
        
        # unpack data
        training = self.training
        AoA_data = training.angle_of_attack
        #
        CL_data  = training.lift_coefficient
        
        # pack for surrogate
        X_data = np.array([AoA_data]).T        
        
        # assign models
        X_data = np.reshape(X_data,-1)
        # assign models
        #Interpolation = Aerodynamics_1d_Surrogate.Interpolation(X_data,CL_data)
        Interpolation = np.poly1d(np.polyfit(X_data, CL_data ,1))
        
        #Interpolation = Fidelity_Zero.Interpolation
        self.surrogates.lift_coefficient_sup = Interpolation
                
        return    
        
    #: def build_surrogate()
    
    
# ----------------------------------------------------------------------
#  Helper Functions
# ----------------------------------------------------------------------

    
def calculate_lift_vortex_lattice(conditions,configuration,geometry):
    """ calculate total vehicle lift coefficient by vortex lattice
    """
    
    # unpack
    vehicle_reference_area = geometry.reference_area
    
    # iterate over wings
    total_lift_coeff = 0.0
    for wing in geometry.wings.values():
        
        [wing_lift_coeff,wing_drag_coeff] = weissinger_vortex_lattice(conditions,configuration,wing)
        total_lift_coeff += wing_lift_coeff * wing.areas.reference / vehicle_reference_area

    return total_lift_coeff
    
def calculate_lift_linear_supersonic(conditions,configuration,geometry):
    """ Calculate total vehicle lift coefficient using linear supersonic theory
    """
    
    # unpack
    vehicle_reference_area = geometry.reference_area
    
    # iterate over wings
    total_lift_coeff = 0.0
    for wing in geometry.wings.values():
        
        wing_lift_coeff = linear_supersonic_lift(conditions,configuration,wing)
        total_lift_coeff += wing_lift_coeff * wing.areas.reference / vehicle_reference_area
    
    return total_lift_coeff    
