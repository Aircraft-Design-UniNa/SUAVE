#by M. Vegh
#note; this script uses the old SUAVE mission at the moment
import SUAVE
import numpy as np
import scipy as sp
import pylab as plt
import copy
import time
import matplotlib
from SUAVE.Methods.Performance import estimate_take_off_field_length
from SUAVE.Methods.Performance import estimate_landing_field_length 
matplotlib.interactive(True)


from pint import UnitRegistry
from SUAVE.Attributes import Units as Units
# ----------------------------------------------------------------------
#   Inputs
# ----------------------------------------------------------------------

def main():
    #use global variables for guess to make optimization faster
    
    global m_guess
    global Ereq_guess
    global Preq_guess
    global iteration_number
    global disp_results #set to 0 unless you want to display plots
    #use these global variables so both optimizer aircraft have access to constraints
    
    global target_range #target overall range
    global wclimb1 #vertical velocity for climb segment 1
    global wclimb2
    global wclimb3
    global wclimb4
    global wclimb5
    global wdesc1 #vertical velocity for descent segment 1
    global wdesc2
    global wdesc3
    
    global Vdesc1 #velocity magnitude of first descent segment
    global Vdesc2
    global Vdesc3
    
    m_guess=  51576.4220961
    Ereq_guess = 80599244272.8               # required energy
    Preq_guess=    14516323.309 
    disp_results=1                              #1 for displaying results, 0 for optimize    
    target_range=2800
    
    wclimb1=3000.*(Units.ft/Units.minute)
    wclimb2=2500.*(Units.ft/Units.minute)
    wclimb3=1800.*(Units.ft/Units.minute)
    wclimb4=900.*(Units.ft/Units.minute)
    wclimb5=200.*(Units.ft/Units.minute)
    
    wdesc1=2600.*(Units.ft/Units.minute)
    wdesc2=2300.*(Units.ft/Units.minute)
    wdesc3=1500.*(Units.ft/Units.minute)
    
    Vdesc1=230.
    Vdesc2=200.
    Vdesc3=140.0 
    
    iteration_number=1
    
    
    #Preq=  1.00318268e+07                     #estimated power requirements for cruise
    Ereq_lis=  2.7621607e+09                 #remaining power requirement for lithium sulfur battery
    Preq_lis= 3.98197096e+06
    
    
    #############
    #input guesses and indices
    i=0
    P_mot        =2E7;    i_P_mot=copy.copy(i);          i+=1
    climb_alt_1  =.01;   i_climb_alt_1=copy.copy(i);    i+=1
    climb_alt_2  =.1;    i_climb_alt_2=copy.copy(i);    i+=1
    climb_alt_3  =1;     i_climb_alt_3=copy.copy(i);    i+=1
    climb_alt_4  =2;     i_climb_alt_4=copy.copy(i);    i+=1
    climb_alt_5  =3;     i_climb_alt_5=copy.copy(i);    i+=1
    alpha_rc     =-1.2;  i_alpha_rc=copy.copy(i);       i+=1
    alpha_tc     =-1.3;  i_alpha_tc=copy.copy(i);       i+=1
    wing_sweep   =0.1;   i_wing_sweep=copy.copy(i);     i+=1
    vehicle_S    =45;    i_vehicle_S=copy.copy(i);      i+=1
    Vclimb_1     =120.;  i_Vclimb_1=copy.copy(i);       i+=1
    Vclimb_2     =130;   i_Vclimb_2=copy.copy(i);       i+=1
    Vclimb_3     =200;   i_Vclimb_3=copy.copy(i);       i+=1
    Vclimb_4     =210;   i_Vclimb_4=copy.copy(i);       i+=1
    Vclimb_5     =230;   i_Vclimb_5=copy.copy(i);       i+=1
    desc_alt_1   =2.;    i_desc_alt_1=copy.copy(i);     i+=1
    desc_alt_2   =1;     i_desc_alt_2=copy.copy(i);     i+=1
    cruise_range=2900;   i_cruise_range=copy.copy(i);   i+=1 #cruise range in km
 
    
    
    #range        =4.12781663e+03 preliminary calc for min Weight/range
   
    #wing_sweep=25
  

    #inputs=[  1.09054811e+11 ,  1.57963981e-01  , 2.66041483e-01 ,  1.41709413e+00, 3.08597883e+00 ,  6.21923270e+00 ,  7.59263894e-01 , -1.82784674e-02,   4.14179730e-04 ,  8.98849634e+01 ,  1.21002104e+02,   1.64754015e+02,   2.01648275e+02  , 2.30416367e+02  , 2.44539233e+03]
    #inputs=   [  1.31584398e+11 ,  4.54129682e+00 , -9.15734295e+00  , 2.60026466e+00,   2.63153086e+00 ,  6.02593615e+00 ,  1.19244464e+00 , -3.45626189e+00,   8.87913318e-03 ,  1.01237339e+02  , 1.55975682e+02 ,  1.64117776e+02,   1.83349067e+02  , 2.30419853e+02  , 2.86384406e+03]
   
   
    """
    Li-S
    inputs= [  8.30342833e+10  , 2.99062504e+10,   4.77626013e+06 ,  2.86536336e+00,  5.53443366e+00 ,  5.53620145e+00 ,  5.70223223e+00 ,  5.89191450e+00,
   4.71228083e+00 , -2.28259122e+00 ,  6.78616016e-08 ,  1.19645462e+02,
   1.10636483e+02 ,  1.47459194e+02 ,  1.84638188e+02  , 2.05206786e+02,
   1.85829008e+02 ,  2.30319308e+02 ,  2.22268873e+03]
    """
     
     
    '''
    HTS motor
    inputs= [  1.43280279e+11 ,  9.96518458e+03 ,  1.94031572e+00 ,  2.23488120e+00,
   5.77988090e+00,   5.84318575e+00,   5.87763323e+00 ,  5.96894385e+00,
   3.12203152e+00 , -5.00000000e+00,   1.01559982e-04  , 8.86687710e+01,
   1.59656249e+02 ,  1.96067314e+02,   2.07856525e+02  , 1.97506660e+02,
   2.00247865e+02  , 2.30000000e+02,   3.54134441e+03]
   '''
    
    
   
    #esp=1500 W-h/kg, range =3800 km
    #inputs= [  2.08480239e+11 ,  1.56398971e+02  , 2.26671872e+02 ,  2.13920953e+00,  5.26093979e+00 ,  5.70421849e+00 ,  5.76221019e+00 ,  5.76221019e+00,  9.08494888e-01 , -4.97338819e+00 ,  2.03386957e-04 ,  1.56432236e+02,   1.31848163e+02 ,  1.57824691e+02 ,  1.74230984e+02 ,  2.00350719e+02,   2.62705750e+02 ,  2.30000000e+02 ,  3.58529306e+03]
   
    #esp=4000 W-h/kg, range=3800 km
    #inputs= [  2.38659244e+11 ,  2.30908552e+04  , 5.14354632e+03  , 2.39493637e+00,  6.46783420e+00,   6.46783421e+00,   6.50325679e+00,   6.50325679e+00,  5.00000000e+00,  -4.99986122e+00 , -2.42616090e-07,   1.03206563e+02, 1.35560173e+02,   1.67515945e+02 ,  1.82203092e+02,   1.70670293e+02,   2.44657141e+02,   2.30000000e+02 ,  3.55771157e+03]

    
    #esp=2000 W-h/kg, range=2400 km
    #inputs=   [  2.53815497e+00 ,  4.61192540e+00 ,  5.81856327e+00,   5.88529881e+00,   5.95456804e+00 ,  1.76614416e+00,  -4.91528402e+00  , 1.31966981e-04,  7.96927333e+01 ,  1.20086331e+02 ,  1.75800907e+02  , 1.73174135e+02,   1.77817946e+02 ,  2.36432755e+02  , 5.94550201e+00 ,  2.42198671e+00,  2.13912785e+03]
    
    #esp=2000 W-h/kg, range=2800 km
    #inputs=[ 0.467209021655 , 1.27293988564 , 1.85802379477 , 1.8621555086 , 1.8671215789 ,-0.707681912748 , -1.31788259783 , 0.143355045854 , 0.538928037207 , 1.13491212744 , 1.92048423657 , 1.46775596285 , 2.85787886319 , 4.52876031895 , 1.60762801081 , 1.54643552768 , 2.67558189044 ]
    
    #inputs=[ 2,0.468244170166 , 1.26874271427 , 1.84022847142 , 1.85751448543 , 1.88643292462 , -0.700035789367 , -1.31889951334 , 0.144545293544 , 0.585963003498 , 1.1168729121 , 1.93452131072 , 1.44445022216 , 2.82497244468 , 4.5412005635 , 1.59345188164 , 1.53665598543 , 2.68414711192 ]
    
    #inputs=[ 2.35471045825 , 0.749770697875 , 1.01292291492 , 1.84022720731 , 2.09651706445 , 8.87434429581 , -0.700710341707 , -1.31914728571 , 0.143808586845 , 2.5 , 1.11687164799 , 1.93452131072 , 1.44445022216 , 1.95467047186 , 1.61929778229 , 1.59345188164 , 1.53665469195 , 2.20868832467 ]
    
    
    inputs=[ 0.649603170822 , 0.770593378919 , 1.05661024486 , 2.02101698489 , 2.65915402573 , 9.41019048066 , -0.699000885392 , -1.29187356582 , 0.149887094925 , 2.21086955626 , 1.203404708 , 1.7228943961 , 1.50786337832 , 2.45517458626 , 1.75939883918 , 1.72107280368 , 1.45504862718 , 2.19682443384 ]
    
    
    #esp=2000 W-h/kg, range=3200 km
    #inputs=[ 0.470029448307 , 1.26947524619 , 1.85810727593 , 1.86213329794 , 1.86694875807 , -0.691113957423 , -1.31307426953 , 0.142700687499 , 0.581284773469 , 1.13387366919 , 1.92609226134 , 1.57023731049 , 2.91504989357 , 4.66307617502 , 1.58758074085 , 1.54640434974 , 3.0755932169 ]
   

    #esp=2000 W-h/kg, range=3600 km
    #inputs=[ 0.475476458321 , 1.26203711498 , 1.85814404874 , 1.86212146795 , 1.86691124225 , -0.674056519244 , -1.31112001738 , 0.142223790287 , 0.626399491242 , 1.14291602718 , 1.93198873427 , 1.59487731726 , 2.89755838438 , 4.64721234556 , 1.579735713 , 1.5463960166 , 3.47560016152 ]
    
    
    
   
    
    #esp=2000 W-h/kg, range=3800 km
    #inputs=[ 0.47715012641 , 1.26298351675 , 1.85719754626 , 1.85945629174 , 1.87098293017, -0.668964227128 , -1.31828904855 , 0.142979804655 , 0.647129378964 , 1.1519159059 , 1.92717914003 , 1.60602814877 , 2.97807881922 , 4.66737619502 , 1.59555455298 , 1.54812129622 , 3.67532550007 ]
    
   
    
    #esp=2000 W-h/kg, range=4000 km
    #inputs=[ 0.491767140436 , 1.27058254361 , 1.85794702776 , 1.85878043005 , 1.85925137562, -0.665607182541 , -1.32002260329 , 0.144436076491 , 0.674617108957 , 1.14098351656 , 1.92345824026 , 1.62813110765 , 3.05625539135 , 4.67822931505 , 1.58321993017 , 1.54946691238 , 3.87611025656 ]
    
    #esp=2000 W-h/kg, range=4400 km
    #inputs= [ 0.491076682602 , 1.2739056184 , 1.85786391596 , 1.85876113889 , 1.85925553583, -0.665494713287 , -1.28458141386 , 0.147215877787 , 0.723623929342 , 1.18597407947 , 1.9315405453 , 1.61376009129 , 3.06757818663 , 4.62147883133 , 1.57104386153 , 1.54937172862 , 4.27610857514 ]
    
    
    
    #esp=2000 W-h/kg, range=4800 km
    #inputs= [ 0.488304800042 , 1.30480539663 , 1.85623876629 , 1.85866209269 , 1.86283747334 , -0.662853251298 , -1.27974927486 , 0.145756108049 , 0.786262717677 , 1.18369357756 , 1.96791351625 , 1.60255185453 , 3.05472358099 , 4.5962675229 , 1.5929518542 , 1.54881790245 , 4.67609500617 ]
    
    
    #esp=2000 W-h/kg, range=5200 km
    #inputs= [ 0.494469134893 , 1.37780676066 , 1.85564259255 , 1.85771194918 , 1.85887508966 , -0.661184242357 , -1.274571189 , 0.146431340215 , 0.836903976357 , 1.19464466793 , 1.97403457512 , 1.61340016387 , 3.01965789885 , 4.64087960543 , 1.59917190572 , 1.55246578773 , 5.07614324659 ]
    
    #esp=2000 W-h/kg, range=5600 km
    #inputs= [ 0.485221871951 , 1.35392973839 , 1.856096857 , 1.85778349155 , 1.85826003839 , -0.670633940334 , -1.27850964161 , 0.147907540489 , 0.902220698898 , 1.19366780453 , 1.94767565835 , 1.60002989374 , 3.02131095632 , 4.62567711756 , 1.60699232975 , 1.55257546111 , 5.47617433263 ]
    
    
    #out=sp.optimize.basinhopping(run, inputs, niter=1E5)
    
    
    
    #out=sp.optimize.fmin_bfgs(run,inputs)
    
    #bounds for bfgs
    if disp_results:
        mass_out=run(inputs)
    else: #you are running an optimization
        #bounds for simulated annealing
        lower_bounds=[1,  .01,.01,0.1,0.1,  0.1, -5., -5.,0.01,  50./100.,  50./100., 50./100.,  50./100.,  50./100.,  50./100.,   .1,   .1, 1800./1000.]
        upper_bounds=[1E3, 8.,10, 10., 10., 12., 5. , 5., 25. , 250./100., 230./100, 230./100., 230./100., 230./100., 230./100. , 11.,  11., 3800./1000.]
        mybounds=[]
        for i in range(len(lower_bounds)):
            mybounds.append((lower_bounds[i], upper_bounds[i]))
        
        #bounds for l_bfgs
        #mybounds=[(0., 11.), (0., 11.), (0., 11.), (0., 11.) ,(0., 11.),(-5.,5), (-5.,5.),(0., 25.),(0.,300.), (0., 100.),(50.,300.),(50.,300.),(50.,300.),(50.,300.), (50., 300.), (0., 11.), (0., 11.),(1000.,None)]
    
       
        #constraints in the design variables
        
        cons=({'type': 'ineq', 'fun': lambda inputs: inputs[i_climb_alt_2]-inputs[i_climb_alt_1]},
        {'type':'ineq', 'fun': lambda inputs: inputs[i_climb_alt_3]-inputs[i_climb_alt_2]},
        {'type':'ineq', 'fun': lambda inputs: inputs[i_climb_alt_4]-inputs[i_climb_alt_3]},
        {'type':'ineq', 'fun': lambda inputs: inputs[i_climb_alt_5]-inputs[i_climb_alt_4]},
        {'type':'ineq', 'fun': lambda inputs: inputs[i_alpha_rc]-inputs[i_alpha_tc]},
        {'type':'ineq', 'fun': lambda inputs: inputs[i_desc_alt_1]-inputs[i_desc_alt_2]},
        {'type':'ineq', 'fun': lambda inputs: inputs[i_climb_alt_1]/np.tan(np.arcsin(wclimb1/(100*inputs[i_Vclimb_1])))+ 
        (inputs[i_climb_alt_2]-inputs[i_climb_alt_1])/np.tan(np.arcsin(wclimb2/(100*inputs[i_Vclimb_2])))+
        (inputs[i_climb_alt_3]-inputs[i_climb_alt_2])/np.tan(np.arcsin(wclimb3/(100*inputs[i_Vclimb_3])))+
        (inputs[i_climb_alt_4]-inputs[i_climb_alt_3])/np.tan(np.arcsin(wclimb4/(100*inputs[i_Vclimb_4])))+
        (inputs[i_climb_alt_5]-inputs[i_climb_alt_4])/np.tan(np.arcsin(wclimb5/(100*inputs[i_Vclimb_5])))+
        inputs[i_cruise_range]*1000+
        (inputs[i_climb_alt_5]-inputs[i_desc_alt_1])/np.tan(np.arcsin(wdesc1/(Vdesc1)))+
        (inputs[i_desc_alt_1]-inputs[i_desc_alt_2])/np.tan(np.arcsin(wdesc2/(Vdesc2)))+
        inputs[i_desc_alt_2]/np.tan(np.arcsin(wdesc3/(Vdesc3)))-target_range})
        
        '''
        print 'range1=',  inputs[i_climb_alt_1]/np.tan(np.arcsin(wclimb1/(100*inputs[i_Vclimb_1])))
        print 'range2=', (inputs[i_climb_alt_2]-inputs[i_climb_alt_1])/np.tan(np.arcsin(wclimb2/(100*inputs[i_Vclimb_2])))
        print 'range3=', (inputs[i_climb_alt_3]-inputs[i_climb_alt_2])/np.tan(np.arcsin(wclimb3/(100*inputs[i_Vclimb_3])))
        print 'range4=', (inputs[i_climb_alt_4]-inputs[i_climb_alt_3])/np.tan(np.arcsin(wclimb4/(100*inputs[i_Vclimb_4])))
        print 'range5=', (inputs[i_climb_alt_5]-inputs[i_climb_alt_4])/np.tan(np.arcsin(wclimb5/(100*inputs[i_Vclimb_5])))
        print 'ranged1=',(inputs[i_climb_alt_5]-inputs[i_climb_alt_4])/np.tan(np.arcsin(wclimb5/(100*inputs[i_Vclimb_5])))
        print 'ranged2=',(inputs[i_desc_alt_1]-inputs[i_desc_alt_2])/np.tan(np.arcsin(wdesc2/(Vdesc2)))
        print 'ranged3=',inputs[i_desc_alt_2]/np.tan(np.arcsin(wdesc3/(Vdesc3)))
        print 'desc_alt_2=', inputs[i_desc_alt_2]
        print 'desc_alt_1=', inputs[i_desc_alt_1]
        
        print 'climb_alt_5=', inputs[i_climb_alt_5]
        print 'climb_alt_4=', inputs[i_climb_alt_4]
        print 'climb_alt_3=', inputs[i_climb_alt_3]
        print 'climb_alt_2=', inputs[i_climb_alt_2]
        print 'climb_alt_1=', inputs[i_climb_alt_1]
        '''
        #print 'range=', inputs[i_climb_alt_1]/np.tan(np.arcsin(wclimb1/(100*inputs[i_Vclimb_1])))+ (inputs[i_climb_alt_2]-inputs[i_climb_alt_1])/np.tan(np.arcsin(wclimb2/(100*inputs[i_Vclimb_2])))+(inputs[i_climb_alt_3]-inputs[i_climb_alt_2])/np.tan(np.arcsin(wclimb3/(100*inputs[i_Vclimb_3])))+(inputs[i_climb_alt_4]-inputs[i_climb_alt_3])/np.tan(np.arcsin(wclimb4/(100*inputs[i_Vclimb_4])))+(inputs[i_climb_alt_5]-inputs[i_climb_alt_4])/np.tan(np.arcsin(wclimb5/(100*inputs[i_Vclimb_5])))+inputs[i_cruise_range]*1000+(inputs[i_climb_alt_5]-inputs[i_desc_alt_1])/np.tan(np.arcsin(wdesc1/(Vdesc1)))+(inputs[i_desc_alt_1]-inputs[i_desc_alt_2])/np.tan(np.arcsin(wdesc2/(Vdesc2)))+inputs[i_desc_alt_2]/np.tan(np.arcsin(wdesc3/(Vdesc3)))
        
        #{'type':'ineq', 'fun': lambda inputs: inputs[5]-inputs[6]},
        
        #out=sp.optimize.anneal(run, inputs, lower=lower_bounds, upper=upper_bounds)
        #out=sp.optimize.fmin_l_bfgs_b(run,x0=inputs, bounds=mybounds, approx_grad=True)
        
        #sp.optimize.minimize(run, inputs, method='SLSQP', bounds=mybounds, constraints=cons)
        sp.optimize.minimize(run, inputs, method='Nelder-Mead', bounds=mybounds, constraints=cons)
        #print mybounds
        #print inputs
        #out=sp.optimize.fmin(run, inputs)
    
    


