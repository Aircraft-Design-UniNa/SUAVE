# tut_mission_Boeing_737.py
# 
# Created:  Michael Colonno, Apr 2013
# Modified: Michael Vegh   , Sep 2013
#           Trent Lukaczyk , Jan 2014

""" evaluate a mission with a Boeing 737-800
"""


# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

import SUAVE
from SUAVE.Attributes import Units

import numpy as np
import pylab as plt

import copy, time

from SUAVE.Methods.Performance import estimate_take_off_field_length
from SUAVE.Methods.Performance import estimate_landing_field_length

from SUAVE.Structure import (
Data, Container, Data_Exception, Data_Warning,
)

# ----------------------------------------------------------------------
#   Main
# ----------------------------------------------------------------------
def main():
    
    # build the vehicle
    vehicle = define_vehicle()
    
    # define the mission
    mission = define_mission(vehicle)
    
    fldlength = evaluate_field_length(vehicle)
        
    # evaluate the mission
    results = evaluate_mission(vehicle,mission)
    
    # plot results
    post_process(vehicle,mission,results)
    
    return


# ----------------------------------------------------------------------
#   Build the Vehicle
# ----------------------------------------------------------------------

def define_vehicle():
    
    # ------------------------------------------------------------------
    #   Initialize the Vehicle
    # ------------------------------------------------------------------    
    
    vehicle = SUAVE.Vehicle()
    vehicle.tag = 'Boeing 737-800'

    
    # ------------------------------------------------------------------
    #   Vehicle-level Properties
    # ------------------------------------------------------------------    

    # mass properties
    vehicle.Mass_Props.m_full       = 79015.8   # kg
    #vehicle.Mass_Props.m_empty      = 62746.4   # kg
    vehicle.Mass_Props.m_takeoff    = 79015.8   # kg
    vehicle.Mass_Props.m_flight_min = 66721.59  # kg
    vehicle.Mass_Props.pos_cg       = [60 * Units.feet, 0, 0]  # Not correct
    vehicle.Mass_Props.I_cg         = [[10 ** 5, 0, 0],[0, 10 ** 6, 0,],[0,0, 10 ** 7]] # Not Correct

    # basic parameters
    vehicle.delta    = 25.0                     # deg
    vehicle.reference_area        = 124.862                  # 
    vehicle.A_engine = np.pi*(0.9525)**2
    vehicle.Ultimate_Load     = 3.5
    vehicle.Limit_Load    = 1.5
    vehicle.control  = "fully powered" 
    vehicle.accessories = "medium range"
    vehicle.passengers = 170
    vehicle.cargo_weight = 10000.  * Units.kilogram
    
    
    # ------------------------------------------------------------------        
    #   Main Wing
    # ------------------------------------------------------------------        
    
    wing = SUAVE.Components.Wings.Wing()
    wing.tag = 'Main Wing'
    
    wing.Areas.reference = 124.862    #
    wing.aspect_ratio    = 8        #
    wing.Spans.projected = 35.66      #
    wing.sweep           = 25 * Units.deg
    wing.symmetric       = False
    wing.thickness_to_chord = 0.1
    wing.taper           = 0.16

    # size the wing planform
    SUAVE.Geometry.Two_Dimensional.Planform.wing_planform(wing)
    
    wing.Chords.mean_aerodynamic = 12.5
    wing.Areas.exposed = 0.8*wing.Areas.wetted
    wing.Areas.affected = 0.6*wing.Areas.wetted
    wing.span_efficiency = 0.9
    wing.Twists.root = 3.0*Units.degrees
    wing.Twists.tip  = 3.0*Units.degrees
    wing.origin          = [20,0,0]
    wing.aerodynamic_center = [3,0,0] 
    wing.vertical   = False
    wing.eta         = 1.0
    
    # add to vehicle
    vehicle.append_component(wing)
    
    
    # ------------------------------------------------------------------        
    #  Horizontal Stabilizer
    # ------------------------------------------------------------------        
    
    wing = SUAVE.Components.Wings.Wing()

    wing.tag = 'Horizontal Stabilizer' 
    
    wing.Areas.reference = 32.488    #
    wing.aspect_ratio    = 6.16      #
    wing.Spans.projected = 14.146      #
    wing.sweep           = 30 * Units.deg
    wing.symmetric       = True
    wing.thickness_to_chord = 0.08
    wing.taper           = 0.4

    # size the wing planform
    SUAVE.Geometry.Two_Dimensional.Planform.wing_planform(wing)
    
    wing.Chords.mean_aerodynamic = 8.0
    wing.Areas.exposed = 0.8*wing.Areas.wetted
    wing.Areas.affected = 0.6*wing.Areas.wetted
    wing.span_efficiency = 0.9
    wing.Twists.root = 3.0*Units.degrees
    wing.Twists.tip  = 3.0*Units.degrees  
    wing.origin          = [50,0,0]
    wing.aerodynamic_center = [2,0,0]
    wing.vertical   = False 
    wing.eta         = 0.9  

  
    # add to vehicle
    vehicle.append_component(wing)
    
    
    # ------------------------------------------------------------------
    #   Vertical Stabilizer
    # ------------------------------------------------------------------
    
    wing = SUAVE.Components.Wings.Wing()
    wing.tag = 'Vertical Stabilizer'    
    
    wing.Areas.reference = 32.488    #
    wing.aspect_ratio    = 1.91      #
    wing.Spans.projected = 7.877      #
    wing.sweep           = 25 * Units.deg
    wing.symmetric       = False
    wing.thickness_to_chord = 0.08
    wing.taper           = 0.4

    # size the wing planform
    SUAVE.Geometry.Two_Dimensional.Planform.wing_planform(wing)
    
    wing.Chords.mean_aerodynamic = 8.0
    wing.Areas.exposed = 0.8*wing.Areas.wetted
    wing.Areas.affected = 0.6*wing.Areas.wetted
    wing.span_efficiency = 0.9
    wing.Twists.root = 0.0*Units.degrees
    wing.Twists.tip  = 0.0*Units.degrees  
    wing.origin          = [50,0,0]
    wing.aerodynamic_center = [2,0,0]    
    wing.vertical   = True 
    wing.t_tail     = False
    wing.eta         = 1.0
        
    # add to vehicle
    vehicle.append_component(wing)


    # ------------------------------------------------------------------
    #  Fuselage
    # ------------------------------------------------------------------
    
    fuselage = SUAVE.Components.Fuselages.Fuselage()
    fuselage.tag = 'Fuselage'
    
    fuselage.number_coach_seats = 200
    fuselage.seats_abreast = 6
    fuselage.seat_pitch = 1
    fuselage.Fineness.nose = 1.6
    fuselage.Fineness.tail = 2.
    fuselage.Lengths.fore_space = 6.
    fuselage.Lengths.aft_space  = 5.
    fuselage.width = 4.
    fuselage.Heights.maximum          = 4.    #
    fuselage.Areas.side_projected       = 4.* 59.8 #  Not correct
    fuselage.Heights.at_quarter_length = 4. # Not correct
    fuselage.Heights.at_three_quarters_length = 4. # Not correct
    fuselage.Heights.at_wing_root_quarter_chord = 4. # Not correct
    fuselage.differential_pressure = 10**5   * Units.pascal    # Maximum differential pressure
    
    # size fuselage planform
    SUAVE.Geometry.Two_Dimensional.Planform.fuselage_planform(fuselage)
    
    # add to vehicle
    vehicle.append_component(fuselage)
    
    
    # ------------------------------------------------------------------
    #  Turbofan
    # ------------------------------------------------------------------    
    
    turbofan = SUAVE.Components.Propulsors.TurboFanPASS()
    turbofan.tag = 'Turbo Fan'
    
    turbofan.propellant = SUAVE.Attributes.Propellants.Jet_A()
    
    turbofan.analysis_type                 = '1D'     #
    turbofan.diffuser_pressure_ratio       = 0.98     #
    turbofan.fan_pressure_ratio            = 1.7      #
    turbofan.fan_nozzle_pressure_ratio     = 0.99     #
    turbofan.lpc_pressure_ratio            = 1.14     #
    turbofan.hpc_pressure_ratio            = 13.415   #
    turbofan.burner_pressure_ratio         = 0.95     #
    turbofan.turbine_nozzle_pressure_ratio = 0.99     #
    turbofan.Tt4                           = 1450.0   #
    turbofan.bypass_ratio                  = 5.4      #
    turbofan.Thrust = Data()
    turbofan.Thrust.design = 25000.0
    turbofan.design_thrust                 = 25000.0  #
    turbofan.no_of_engines                 = 2.0      #
    turbofan.engine_length                 = 4.0
    
    # turbofan sizing conditions
    sizing_segment = SUAVE.Components.Propulsors.Segments.Segment()
    
    sizing_segment.M   = 0.8          #
    sizing_segment.alt = 10.0         #
    sizing_segment.T   = 218.0        #
    sizing_segment.p   = 0.239*10**5  # 
    
    # size the turbofan
    turbofan.engine_sizing_1d(sizing_segment)     
    
    # add to vehicle
    vehicle.append_component(turbofan)

    vehicle.Mass_Props.breakdown = SUAVE.Methods.Weights.Correlations.Tube_Wing.empty(vehicle)
    vehicle.Mass_Props.m_empty = vehicle.Mass_Props.breakdown.empty
    
    # ------------------------------------------------------------------
    # compute wing fuel capacity
    # ------------------------------------------------------------------
    vehicle.Mass_Props.fuel_density = turbofan.propellant.density

    wing = vehicle.Wings['Main Wing']
    SUAVE.Geometry.Two_Dimensional.Planform.wing_fuel_volume(wing)
    vehicle.Mass_Props.max_usable_fuel = wing.fuel_volume * vehicle.Mass_Props.fuel_density # [kg]
    
    

    # ------------------------------------------------------------------
    #   Simple Aerodynamics Model
    # ------------------------------------------------------------------ 
    
    aerodynamics = SUAVE.Attributes.Aerodynamics.Fidelity_Zero_Supersonic()
    #aerodynamics = SUAVE.Attributes.Aerodynamics.Fidelity_Zero()
    aerodynamics.initialize(vehicle)
    
    # build stability model
    stability = SUAVE.Attributes.Flight_Dynamics.Fidelity_Zero()
    stability.initialize(vehicle)
    aerodynamics.stability = stability
    vehicle.aerodynamics_model = aerodynamics
    
    # ------------------------------------------------------------------
    #   Simple Propulsion Model
    # ------------------------------------------------------------------     
    
    vehicle.propulsion_model = vehicle.Propulsors

    # ------------------------------------------------------------------
    #   Define Configurations
    # ------------------------------------------------------------------

    # --- Takeoff Configuration ---
    config = vehicle.new_configuration("takeoff")
    # this configuration is derived from the baseline vehicle

    # --- Cruise Configuration ---
    config = vehicle.new_configuration("cruise")
    # this configuration is derived from vehicle.Configs.takeoff
    

    # ------------------------------------------------------------------
    #   Vehicle Definition Complete
    # ------------------------------------------------------------------
    
    return vehicle

