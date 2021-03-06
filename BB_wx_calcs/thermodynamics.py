import numpy as np

"""
Thermodynamic equations
"""

def c_to_K(c):
    """
    Converts Celsius to Kelvin temperature
    """
    return c+273.15

def TempPress_to_PotTemp(temp,press):
    """
    Converts a temperature and pressure to potential temperature
    Uses Poisson's Equation 
    (Wallace and Hobbs equation 3.54 on pg. 78)
                  
                  theta = T(p0/p)^(R/cp)
    
    Input:
        temperature in Celsius
        pressure in hPa (mb)
    Output:
        potential temperature (aka theta)
    """
    
    R = 287.   # J K-1 kg-1
    cp = 1004. # J K-1 kg-1
    p0 = 1000. # hPa
    
    theta = c_to_K(temp)*(p0/press)**(R/cp)
    
    return theta
    
def DwptPress_to_MixRatio(Tdew,press):
    """
    Converts a Temperature, Pressure, and DewPoint to a Mixing Ratio
    From: http://www.srh.noaa.gov/images/epz/wxcalc/vaporPressure.pdf
      and http://www.srh.noaa.gov/images/epz/wxcalc/mixingRatio.pdf
    
                 w = 621.97 * (e/(press-e))   
                     from  Walace and Hobbs 3.59 
                     with some algebra to solve for w. 
                     epsilon = 0.622. w is in g/kg (not kg/kg)
                 
                 e = 6.11 * 10 ^ (7.5 * Tdew/(237.3+Tdew))
    input:
        dewpoint: Dewpoint Temperature in Celsius
        pressure: hPa
    output:
        actual mixing ratio in g kg -1
    """    
    e = 6.11 * 10 **(7.5 * Tdew/(237.3+Tdew))  # Alternatively e = 6.112 * exp((17.67 * Tdew) / ( Tdew + 243.5 ))
    w = 621.97 * (e/(press-e))

    return w   
    
    
def rh_to_mr_wat( rh, p, t) :
  '''
  Returns mixing ratio over water, in g/kg, given relative humidity in %, 
  pressure in hPa and temperature in K.
  '''
  return rh * 0.01 * satmixwat(p, t)
  
def satmixwat( p,  t) :
  '''
  Returns saturation mixing ratio over water, in g/kg, given pressure in hPa and
  temperature in K.
  '''
  es = svpwat(t)
  return (622. * es)/p
  
def svpwat(t) :
    '''
    Returns saturation vapor pressure over water, in hPa, given temperature in K.
    '''

    a0 = 0.999996876e0
    a1 = -0.9082695004e-2
    a2 = 0.7873616869e-4
    a3 = -0.6111795727e-6
    a4 = 0.4388418740e-8
    a5 = -0.2988388486e-10
    a6 = 0.2187442495e-12
    a7 = -0.1789232111e-14
    a8 = 0.1111201803e-16
    a9 = -0.3099457145e-19
    b = 0.61078e+1
    t -= 273.16

    return (b / ((a0+t*(a1+t*(a2+t*(a3+t*(a4+t*(a5+t*(a6+t*(a7+t*(a8+t*a9)))))))))**8.))

def WBT(pres, tht):
    """
    Parcel temperature if lifted above the lcl
    (aka, the wet bulb temperature, following moist adiabtic lapse rate)
    """
    #parcel temp if above lcl
    val = 0
    if tht > 270:
        val = tht - 270.
    tg = (tht - .5 * (val)**1.05) * (pres/1000.) ** .2
    #*      Set convergence and initial guess in degrees C.
    epsi = .001
    tgnu = tht - 273.15
    #*      Set a limit of 100 iterations.  Compute TENU, TENUP, the
    #C*      THTE's at, one degree above the guess temperature.
    #       Do Newton iteration.
    iterN = 0
    convrg = 0
    while (iterN < 100) and (convrg != 1):
        iterN += 1
        tgnup = tgnu + 1.
        tenu = THTE(pres, tgnu, tgnu)
        tenup = THTE(pres, tgnup, tgnup)
        #C*        Compute the correction, DELTG; return on convergence.
        denom = tenup - tenu
        if denom > 0:
            cor = (tht - tenu)/(tenup - tenu)
            tgnu = tgnu + cor
            if np.abs(cor) < epsi:
                convrg = 1

    if convrg != 1:
        wbt = np.nan
    else:
        wbt = tgnu + 273.15
        #	 printf "$pres $tht $tg $tgnu $iterN $wbpt\n";
        #       print "convrg $convrg wbpt $wbpt\n";

    return wbt

def THTE(p, t, td):
    """
    Compute equivelent potential temperature
    Input:   
        pressure in [hPa]
        temperature in [C]
        dew point in [C]
    Output:
        THTE (equivalent potential temperature)
    """
    vapr = 6.112 * np.exp((17.67*td)/(td + 243.5))
    corr = (1.001 + ((p - 100.)/900.)*.0034)
    e = corr * vapr
    mixr = .62197*(e/(p - e))*1000.
    # temp of lcl from gempak sub
    #   printf " $p $t $td $mixr\n";
    TLCL = (800. * (td + 273.15 - 56.)/(800. + (td + 273.15 - 56.) * \
           np.log((t + 273.15)/(td + 273.15)))) + 56.

    E = (287/1004)*(1. - (.28*.001*mixr))
    thtm = (273.15 + t)*(1000/p)**E
    e = ((3.376/TLCL) - .00254) * (mixr * (1. + .81*.001*mixr))
    THTE = thtm*np.exp(e)

    return THTE

"""
    # Need to make a few calculations for additional data (THIS IS NOT FINISHED!!!)
#----------------------------------------------------------------------
# Convert geopotential to pressure
# p2 = p1*exp(-(Z2-Z1)/H) where H=RTa/g0


#Convert Potential Temperature (K) to Temperature (C)
# theta = T*(p0/p)^(R/cp)

# Convert mixing ratio to dewpoint temperature
"""