# ----------------------------------------------------------------------
#   Calls
# ----------------------------------------------------------------------
def run(inputs):                #sizing loop to enable optimization
    time1=time.time()
    global target_range           #minimum flight range of the aircraft (constraint)
    i=0 #counter for inputs
    #uncomment these global variables unless doing monte carlo optimization
    
    global m_guess
   
    global Ereq_guess
    global Preq_guess
    
    #start from same initial guess if monte carlo optimization
    """
    m_guess=   61475.7561613  
    Ereq_guess = 106763352375.0                 # required energy
    Preq_guess=  10455659.345
    """
    global iteration_number
    global disp_results
    
    #mass=[ 100034.162173]
    #mass=[ 113343.414181]                 
    if np.isnan(m_guess) or m_guess>1E7:
        m_guess=10000.

    if np.isnan(Ereq_guess) or Ereq_guess>1E13:
        Ereq_guess=1E10
        print 'Ereq nan'
    if np.isnan(Preq_guess) or Preq_guess>1E10:
        Preq_guess=1E6
        print 'Preq nan'
    print 'mguess=', m_guess
    mass=[ m_guess ]       #mass guess, 2000 W-h/kg
    Ereq=[Ereq_guess]
    #Preq=[Preq_guess]
    P_mot      =inputs[i];       i+=1
    climb_alt_1=inputs[i];       i+=1
    climb_alt_2=inputs[i];       i+=1
    climb_alt_3=inputs[i];       i+=1
    climb_alt_4=inputs[i];       i+=1
    climb_alt_5=inputs[i];       i+=1
    alpha_rc=inputs[i];          i+=1
    alpha_tc=inputs[i];          i+=1
    wing_sweep=inputs[i];        i+=1
    vehicle_S=inputs[i]*100;     i+=1
    Vclimb_1=inputs[i]*100;      i+=1
    Vclimb_2=inputs[i]*100;      i+=1
    Vclimb_3=inputs[i]*100;      i+=1
    Vclimb_4=inputs[i]*100;      i+=1
    Vclimb_5=inputs[i]*100;      i+=1
    desc_alt_1=inputs[i];        i+=1
    desc_alt_2=inputs[i];        i+=1
    cruise_range=inputs[i]*1000; i+=1

    Preq=P_mot*10**7   #set power as an input
    
    
    #V_cruise =inputs[i];         i+=1
    V_cruise=230.
    
    
    tol=.1 #difference in mass in kg between iterations
    dm=10000. #initialize error
    if disp_results==0:
        max_iter=20
    else:
        max_iter=30
    j=0
     
   
    while abs(dm)>tol:      #size the vehicle
        m_guess=mass[j]
        
        Ereq_guess=Ereq[j]
        #Preq_guess=Preq[j]
        
        vehicle = define_vehicle(m_guess,Ereq_guess, Preq, climb_alt_5,wing_sweep, alpha_rc, alpha_tc, vehicle_S, V_cruise)
        mission = define_mission(vehicle,climb_alt_1,climb_alt_2,climb_alt_3, climb_alt_4,climb_alt_5, desc_alt_1, desc_alt_2, Vclimb_1, Vclimb_2, Vclimb_3, Vclimb_4,Vclimb_5,V_cruise , cruise_range)
        results = evaluate_mission(vehicle,mission)
        results = evaluate_field_length(vehicle,mission,results) #now evaluate field length
        
        
        mass.append(vehicle.mass_properties.m_end)
        Ereq.append(results.Etotal)
        #Preq.append(results.Pmax)
        dm=mass[j+1]-mass[j]
        print 'mass=', mass[j+1]
        print 'dm=', dm
        print 'Ereq_guess=', Ereq_guess 
        print 'Preq=', Preq
        j+=1
        if j>max_iter:
            print "maximum number of iterations exceeded"
            break
    #vehicle sized and defined now
    
 
    
    
    #post_process(vehicle,mission,results)
    #add penalty function for battery
   
    #find minimum energy for each battery

    max_alpha=np.zeros(len(results.segments))
    min_alpha=np.zeros(len(results.segments))
    for i in range(len(results.segments)):
        #min_Ebat[i]=min(results.segments[i].Ecurrent)
        aoa=results.segments[i].conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        #Smin_Ebat_lis[i]=min(results.segments[i].Ecurrent_lis)
        
        max_alpha[i]=max(aoa)
        min_alpha[i]=min(aoa)
        
    max_alpha=max(max_alpha)
    min_alpha=min(min_alpha)
    
    #results.segments[i].Ecurrent_lis=battery_lis.CurrentEnergy
    #penalty_energy=abs(min(min_Ebat/battery.TotalEnergy, min_Ebat_lis/battery_lis.TotalEnergy,0.))*10.**8.
    #penalty_bat_neg=(10.**4.)*abs(min(0.,Ereq_lis, Preq_lis))   #penalty to make sure none of the inputs are negative
    
    
    vehicle.mass_properties.m_full=results.segments[0].conditions.weights.total_mass[:,0]    #make the vehicle the final mass
    if  disp_results:
        print 'climb_alt1=', climb_alt_1
        print 'Vclimb_1=', Vclimb_1
        print 'climb_alt2=', climb_alt_2
        print 'Vclimb_2=', Vclimb_2
        print 'climb_alt3=', climb_alt_3
        print 'Vclimb_3=', Vclimb_3
        print 'climb_alt4=', climb_alt_4
        print 'Vclimb_4=', Vclimb_4
        print 'climb_alt_5=', climb_alt_5
        print 'Vclimb_5=', Vclimb_5
        print 'desc_alt_1=', desc_alt_1
        print 'desc_alt_2=', desc_alt_2
  
        #print 'V_cruise=' ,V_cruise
        print 'alpha_rc=', alpha_rc
        print 'alpha_tc=', alpha_tc
        print 'wing_sweep=', wing_sweep
        print 'Sref=', vehicle_S
        print 'cruise range=', cruise_range
        print 'total range=', results.segments[-1].conditions.frames.inertial.position_vector[-1,0]/1000
        print 'takeoff mass=', results.segments[0].conditions.weights.total_mass[-1,0] 
        print 'landing mass=', results.segments[-1].conditions.weights.total_mass[-1,0] 
        print 'takeoff field length=', results.field_length.takeoff
        print 'landing field length=', results.field_length.landing
        post_process(vehicle,mission,results)
        
    else: #include penalty functions if you are not displaying the results
        #add penalty function for takeoff and landing field length
        results.segments[-1].conditions.weights.total_mass[-1,0]+=100.*abs(min(0, 1500-results.field_length.takeoff, 1500-results.field_length.landing))
        #add penalty functions for twist, ensuring that trailing edge is >-5 degrees
        results.segments[-1].conditions.weights.total_mass[-1,0]+=100000.*abs(min(0, alpha_tc+5))
        results.segments[-1].conditions.weights.total_mass[-1,0]+=100000.*abs(max(0, alpha_rc-5))
        #now add penalty function if range is not met
        results.segments[-1].conditions.weights.total_mass[-1,0]+=1000.*abs(min(results.segments[-1].conditions.frames.inertial.position_vector[-1,0]/1000-target_range,0,))
        #add penalty function for washin
        results.segments[-1].conditions.weights.total_mass[-1,0]+=10000.*abs(min(0, alpha_rc-alpha_tc))
    
        #make sure that angle of attack is below 30 degrees but above -30 degrees
        results.segments[-1].conditions.weights.total_mass[-1,0]+=10000.*abs(min(0, 30-max_alpha))+10000.*abs(min(0, 30+min_alpha))
    
        #now add penalty function if wing sweep is too high
        results.segments[-1].conditions.weights.total_mass[-1,0]+=10000.*abs(min(0, 30.-wing_sweep, wing_sweep))
    
        #penalty function in case altitude segments don't match up
        results.segments[-1].conditions.weights.total_mass[-1,0]+=100000*abs(min(climb_alt_5-climb_alt_4, climb_alt_5-climb_alt_3, climb_alt_5-climb_alt_2, climb_alt_5-climb_alt_1,
        climb_alt_4-climb_alt_3, climb_alt_4-climb_alt_2, climb_alt_4-climb_alt_1,
        climb_alt_3-climb_alt_2, climb_alt_2-climb_alt_1, climb_alt_3-climb_alt_1, 0.))
    
        #penalty function in case descent altitude segments don't match up
        results.segments[-1].conditions.weights.total_mass[-1,0]+=100000*abs(min(0., climb_alt_5-desc_alt_1, desc_alt_1-desc_alt_2))
     
        #penalty function to make sure that cruise velocity >=E-190 cruise
        results.segments[-1].conditions.weights.total_mass[-1,0]+=100000*abs(max(0,230.-V_cruise))    
        
    #print vehicle.mass_properties.m_full/(results.segments[-1].vectors.r[-1,0]/1000.),' ', vehicle.mass_properties.m_full, ' ',results.segments[-1].vectors.r[-1,0]/1000. , inputs
    print 'landing mass=', results.segments[-1].conditions.weights.total_mass[-1,0], ' total range=',results.segments[-1].conditions.frames.inertial.position_vector[-1,0] /1000
    
    print 'Ereq=',Ereq_guess, 'Preq=', Preq_guess
    print 'takeoff field length=', results.field_length.takeoff,'landing field length=', results.field_length.landing
    time2=time.time()
    iteration_number+=1
    print 't=', time2-time1, 'seconds'
    print 'iteration number=', iteration_number
    
    #print inputs of each iteration so they can be directly copied
    
    print '[',
    for j in range(len(inputs)):
        print inputs[j],
        if j!=len(inputs)-1:
            print ',',
    print ']'
    
    #print 'total range=', results.segments[-1].conditions.frames.inertial.position_vector[-1,0]/1000, ' km'
    """
    if np.isnan(vehicle.mass_properties.m_full):
        vehicle.mass_properties.m_full=1E50  #put penalty in case nan values appear
    """
    
  
    #print vehicle
    return results.segments[-1].conditions.weights.total_mass[-1,0]/(10.**4.)#/(results.segments[-1].vectors.r[-1,0]/1000.) 

 
    
   
    