#: def define_vehicle()


# ----------------------------------------------------------------------
#   Define the Mission
# ----------------------------------------------------------------------
def define_mission(vehicle):
    
    # ------------------------------------------------------------------
    #   Initialize the Mission
    # ------------------------------------------------------------------

    mission = SUAVE.Attributes.Missions.Mission()
    mission.tag = 'The Test Mission'

    # initial mass
    mission.m0 = vehicle.Mass_Props.m_full # linked copy updates if parent changes
    
    # atmospheric model
    atmosphere = SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()
    planet = SUAVE.Attributes.Planets.Earth()
    
    
    # ------------------------------------------------------------------
    #   First Climb Segment: constant Mach, constant segment angle 
    # ------------------------------------------------------------------
    
    segment = SUAVE.Attributes.Missions.Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "Climb - 1"
    
    # connect vehicle configuration
    segment.config = vehicle.Configs.takeoff
    
    # define segment attributes
    segment.atmosphere     = atmosphere
    segment.planet         = planet    
    
    segment.altitude_start = 0.0   * Units.km
    segment.altitude_end   = 3.0   * Units.km
    segment.air_speed      = 125.0 * Units['m/s']
    segment.climb_rate     = 6.0   * Units['m/s']
    
    # add to misison
    mission.append_segment(segment)
    
    
    # ------------------------------------------------------------------
    #   Second Climb Segment: constant Speed, constant segment angle 
    # ------------------------------------------------------------------    
    
    segment = SUAVE.Attributes.Missions.Segments.Climb.Constant_Speed_Constant_Rate()
    #segment = SUAVE.Attributes.Missions.Segments.Climb.Constant_Mach_Constant_Rate()
    segment.tag = "Climb - 2"
    
    # connect vehicle configuration
    segment.config = vehicle.Configs.cruise
    
    # segment attributes
    segment.atmosphere     = atmosphere
    segment.planet         = planet    
    
    #segment.altitude_start = 3.0   * Units.km ## Optional
    segment.altitude_end   = 8.0   * Units.km
    segment.air_speed      = 190.0 * Units['m/s']
    segment.climb_rate     = 6.0   * Units['m/s']
    #segment.mach_number    = 0.5
    #segment.climb_rate     = 6.0   * Units['m/s']
    
    # add to mission
    mission.append_segment(segment)

    
    # ------------------------------------------------------------------
    #   Third Climb Segment: constant Mach, constant segment angle 
    # ------------------------------------------------------------------    
    
    segment = SUAVE.Attributes.Missions.Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "Climb - 3"
    
    # connect vehicle configuration
    segment.config = vehicle.Configs.cruise
    
    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet        
    
    segment.altitude_end = 10.668 * Units.km
    segment.air_speed    = 226.0  * Units['m/s']
    segment.climb_rate   = 3.0    * Units['m/s']
    
    # add to mission
    mission.append_segment(segment)
    
    
    # ------------------------------------------------------------------    
    #   Cruise Segment: constant speed, constant altitude
    # ------------------------------------------------------------------    
    
    segment = SUAVE.Attributes.Missions.Segments.Cruise.Constant_Speed_Constant_Altitude()
    segment.tag = "Cruise"
    
    # connect vehicle configuration
    segment.config = vehicle.Configs.cruise
    
    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet        
    
    #segment.altitude   = 10.668  * Units.km     # Optional
    segment.air_speed  = 230.412 * Units['m/s']
    segment.distance   = 3933.65 * Units.km
        
    mission.append_segment(segment)

    # ------------------------------------------------------------------    
    #   First Descent Segment: consant speed, constant segment rate
    # ------------------------------------------------------------------    

    segment = SUAVE.Attributes.Missions.Segments.Descent.Constant_Speed_Constant_Rate()
    segment.tag = "Descent - 1"
    
    # connect vehicle configuration
    segment.config = vehicle.Configs.cruise
    
    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet   
    
    segment.altitude_end = 5.0   * Units.km
    segment.air_speed    = 170.0 * Units['m/s']
    segment.descent_rate = 5.0   * Units['m/s']
    
    # add to mission
    mission.append_segment(segment)
    

    # ------------------------------------------------------------------    
    #   Second Descent Segment: consant speed, constant segment rate
    # ------------------------------------------------------------------    

    segment = SUAVE.Attributes.Missions.Segments.Descent.Constant_Speed_Constant_Rate()
    segment.tag = "Descent - 2"

    # connect vehicle configuration
    segment.config = vehicle.Configs.cruise

    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet    
    
    segment.altitude_end = 0.0   * Units.km
    segment.air_speed    = 145.0 * Units['m/s']
    segment.descent_rate = 5.0   * Units['m/s']

    # append to mission
    mission.append_segment(segment)

    
    # ------------------------------------------------------------------    
    #   Mission definition complete    
    # ------------------------------------------------------------------
    
    return mission