# ----------------------------------------------------------------------
#   Build the Vehicle
# ----------------------------------------------------------------------

def define_vehicle(Mguess,Ereq, Preq, max_alt,wing_sweep,alpha_rc, alpha_tc, vehicle_S , V_cruise  ):
    
    # ------------------------------------------------------------------
    #   Initialize the Vehicle
    # ------------------------------------------------------------------    
    
    vehicle = SUAVE.Vehicle()
    vehicle.tag = 'Embraer E190'

    
    # ------------------------------------------------------------------
    #   Vehicle-level Properties
    # ------------------------------------------------------------------    

    
    #vehicle.Nult      = 1.5 * 2.5                       # Ultimate load
    #vehicle.TOW       = Mguess # Maximum takeoff weight in kilograms
    #vehicle.zfw       = Mguess # Maximum zero fuel weight in kilograms
     
    vehicle.envelope.ultimate_load = 3.5
    vehicle.envelope.limit_load    = 1.5
    vehicle.num_eng                                 = 2.                        # Number of engines on the aircraft
    vehicle.passengers                              = 110.                      # Number of passengers
    vehicle.wt_cargo                                = 0.  * Units.kilogram  # Mass of cargo
    vehicle.num_seats = 110.                      # Number of seats on aircraft
    vehicle.systems.control                         = "partially powered"       # Specify fully powered, partially powered or anything else is fully aerodynamic
    vehicle.systems.accessories                     = "medium-range"              # Specify what type of aircraft you have
    vehicle.w2h                                     = 16.     * Units.meters    # Length from the mean aerodynamic center of wing to mean aerodynamic center of the horizontal tail
    vehicle.w2v                                     = 20.     * Units.meters    # Length from the mean aerodynamic center of wing to mean aerodynamic center of the vertical tail
    #vehicle.delta                                    =wing_sweep
    vehicle.reference_area                          = vehicle_S 
   
    
    # mass properties
   
    #vehicle.mass_properties.m_full       = Mguess   # kg
    
    #vehicle.mass_properties.m_empty      = Mguess   # kg
    

    # basic parameters
    #vehicle.delta    = 25.0                     # deg
                  # 
    #vehicle.A_engine = np.pi*(0.9525)**2   
    vehicle.A_engine = 2.85*2
    
    # ------------------------------------------------------------------        
    #   Main Wing
    # ------------------------------------------------------------------        
    
    wing = SUAVE.Components.Wings.Main_Wing()
    wing.tag = 'Main Wing'
   
    wing.areas.reference           = vehicle.reference_area    * Units.meter**2  # Wing gross area in square meters
    wing.aspect_ratio              = 8.3  
    wing.spans.projected           = (wing.aspect_ratio*wing.areas.reference)**.5    * Units.meter     # Span in meters
    wing.taper                     = 0.28                       # Taper ratio
    wing.thickness_to_chord        = 0.105                      # Thickness-to-chord ratio
    wing.sweep                     = wing_sweep     * Units.deg       # sweep angle in degrees
    wing.chords.root               = 5.4     * Units.meter     # Wing exposed root chord length
    wing.chords.mean_aerodynamic   = 12.     * Units.ft    # Length of the mean aerodynamic chord of the wing
    wing.areas_wetted              =wing.areas.reference*2.
    wing.aerodynamic_center        =[wing.chords.mean_aerodynamic/4.,0,0]
    #SUAVE.Geometry.Two_Dimensional.Planform.wing_planform(wing)
    wing.flaps_chord               = 0.28
    wing.areas_exposed             = 0.8*wing.areas.wetted  #
    wing.areas_affected            = 0.6*wing.areas.wetted  #
    wing.eta                       = 1.0                   #
    
    #wing.alpha_tc    = -1.0                   #
    #wing.alpha_rc   =3.0
    wing.flap_type   = 'double_slotted'
    wing.twists.root  =alpha_rc*Units.degrees 
    #wing.alpha_tc   =alpha_tc
    wing.twists.tip  =alpha_tc*Units.degrees 
    wing.vertical    =False
    wing.highlift    = False                 
    
    #wing.hl          = 1                     #
    #wing.flaps_chord = 20                    #
    #wing.flaps_angle = 20                    #
    #wing.slats_angle = 10                    #

    # add to vehicle
    vehicle.append_component(wing)
   
    #compute max CL for takeoff now
    
    # ------------------------------------------------------------------        
    #  Horizontal Stabilizer
    # ------------------------------------------------------------------        
    
    horizontal = SUAVE.Components.Wings.Wing()
    horizontal.tag = 'Horizontal Stabilizer'
    
    horizontal.spans.projected          = 12.08     * Units.meters    # Span of the horizontal tail
    horizontal.sweep                    = wing.sweep      # Sweep of the horizontal tail
    horizontal.chords.mean_aerodynamic  = 2.4      * Units.meters    # Length of the mean aerodynamic chord of the horizontal tail
    horizontal.thickness_to_chord       = 0.11                      # Thickness-to-chord ratio of the horizontal tail
                         # Fraction of horizontal tail area exposed
  
    
   
    horizontal.aspect_ratio         = 5.5         #
    horizontal.symmetric            = True          
    horizontal.thickness_to_chord   = 0.11          #
    horizontal.taper                = 0.11           #
    c_ht                            = 1.   #horizontal tail sizing coefficient
    # size the wing planform
    SUAVE.Geometry.Two_Dimensional.Planform.horizontal_tail_planform_raymer(horizontal,wing,vehicle.w2h,c_ht )
    
    horizontal.chords.mean_aerodynamic = 8.0
    horizontal. areas.wetted          = horizontal.areas.reference*2.0
    horizontal.areas.exposed          = 0.8*horizontal.areas.wetted  #
    horizontal.areas.affected         = 0.6*horizontal.areas.wetted  #  
    #wing.Cl         = 0.2                   #
    horizontal.eta          = 0.9                   #
                     #
    horizontal.twists.root   =2.0*Units.degrees 
    #horizontal.alpha_tc   = 2.0                   #
    horizontal.twists.tip   =2.0*Units.degrees 
    #wing.origin             =[ ]
    horizontal.aerodynamic_center= [horizontal.chords.mean_aerodynamic/4.,0,0]
    horizontal.vertical= False
    # add to vehicle
    vehicle.append_component(horizontal)

    # ------------------------------------------------------------------
    #   Vertical Stabilizer
    # ------------------------------------------------------------------
    vertical = SUAVE.Components.Wings.Wing()
    vertical.tag = 'Vertical Stabilizer'    
    
   
    vertical.aspect_ratio       = 1.7          #
    #wing.span      = 100           #
    vertical.sweep              = wing_sweep * Units.deg  #
    vertical.spans.projected     = 5.3     * Units.meters    # Span of the vertical tail
    #vertical.symmetric = False    
    vertical.thickness_to_chord = 0.12          #
    vertical.taper              = 0.10          #
    c_vt                        =.09
    # size the wing planform
    SUAVE.Geometry.Two_Dimensional.Planform.vertical_tail_planform_raymer(vertical, wing, vehicle.w2v, c_vt)
    
    vertical.chords.mean_aerodynamic  = 11.0                  
    vertical.areas.wetted   = 2.*vertical.areas.reference
    vertical.areas.exposed  = 0.8*vertical.areas.wetted  #
    vertical.areas.affected = 0.6*vertical.areas.wetted  #  
    #wing.Cl        = 0.002                  #
    vertical.eta           = 0.9                   #
    
    vertical.twists.root   =0.
    vertical.twists.tip    =0.
    
    vertical.aerodynamic_center=[vertical.chords.mean_aerodynamic/4.,0,0]
    vertical.t_tail    = False      # Set to "yes" for a T-tail
    
    vertical.vertical  =True
    # add to vehicle
    vehicle.append_component(vertical)
    
    # ------------------------------------------------------------------
    #  Fuselage
    # ------------------------------------------------------------------
    fuselage                           = SUAVE.Components.Fuselages.Fuselage()
    fuselage.tag                       = 'Fuselage'
    
    fuselage.number_coach_seats        = 114.  #
    fuselage.seat_pitch                = 0.7455    # m
    fuselage.seats_abreast             = 4    #
    fuselage.fineness.nose             = 2.0  #
    fuselage.fineness.tail             = 3.0  #
  
    fuselage.lengths.fore_space        = 0.
    fuselage.lengths.aft_space         =0.
    fuselage.width                     = 3.0  #
   
    fuselage.heights.maximum           =3.4
    fuselage.heights.at_quarter_length = fuselage.heights.maximum
    fuselage.heights.at_three_quarters_length = fuselage.heights.maximum
    fuselage.heights.at_wing_root_quarter_chord = fuselage.heights.maximum
    #fuselage.area            = 320.      * Units.meter**2  
    
    # size fuselage planform
    SUAVE.Geometry.Two_Dimensional.Planform.fuselage_planform(fuselage)
    
    # add to vehicle
    vehicle.append_component(fuselage)
 
    ################
    
    # ------------------------------------------------------------------
    #  Propulsion
    # ------------------------------------------------------------------
    
    
    atm = SUAVE.Attributes.Atmospheres.Earth.International_Standard()
    p1, T1, rho1, a1, mew1 = atm.compute_values(0.)
    p2, T2, rho2, a2, mew2 = atm.compute_values(max_alt*Units.km)
  
    
    sizing_segment = SUAVE.Components.Propulsors.Segments.Segment()
    sizing_segment.M   = 230./a2        
    sizing_segment.alt = max_alt
    sizing_segment.T   = T2           
    
    sizing_segment.p   = p2     
    #create battery
    battery = SUAVE.Components.Energy.Storages.Battery_Li_Air()
    #battery_lis = SUAVE.Components.Energy.Storages.Battery()
    #battery_lis.type='Li_S'
    #battery_lis.tag='Battery_Li_S'
    battery.tag = 'Battery'
    battery.type ='Li-Air'
    # attributes
    battery.SpecificEnergy = 2000.0 #W-h/kW
    battery.SpecificPower  = 0.64   #kW/kg    
    
    #ducted fan
    DuctedFan= SUAVE.Components.Propulsors.Ducted_Fan_Bat()
    DuctedFan.propellant = SUAVE.Attributes.Propellants.Aviation_Gasoline()
    DuctedFan.diffuser_pressure_ratio = 0.98
    DuctedFan.fan_pressure_ratio = 1.65
    DuctedFan.fan_nozzle_pressure_ratio = 0.99
    DuctedFan.design_thrust = 2.*Preq/V_cruise #factor of 2 accounts for top of climb
    DuctedFan.number_of_engines=2.0   
    DuctedFan.eta_pe=.95         #electric efficiency of battery
    DuctedFan.engine_sizing_ductedfan(sizing_segment)   #calling the engine sizing method 
                                   
    vehicle.append_component(DuctedFan)
    vehicle.append_component( battery )
    #vehicle.append_component( battery_lis )

    #SUAVE.Methods.Power.size_opt_battery(battery_lis,Ereq_lis, Preq_lis) #create an optimum battery from these requirements
   
    battery.mass_properties.mass=max(Ereq/(battery.SpecificEnergy*3600.), Preq/(battery.SpecificPower*1000.));
    
    battery.MaxPower=battery.mass_properties.mass*(battery.SpecificPower*1000) #find max power available from battery
    battery.TotalEnergy=battery.mass_properties.mass*battery.SpecificEnergy*3600
    battery.CurrentEnergy=battery.TotalEnergy
    
    m_air=battery.find_mass_gain()    #find mass gain of battery throughout mission and size vehicle

    #vehicle.mass_properties.m_empty+=battery.mass_properties.mass-16416.4+3600
    
    #now add the electric motor weight
    #motor_mass=DuctedFan.no_of_engines*SUAVE.Methods.Weights.Correlations.Propulsion.air_cooled_motor((battery.MaxPower+Preq_lis)*Units.watts/DuctedFan.no_of_engines)
    motor_mass=DuctedFan.number_of_engines*SUAVE.Methods.Weights.Correlations.Propulsion.air_cooled_motor((Preq)*Units.watts/DuctedFan.number_of_engines)
    #motor_mass=DuctedFan.no_of_engines*SUAVE.Methods.Weights.Correlations.Propulsion.hts_motor((battery.MaxPower+Preq_lis)*Units.watts/DuctedFan.no_of_engines)
    #engine_mass=SUAVE.Methods.Weights.Correlations.Propulsion.engine_jet(DuctedFan.design_thrust*Units.N)
    propulsion_mass=SUAVE.Methods.Weights.Correlations.Propulsion.integrated_propulsion(motor_mass/DuctedFan.number_of_engines,DuctedFan.number_of_engines)
   
    #propulsion_mass=motor_mass
    DuctedFan.mass_properties.mass=propulsion_mass
    DuctedFan.battery=battery
    #DuctedFan.battery_lis=battery_lis
    fuselage.differential_pressure=max(abs(p2-p1),0)   #assume its pressurized to 2/3 atmospheric pressure
    
    """
    fus_weight=SUAVE.Methods.Weights.Correlations.Tube_Wing.tube(S_fus*(Units.meter**2), 
    diff_p_fus*Units.pascal,fuselage.width*Units.meter,fuselage.height*Units.meter, fuselage.length*Units.meter,
    Nult_fus, Mguess*Units.kg, main_wing.mass_properties.mass*Units.kg, (DuctedFan.mass_properties.mass+motor_mass)*Units.kg, main_wing.root_chord*Units.meter)
  
    fuselage.mass_properties.mass=fus_weight
    vehicle.append_component(fuselage)
    

    #######Other weight correlations##########
    m_landing_gear=SUAVE.Methods.Weights.Correlations.Tube_Wing.landing_gear(Mguess*Units.kg)*1.5 ##factor of 1.5 is for increased landing weight
    systems=SUAVE.Methods.Weights.Correlations.Tube_Wing.systems(fuselage.num_coach_seats, 'fully powered', h_stab.area_wetted*(Units.meter**2), v_stab.area_wetted*(Units.meter**2),
    main_wing.area_wetted*(Units.meter**2), "medium-range")
    m_pl=10454.54545*2.
    m_systems=systems.wt_systems
    """
   
    
    # ------------------------------------------------------------------
    #   Simple Aerodynamics Model
    # ------------------------------------------------------------------ 
    
    aerodynamics = SUAVE.Attributes.Aerodynamics.Fidelity_Zero()
    aerodynamics.initialize(vehicle)
    vehicle.aerodynamics_model = aerodynamics
    
    vehicle.propulsion_model=vehicle.propulsors 

    
    # ------------------------------------------------------------------
    #   Define New Gross Takeoff Weight
    # ------------------------------------------------------------------
    #now add component weights to the gross takeoff weight of the vehicle
    m_fuel=0.
    #m_air=0.              #mass gain from the lithium air battery 
    
    '''
    battery.mass_properties.mass=0
    DuctedFan.mass_properties.mass=0
    m_air=0
    '''
    vehicle.mass_properties.max_takeoff             = Mguess 
    #vehicle.mass_properties.operating_empty         = Mguess-m_ai   
    vehicle.mass_properties.takeoff                 = Mguess-m_air
    vehicle.mass_properties.max_zero_fuel           = Mguess-m_air
    weight =SUAVE.Methods.Weights.Correlations.Tube_Wing.empty_custom_eng(vehicle, DuctedFan)

    vehicle.mass_properties.m_full=weight.empty+battery.mass_properties.mass+weight.payload
    
    """
    vehicle.mass_properties.m_full=fuselage.mass_properties.mass+main_wing.mass_properties.mass+battery.mass_properties.mass+battery_lis.mass_properties.mass+m_landing_gear+ \
    v_stab.mass_properties.mass+h_stab.mass_properties.mass+m_pl+DuctedFan.mass_properties.mass+m_fuel+m_systems+m_air
    """
    #use penalty function to ensure that battery energy is always positive
    #vehicle.mass_properties.m_full+=10000.*abs(min(0, battery_lis.TotalEnergy, battery.TotalEnergy))
    vehicle.mass_properties.m_empty=vehicle.mass_properties.m_full
    vehicle.mass_properties.m_end=vehicle.mass_properties.m_full+m_air
    vehicle.mass_properties.m_takeoff=vehicle.mass_properties.m_full
   
    
    '''
    print 'battery            =', battery.mass_properties.mass
    print 'motor              =', motor_mass
    print 'ducted fan         =', DuctedFan.mass_properties.mass-motor_mass
    print 'propulsion_overall =', weight.propulsion
    print 'passenger          =', weight.payload
    print 'air                =', m_air
    print 'wing               =', weight.wing
    print 'vtail              =', weight.vertical_tail+weight.rudder     
    print 'htail              =', weight.horizontal_tail
    print 'fuselage           =', weight.fuselage[0]
    print 'landing gear       =', weight.landing_gear
    print 'systems            =', weight.systems
    print 'furnishing         =', weight.wt_furnish
    print 'takeoff mass       =', vehicle.mass_properties.m_full[0]
    print 'landing mass       =', vehicle.mass_properties.m_full[0]+m_air
    print 'empty mass         =', weight.empty[0]
    '''
    
    
    ##############################################################################
    # ------------------------------------------------------------------
    #   Define Configurations
    # ------------------------------------------------------------------

    # --- Takeoff Configuration ---
    config = vehicle.new_configuration("takeoff")
    # this configuration is derived from the baseline vehicle

    # --- Cruise Configuration ---
    config = vehicle.new_configuration("cruise")
    # this configuration is derived from vehicle.configs.takeoff

    # --- Takeoff Configuration ---
    takeoff_config = vehicle.configs.takeoff
    takeoff_config.wings['Main Wing'].flaps_angle =  15. * Units.deg
    takeoff_config.wings['Main Wing'].slats_angle  = 25. * Units.deg
    # V2_V2_ratio may be informed by user. If not, use default value (1.2)
    #takeoff_config.V2_VS_ratio = 1.21
    # CLmax for a given configuration may be informed by user. If not, is calculated using correlations
    #takeoff_config.maximum_lift_coefficient = 2.
    #takeoff_config.max_lift_coefficient_factor = 1.0

    # --- Landing Configuration ---
    landing_config = vehicle.new_configuration("landing")
    landing_config.wings['Main Wing'].flaps_angle =  20. * Units.deg
    landing_config.wings['Main Wing'].slats_angle  = 25. * Units.deg
    # Vref_V2_ratio may be informed by user. If not, use default value (1.23)
    #landing_config.Vref_VS_ratio = 1.23
    # CLmax for a given configuration may be informed by user
    #landing_config.maximum_lift_coefficient = 2.
    #landing_config.max_lift_coefficient_factor = 1.0
    landing_config.mass_properties.landing = vehicle.mass_properties.m_end
    