#: def define_mission()


# ----------------------------------------------------------------------
#   Evaluate the Field Length
# ----------------------------------------------------------------------
def evaluate_field_length(vehicle):
    
    # ---------------------------
    # Check field performance
    # ---------------------------
    # define takeoff and landing configuration
    #print ' Defining takeoff and landing configurations'
    takeoff_config,landing_config = define_field_configs(vehicle)

    # define airport to be evaluated
    airport = SUAVE.Attributes.Airports.Airport()
    airport.altitude   =  0.0  * Units.ft
    airport.delta_isa  =  0.0
    airport.atmosphere =  SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()

    # evaluate takeoff / landing
    #print ' Estimating takeoff performance'
    TOFL = estimate_take_off_field_length(vehicle,takeoff_config,airport)
    #print ' Estimating landing performance'
    LFL = estimate_landing_field_length(vehicle,landing_config,airport)
    
    fldlength      = Data()
    fldlength.TOFL = TOFL
    fldlength.LFL  = LFL
    
    return fldlength

# ----------------------------------------------------------------------
#   Evaluate the Mission
# ----------------------------------------------------------------------
def evaluate_mission(vehicle,mission):
    
    # ------------------------------------------------------------------    
    #   Run Mission
    # ------------------------------------------------------------------
    results = SUAVE.Methods.Performance.evaluate_mission(mission)
   
    
    # ------------------------------------------------------------------    
    #   Compute Useful Results
    # ------------------------------------------------------------------
    #SUAVE.Methods.Results.compute_energies(results,summary=True)
    #SUAVE.Methods.Results.compute_efficiencies(results)
    #SUAVE.Methods.Results.compute_velocity_increments(results)
    #SUAVE.Methods.Results.compute_alpha(results)    
    
    return results

# ----------------------------------------------------------------------
#   Plot Results
# ----------------------------------------------------------------------
def post_process(vehicle,mission,results):
    
    # ------------------------------------------------------------------    
    #   Thrust Angle
    # ------------------------------------------------------------------
    #title = "Thrust Angle History"
    #plt.figure(0)
    #for i in range(len(results.Segments)):
        #plt.plot(results.Segments[i].t/60,np.degrees(results.Segments[i].gamma),'bo-')
    #plt.xlabel('Time (mins)'); plt.ylabel('Thrust Angle (deg)'); plt.title(title)
    #plt.grid(True)

    # ------------------------------------------------------------------    
    #   Throttle
    # ------------------------------------------------------------------
    plt.figure("Throttle History")
    axes = plt.gca()
    for i in range(len(results.Segments)):
        time = results.Segments[i].conditions.frames.inertial.time[:,0] / Units.min
        eta  = results.Segments[i].conditions.propulsion.throttle[:,0]
        axes.plot(time, eta, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Throttle')
    axes.grid(True)

    # ------------------------------------------------------------------    
    #   Angle of Attack
    # ------------------------------------------------------------------
    #title = "Angle of Attack History"
    #plt.figure(2)
    #for i in range(len(results.Segments)):
        #plt.plot(results.Segments[i].t/60,np.degrees(results.Segments[i].alpha),'bo-')
    #plt.xlabel('Time (mins)'); plt.ylabel('Angle of Attack (deg)'); plt.title(title)
    #plt.grid(True)
    
    plt.figure("Angle of Attack History")
    axes = plt.gca()    
    for i in range(len(results.Segments)):     
        time = results.Segments[i].conditions.frames.inertial.time[:,0] / Units.min
        aoa = results.Segments[i].conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        axes.plot(time, aoa, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Angle of Attack (deg)')
    axes.grid(True)        

    # ------------------------------------------------------------------    
    #   Fuel Burn
    # ------------------------------------------------------------------
    #title = "Fuel Burn"
    #plt.figure(3)
    #for i in range(len(results.Segments)):
        #plt.plot(results.Segments[i].t/60,mission.m0 - results.Segments[i].m,'bo-')
    #plt.xlabel('Time (mins)'); plt.ylabel('Fuel Burn (kg)'); plt.title(title)
    #plt.grid(True)

    # ------------------------------------------------------------------    
    #   Fuel Burn Rate
    # ------------------------------------------------------------------
    plt.figure("Fuel Burn Rate")
    axes = plt.gca()    
    for i in range(len(results.Segments)):     
        time = results.Segments[i].conditions.frames.inertial.time[:,0] / Units.min
        mdot = results.Segments[i].conditions.propulsion.fuel_mass_rate[:,0]
        axes.plot(time, mdot, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Fuel Burn Rate (kg/s)')
    axes.grid(True)    

    
    
    # ------------------------------------------------------------------    
    #   Altitude
    # ------------------------------------------------------------------
    plt.figure("Altitude")
    axes = plt.gca()    
    for i in range(len(results.Segments)):     
        time     = results.Segments[i].conditions.frames.inertial.time[:,0] / Units.min
        altitude = results.Segments[i].conditions.freestream.altitude[:,0] / Units.km
        axes.plot(time, altitude, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Altitude (km)')
    axes.grid(True)
    
    
    # ------------------------------------------------------------------    
    #   Vehicle Mass
    # ------------------------------------------------------------------    
    plt.figure("Vehicle Mass")
    axes = plt.gca()
    for i in range(len(results.Segments)):
        time = results.Segments[i].conditions.frames.inertial.time[:,0] / Units.min
        mass = results.Segments[i].conditions.weights.total_mass[:,0]
        axes.plot(time, mass, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Vehicle Mass (kg)')
    axes.grid(True)
    

    # ------------------------------------------------------------------    
    #   Atmosphere
    # ------------------------------------------------------------------
    #title = "Atmosphere"
    #plt.figure(7)    
    #plt.title(title)
    #for segment in results.Segments.values():

        #plt.subplot(3,1,1)
        #plt.plot( segment.t / Units.minute , 
                  #segment.rho * np.ones_like(segment.t),
                  #'bo-' )
        #plt.xlabel('Time (min)')
        #plt.ylabel('Density (kg/m^3)')
        #plt.grid(True)
        
        #plt.subplot(3,1,2)
        #plt.plot( segment.t / Units.minute , 
                  #segment.p * np.ones_like(segment.t) ,
                  #'bo-' )
        #plt.xlabel('Time (min)')
        #plt.ylabel('Pressure (Pa)')
        #plt.grid(True)
        
        #plt.subplot(3,1,3)
        #plt.plot( segment.t / Units.minute , 
                  #segment.T * np.ones_like(segment.t) ,
                  #'bo-' )
        #plt.xlabel('Time (min)')
        #plt.ylabel('Temperature (K)')
        #plt.grid(True)
    
    
    # ------------------------------------------------------------------    
    #   Aerodynamics
    # ------------------------------------------------------------------
    fig = plt.figure("Aerodynamic Forces")
    for segment in results.Segments.values():
        
        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        Lift   = -segment.conditions.frames.wind.lift_force_vector[:,2]
        Drag   = -segment.conditions.frames.wind.drag_force_vector[:,0]
        Thrust = segment.conditions.frames.body.thrust_force_vector[:,0]
        #Pitching_moment = segment.conditions.aerodynamics.cm_alpha[:,0]

        axes = fig.add_subplot(4,1,1)
        axes.plot( time , Lift , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('Lift (N)')
        axes.grid(True)
        
        axes = fig.add_subplot(4,1,2)
        axes.plot( time , Drag , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('Drag (N)')
        axes.grid(True)
        
        axes = fig.add_subplot(4,1,3)
        axes.plot( time , Thrust , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('Thrust (N)')
        axes.grid(True)        
        
        #axes = fig.add_subplot(4,1,4)
        #axes.plot( time , Pitching_moment , 'bo-' )
        #axes.set_xlabel('Time (min)')
        #axes.set_ylabel('Pitching_moment (~)')
        #axes.grid(True)
        
    # ------------------------------------------------------------------    
    #   Aerodynamics 2
    # ------------------------------------------------------------------
    fig = plt.figure("Aerodynamic Coefficients")
    for segment in results.Segments.values():
        
        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        CLift  = segment.conditions.aerodynamics.lift_coefficient[:,0]
        CDrag  = segment.conditions.aerodynamics.drag_coefficient[:,0]
        Drag   = -segment.conditions.frames.wind.drag_force_vector[:,0]
        Thrust = segment.conditions.frames.body.thrust_force_vector[:,0]

        axes = fig.add_subplot(3,1,1)
        axes.plot( time , CLift , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('CL')
        axes.grid(True)
        
        axes = fig.add_subplot(3,1,2)
        axes.plot( time , CDrag , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('CD')
        axes.grid(True)
        
        axes = fig.add_subplot(3,1,3)
        axes.plot( time , Drag   , 'bo-' )
        axes.plot( time , Thrust , 'ro-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('Drag and Thrust (N)')
        axes.grid(True)
    
    
    # ------------------------------------------------------------------    
    #   Aerodynamics 2
    # ------------------------------------------------------------------
    fig = plt.figure("Drag Components")
    axes = plt.gca()    
    for i, segment in enumerate(results.Segments.values()):
        
        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        drag_breakdown = segment.conditions.aerodynamics.drag_breakdown
        cdp = drag_breakdown.parasite.total[:,0]
        cdi = drag_breakdown.induced.total[:,0]
        cdc = drag_breakdown.compressible.total[:,0]
        cdm = drag_breakdown.miscellaneous.total[:,0]
        cd  = drag_breakdown.total[:,0]
        
        
        axes.plot( time , cdp , 'ko-', label='CD_P' )
        axes.plot( time , cdi , 'bo-', label='CD_I' )
        axes.plot( time , cdc , 'go-', label='CD_C' )
        axes.plot( time , cdm , 'yo-', label='CD_M' )
        axes.plot( time , cd  , 'ro-', label='CD'   )
        
        if i == 0:
            axes.legend(loc='upper center')
        
    axes.set_xlabel('Time (min)')
    axes.set_ylabel('CD')
    axes.grid(True)
    
    return     


# Check stability using something of the form
# cm_alpha = results.Segments.Cruise.conditions.aerodynamics.cm_alpha


# ----------------------------------------------------------------------
#   Define takeoff and landing configuration
# ----------------------------------------------------------------------
def define_field_configs(vehicle):

    # Imports
    import copy

    # --- Takeoff Configuration ---
    takeoff_config = vehicle.Configs.takeoff
    takeoff_config.Wings['Main Wing'].flaps_angle =  20. * Units.deg
    takeoff_config.Wings['Main Wing'].slats_angle  = 25. * Units.deg
    # V2_V2_ratio may be informed by user. If not, use default value (1.2)
    takeoff_config.V2_VS_ratio = 1.21
    # CLmax for a given configuration may be informed by user. If not, is calculated using correlations
    takeoff_config.maximum_lift_coefficient = 2.
    #takeoff_config.max_lift_coefficient_factor = 1.0

    # --- Landing Configuration ---
    landing_config = vehicle.new_configuration("landing")
    landing_config.Wings['Main Wing'].flaps_angle =  30. * Units.deg
    landing_config.Wings['Main Wing'].slats_angle  = 25. * Units.deg
    # Vref_V2_ratio may be informed by user. If not, use default value (1.23)
    landing_config.Vref_VS_ratio = 1.23
    # CLmax for a given configuration may be informed by user
    landing_config.maximum_lift_coefficient = 2.
    #landing_config.max_lift_coefficient_factor = 1.0
    landing_config.Mass_Props.m_landing = 0.85 * vehicle.Mass_Props.m_takeoff

    return takeoff_config,landing_config


# ---------------------------------------------------------------------- 
#   Module Tests
# ----------------------------------------------------------------------

if __name__ == '__main__':
    
    profile_module = False
        
    if not profile_module:
        
        main()
        plt.show()        
        
    else:
        profile_file = 'log_Profile.out'
        
        import cProfile
        cProfile.run('import tut_mission_Boeing_737800 as tut; tut.profile()', profile_file)
        
        import pstats
        p = pstats.Stats(profile_file)
        p.sort_stats('time').print_stats(20)        
        
        import os
        os.remove(profile_file)
    
#: def main()


def profile():
    t0 = time.time()
    vehicle = define_vehicle()
    mission = define_mission(vehicle)
    results = evaluate_mission(vehicle,mission)
    print 'Run Time:' , (time.time()-t0)