#########################################################################
    
    
    # ------------------------------------------------------------------
    #   Vehicle Definition Complete
    # ------------------------------------------------------------------
    
    return vehicle

###############################################################################################################################################
# ----------------------------------------------------------------------
#   Define the Mission
# ----------------------------------------------------------------------
def define_mission(vehicle,climb_alt_1,climb_alt_2,climb_alt_3, climb_alt_4, climb_alt_5, desc_alt_1, desc_alt_2,Vclimb_1, Vclimb_2, Vclimb_3, Vclimb_4,Vclimb_5,  V_cruise , cruise_range):
   
    # ------------------------------------------------------------------
    #   Initialize the Mission
    # ------------------------------------------------------------------
   
    
    mission = SUAVE.Attributes.Missions.Mission()
    mission.tag = 'The Test Mission'

    # initial mass
    mission.m0 = vehicle.mass_properties.m_full
    
    # atmospheric model
    atmosphere = SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()
    planet = SUAVE.Attributes.Planets.Earth()
    
    #airport
    airport = SUAVE.Attributes.Airports.Airport()
    airport.altitude   =  0.0  * Units.ft
    airport.delta_isa  =  0.0
    airport.atmosphere = SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()
    
    mission.airport = airport
    
    
    # ------------------------------------------------------------------
    #   First Climb Segment: constant Mach, constant segment angle 
    # ------------------------------------------------------------------
    
    segment =  SUAVE.Attributes.Missions.Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "Climb - 1"
    
    # connect vehicle configuration
    segment.config = vehicle.configs.takeoff
    
    # define segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet    
    #segment.altitude   = [0.0, climb_alt_1]   # km
    segment.altitude_start=0.0
    segment.altitude_end  =climb_alt_1* Units.km
    # pick two:
    segment.Vinf       = Vclimb_1        # m/s
    #segment.rate       = 6.0          # m/s
    global wclimb1
    segment.rate       = wclimb1
    
    #segment.psi        = 8.5          # deg
    
    # add to mission
    mission.append_segment(segment)
    
    
    # ------------------------------------------------------------------
    #   Second Climb Segment: constant Speed, constant segment angle 
    # ------------------------------------------------------------------    
   
    segment = SUAVE.Attributes.Missions.Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "Climb - 2"
    
    # connect vehicle configuration
    segment.config = vehicle.configs.cruise
    
    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet    
    #segment.altitude   = [3.0,8.0] # km  
    segment.altitude_end=climb_alt_2* Units.km
    
    # pick two:
    #segment.Vinf       = 190.0       # m/s
    segment.Vinf       =Vclimb_2
    #segment.rate       = 6.0         # m/s
    global wclimb2
    segment.rate        =wclimb2
    #segment.psi        = 15.0        # deg
    
    # add to mission
    mission.append_segment(segment)

    
    # ------------------------------------------------------------------
    #   Third Climb Segment: constant velocity, constant segment angle 
    # ------------------------------------------------------------------    
    
    segment = SUAVE.Attributes.Missions.Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "Climb - 3"

    # connect vehicle configuration
    segment.config = vehicle.configs.cruise
    
    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet   
    #segment.altitude   = [8.0, 10.668] # km    
   
    segment.altitude_end=climb_alt_3* Units.km
    # pick two:
    #segment.Vinf        = 226.0        # m/s   
    segment.Vinf        = Vclimb_3
    #segment.rate        = 3.0          # m/s
    global wclimb3
    segment.rate       =wclimb3
    #segment.psi         = 15.0         # deg
    
    # add to mission
    mission.append_segment(segment)
    
     # ------------------------------------------------------------------
    #   Fourth Climb Segment: constant velocity, constant segment angle 
    # ------------------------------------------------------------------    
    
    segment = SUAVE.Attributes.Missions.Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "Climb - 4"

    # connect vehicle configuration
    segment.config = vehicle.configs.cruise
    
    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet   
    #segment.altitude   = [8.0, 10.668] # km    
   
    segment.altitude_end=climb_alt_4* Units.km
    # pick two:
    #segment.Vinf        = 226.0        # m/s   
    segment.Vinf        = Vclimb_4
    #segment.rate        = 3.0          # m/s
    global wclimb4
    segment.rate       =wclimb4
    #segment.psi         = 15.0         # deg
    
    # add to mission
    mission.append_segment(segment)
    
    
    # ------------------------------------------------------------------
    #   Fifth Climb Segment: Constant Speed, Constant Climb Rate
    # ------------------------------------------------------------------    
    
    segment = SUAVE.Attributes.Missions.Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "Climb - 5"

    # connect vehicle configuration
    segment.config = vehicle.configs.cruise
    
    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet        

    segment.altitude_end=climb_alt_5* Units.km
    
    # pick two:
    segment.Vinf       = Vclimb_5
    #segment.Minf        = 0.78        # m/s   
    #segment.rate        = 1.0         # m/s
    global wclimb5
    segment.rate       =wclimb5
    # add to mission
    mission.append_segment(segment)    
    
    
    
    # ------------------------------------------------------------------    
    #   Cruise Segment: constant speed, constant altitude
    # ------------------------------------------------------------------    
    
    segment = SUAVE.Attributes.Missions.Segments.Cruise.Constant_Speed_Constant_Altitude()
    segment.tag = "Cruise"
    
    # connect vehicle configuration
    segment.config = vehicle.configs.cruise
    
    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet     
    #segment.altitude   = 10.668   
    #segment.altitude   = mission.Segments["Climb - 5"].altitude_end    # km
    segment.air_speed       = V_cruise    # m/s
    segment.distance   =cruise_range*Units.km
    
    #segment.range      = 2400  # km
    mission.append_segment(segment)
    
    # ------------------------------------------------------------------    
    #   First Descent Segment: constant speed, constant segment rate
    # ------------------------------------------------------------------    

    segment = SUAVE.Attributes.Missions.Segments.Descent.Constant_Speed_Constant_Rate()
    segment.tag = "Descent - 1"
    
    # connect vehicle configuration
    segment.config = vehicle.configs.cruise
    
    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet    
    #segment.altitude   = [10.668, 5.0]  # km
    segment.altitude_end   =  desc_alt_1  * Units.km
    global Vdesc1
    segment.Vinf       = Vdesc1          # m/s
    #segment.rate       = 5.0            # m/s
    global wdesc1
    segment.rate         =wdesc1
    
    # add to mission
    mission.append_segment(segment)
    

    # ------------------------------------------------------------------    
    #   Second Descent Segment: constant speed, constant segment rate
    # ------------------------------------------------------------------    

    segment = SUAVE.Attributes.Missions.Segments.Descent.Constant_Speed_Constant_Rate()
    segment.tag = "Descent - 2"

    # connect vehicle configuration
    segment.config = vehicle.configs.cruise

    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet   
    segment.altitude_end   =  desc_alt_2 * Units.km # km
    #segment.altitude   = [5., 0.0]
    global Vdesc2
    segment.Vinf       = Vdesc2      # m/s
    #segment.rate       = 5.0         # m/s
    global wdesc2
    segment.rate         =wdesc2
    # append to mission
    mission.append_segment(segment)

       # ------------------------------------------------------------------    
    #   Third Descent Segment: constant speed, constant segment rate
    # ------------------------------------------------------------------    

    segment = SUAVE.Attributes.Missions.Segments.Descent.Constant_Speed_Constant_Rate()
    segment.tag = "Descent -3"

    # connect vehicle configuration
    segment.config = vehicle.configs.cruise
    
    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet   
    segment.altitude_end   =  0.  # km
    global Vdesc3
    segment.Vinf       = Vdesc3      # m/s
    #segment.rate       = 5.0         # m/s
    global wdesc3
    segment.rate         =wdesc3
    # append to mission
    mission.append_segment(segment)
    
    # ------------------------------------------------------------------    
    #   Mission definition complete   
    
    #vehicle.mass_properties.m_empty+=motor_mass

    #print vehicle.mass_properties.m_full
    
    return mission

#: def define_mission()


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
    
    SUAVE.Methods.Results.compute_energies(results,summary=False)
    #SUAVE.Methods.Results.compute_efficiencies(results)
    #SUAVE.Methods.Results.compute_velocity_increments(results)
    #SUAVE.Methods.Results.compute_alpha(results)    
    
    battery = vehicle.energy.Storages['Battery']
   
    #battery_lis = vehicle.Energy.Storages['Battery_Li_S']
    Pbat_loss=np.zeros_like(results.segments[0].P_e)   #initialize battery losses
   
    #results.segments[0].t=results.segments[0].conditions.frames.inertial.time[:,0]
    
    #Ecurrent=np.zeros_like( results.segments[0].t)      #initialize battery energies
    #Ecurrent_lis=np.zeros_like(results.segments[0].conditions.frames.inertial.time[:,0])
   
    Pmax=0.
    Ecurrent_min=battery.TotalEnergy
    #now run the batteries for the mission
    j=0
    
    for i in range(len(results.segments)):
        results.segments[i].t=results.segments[i].conditions.frames.inertial.time[:,0]
       
        results.segments[i].Ecurrent=np.zeros_like(results.segments[i].t)
        results.segments[i].mdot=np.zeros_like(results.segments[i].t)
        #results.segments[i].Ecurrent_lis=np.zeros_like(results.segments[i].t)
        if i==0:
        
            results.segments[i].Ecurrent[0]=battery.TotalEnergy
            
            #results.segments[i].Ecurrent_lis[0]=battery_lis.TotalEnergy
        if i!=0 and j!=0:
            results.segments[i].Ecurrent[0]=battery.CurrentEnergy #assign energy at end of segment to next segment 
            #results.segments[i].Ecurrent_lis[0]=battery_lis.CurrentEnergy #assign energy at end of segment to next segment 
        for j in range(len(results.segments[i].P_e)):
           # print battery.CurrentEnergy/battery.TotalEnergy
            if Pmax<results.segments[i].P_e[j]:
                Pmax=results.segments[i].P_e[j]
            #if battery.MaxPower>=results.segments[i].P_e[j]:
                #Ploss_lis=0
            if j!=0:
                [Ploss,mdot]=battery(results.segments[i].P_e[j], (results.segments[i].t[j]-results.segments[i].t[j-1]))
                    
            elif i!=0 and j==0:
                [Ploss,mdot]=battery(results.segments[i].P_e[j], -(results.segments[i-1].t[-2]-results.segments[i-1].t[-1]))
                #print results.segments[i].t[j], results.segments[i-1].t[-1], results.segments[i-1].t[-2]
            elif j==0 and i==0: 
                
                [Ploss,mdot]=battery(results.segments[i].P_e[j], (results.segments[i].t[j+1]-results.segments[i].t[j]))
                
            """
            else: #Li-air battery cannot meet total power requirements
                if j!=0:
                     [Ploss,mdot]=battery(battery.MaxPower, (results.segments[i].t[j]-results.segments[i].t[j-1]))
                     #Ploss_lis=battery_lis(results.segments[i].P_e[j]-battery.MaxPower, (results.segments[i].t[j]-results.segments[i].t[j-1]))
                     
                elif i!=0 and j==0:
                    [Ploss,mdot]=battery(battery.MaxPower, (results.segments[i].t[j]-results.segments[i-1].t[-1]))
                    #Ploss_lis=battery_lis(battery.MaxPower-results.segments[i].P_e[j], (results.segments[i].t[j]-results.segments[i-1].t[-1]))
                    
                elif j==0 and i==0: 
                    
                    [Ploss,mdot]=battery(battery.MaxPower, (results.segments[i].t[j+1]-results.segments[i].t[j]))
                    #Ploss_lis=battery_lis(battery.MaxPower-results.segments[i].P_e[j], (results.segments[i].t[j+1]-results.segments[i].t[j]))
                    
                if results.segments[i].P_e[j]>battery.MaxPower+battery_lis.MaxPower:
                    penalty_power=results.segments[i].P_e[j]
            """     
           
            results.segments[i].mdot[j]=mdot
            results.segments[i].Ecurrent[j]=battery.CurrentEnergy
            if results.segments[i].Ecurrent[j]<Ecurrent_min:
                Ecurrent_min=results.segments[i].Ecurrent[j]
            #results.segments[i].Ecurrent_lis[j]=battery_lis.CurrentEnergy
            results.segments[i].P_e[j]+=Ploss #+Ploss_lis
    
    results.Etotal=results.segments[0].Ecurrent[0]-Ecurrent_min  #find the total energy required to run the mission
   
    results.Pmax= Pmax
    '''
    print "Etotal=", results.Etotal
    print "Pmax=", Pmax
    print "Ecurrent_min=", Ecurrent_min
    '''
    #add lithium air battery mass gain to weight of the vehicle
   
    #vehicle.mass_properties.m_full+=m_li_air
    
    return results
#########################################################################################################################
def evaluate_field_length(vehicle,mission,results):
    
    # unpack
    airport = mission.airport
    
    takeoff_config = vehicle.configs.takeoff
    landing_config = vehicle.configs.landing
    
     
    
    # evaluate
    TOFL = estimate_take_off_field_length(vehicle,takeoff_config,airport)
    LFL = estimate_landing_field_length(vehicle,landing_config,airport)
    
    # pack
    field_length = SUAVE.Structure.Data()
    field_length.takeoff = TOFL[0]
    field_length.landing = LFL[0]
    
    results.field_length = field_length
 
    
    return results
#########################################################################################################################
# ----------------------------------------------------------------------
#   Plot Results
# ----------------------------------------------------------------------
def post_process(vehicle,mission,results):
    battery = vehicle.energy.Storages['Battery']
    #battery_lis = vehicle.Energy.Storages['Battery_Li_S']
    # ------------------------------------------------------------------    
    #   Thrust Angle
    # ------------------------------------------------------------------
    '''
    title = "Thrust Angle History"
    plt.figure(0)
    for i in range(len(results.segments)):
        plt.plot(results.segments[i].t/60,np.degrees(results.segments[i].gamma),'bo-')
    plt.xlabel('Time (mins)'); plt.ylabel('Thrust Angle (deg)'); plt.title(title)
    plt.grid(True)
    '''
    # ------------------------------------------------------------------    
    #   Throttle
    # ------------------------------------------------------------------
    plt.figure("Throttle History")
    axes = plt.gca()
    for i in range(len(results.segments)):
        time = results.segments[i].conditions.frames.inertial.time[:,0] / Units.min
        eta  = results.segments[i].conditions.propulsion.throttle[:,0]
        axes.plot(time, eta, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Throttle')
    axes.grid(True)

    # ------------------------------------------------------------------    
    #   Angle of Attack
    # ------------------------------------------------------------------
    plt.figure("Angle of Attack History")
    axes = plt.gca()    
    for i in range(len(results.segments)):     
        time = results.segments[i].conditions.frames.inertial.time[:,0] / Units.min
        aoa = results.segments[i].conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        axes.plot(time, aoa, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Angle of Attack (deg)')
    axes.grid(True)        
    
    # ------------------------------------------------------------------    
    #   Vehicle Mass
    # ------------------------------------------------------------------
    plt.figure("Vehicle Mass")
    axes = plt.gca()
    for i in range(len(results.segments)):
        time = results.segments[i].conditions.frames.inertial.time[:,0] / Units.min
        mass = results.segments[i].conditions.weights.total_mass[:,0]
        axes.plot(time, mass, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Vehicle Mass (kg)')
    axes.grid(True)
    
    
    
    # ------------------------------------------------------------------    
    #   Mass Gain Rate
    # ------------------------------------------------------------------
    plt.figure("Mass Accumulation Rate")
    axes = plt.gca()    
    for i in range(len(results.segments)):     
        time = results.segments[i].conditions.frames.inertial.time[:,0] / Units.min
        mdot = results.segments[i].conditions.propulsion.fuel_mass_rate[:,0]
        axes.plot(time, mdot, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Mass Accumulation Rate(kg/s)')
    axes.grid(True)    
    
    
 

    
    
    # ------------------------------------------------------------------    
    #   Altitude
    # ------------------------------------------------------------------
    plt.figure("Altitude")
    axes = plt.gca()    
    for i in range(len(results.segments)):     
        time     = results.segments[i].conditions.frames.inertial.time[:,0] / Units.min
        altitude = results.segments[i].conditions.freestream.altitude[:,0] /Units.km
        axes.plot(time, altitude, 'bo-')
    axes.set_xlabel('Time (mins)')
    axes.set_ylabel('Altitude (km)')
    axes.grid(True)
    
    
    # ------------------------------------------------------------------    
    #   Horizontal Distance
    # ------------------------------------------------------------------
    '''
    title = "Ground Distance"
    plt.figure(title)
    for i in range(len(results.segments)):
        plt.plot(results.segments[i].t/60,results.segments[i].conditions.frames.inertial.position_vector[:,0])
    plt.xlabel('Time (mins)'); plt.ylabel('ground distance(km)'); plt.title(title)
    plt.grid(True)
    '''
    
    # ------------------------------------------------------------------    
    #   Energy
    # ------------------------------------------------------------------
    
    title = "Energy and Power"
    fig=plt.figure(title)
    #print results.segments[0].Ecurrent[0]
    for segment in results.segments:
        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        axes = fig.add_subplot(2,1,1)
        axes.plot(time, segment.Ecurrent/battery.TotalEnergy,'bo-')
        axes.set_xlabel('Time (mins)')
        axes.set_ylabel('State of Charge of the Battery')
        axes.grid(True)
        axes = fig.add_subplot(2,1,2)
        axes.plot(time, segment.P_e,'bo-')
        axes.set_xlabel('Time (mins)')
        axes.set_ylabel('Electric Power (Watts)')
        axes.grid(True)
    """
    for i in range(len(results.segments)):
        plt.plot(results.segments[i].t/60, results.segments[i].Ecurrent_lis/battery_lis.TotalEnergy,'ko-')
      
        #results.segments[i].Ecurrent_lis/battery_lis.TotalEnergy
    """
    # ------------------------------------------------------------------    
    #   Aerodynamics
    # ------------------------------------------------------------------
    fig = plt.figure("Aerodynamic Forces")
    for segment in results.segments.values():
        
        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        Lift   = -segment.conditions.frames.wind.lift_force_vector[:,2]
        Drag   = -segment.conditions.frames.wind.drag_force_vector[:,0]
        Thrust = segment.conditions.frames.body.thrust_force_vector[:,0]

        axes = fig.add_subplot(3,1,1)
        axes.plot( time , Lift , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('Lift (N)')
        axes.grid(True)
        
        axes = fig.add_subplot(3,1,2)
        axes.plot( time , Drag , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('Drag (N)')
        axes.grid(True)
        
        axes = fig.add_subplot(3,1,3)
        axes.plot( time , Thrust , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('Thrust (N)')
        axes.grid(True)
        
    # ------------------------------------------------------------------    
    #   Aerodynamics 2
    # ------------------------------------------------------------------
    fig = plt.figure("Aerodynamic Coefficients")
    for segment in results.segments.values():
        
        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        CLift  = segment.conditions.aerodynamics.lift_coefficient[:,0]
        CDrag  = segment.conditions.aerodynamics.drag_coefficient[:,0]
        Drag   = -segment.conditions.frames.wind.drag_force_vector[:,0]
        Thrust = segment.conditions.frames.body.thrust_force_vector[:,0]

        axes = fig.add_subplot(4,1,1)
        axes.plot( time , CLift , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('CL')
        axes.grid(True)
        
        axes = fig.add_subplot(4,1,2)
        axes.plot( time , CDrag , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('CD')
        axes.grid(True)
        
        axes = fig.add_subplot(4,1,3)
        axes.plot( time , Drag   , 'bo-' )
        axes.plot( time , Thrust , 'ro-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('Drag and Thrust (N)')
        axes.grid(True)
        
        axes = fig.add_subplot(4,1,4)
        axes.plot( time , CLift/CDrag , 'bo-' )
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('CL/CD')
        axes.grid(True)
    plt.show()
    raw_input('Press Enter To Quit')
    return     
   
  
  
if __name__ == '__main__':
    main()
