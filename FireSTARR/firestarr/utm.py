"""
Provide UTM coordinate translations
Original Javascript by Chuck Taylor
Port to C++ by Alex Hajnal

This is a simple port of the code on the Geographic/UTM Coordinate Converter (1) page
from Javascript to C++.
Using this you can easily convert between UTM and WGS84 (latitude and longitude).
Accuracy seems to be around 50cm (I suspect rounding errors are limiting precision).
This code is provided as-is and has been minimally tested; enjoy but use at your own
risk!
The license for UTM.cpp and UTM.h is the same as the original Javascript:
"The C++ source code in UTM.cpp and UTM.h may be copied and reused without
restriction."

1) http://home.hiwaay.net/~taylorc/toolbox/geography/geoutm.html
"""
import math

## Ellipsoid model major axis (WGS84)
SM_A = 6378137.0
## Ellipsoid model minor axis (WGS84)
SM_B = 6356752.314
## UTM scale factor (WGS84)
UTM_SCALE_FACTOR = 0.9996

def to_radians(deg):
    """!
    Convert degrees to radians
    @param deg Value (degrees)
    @return Value (radians)
    """
    return deg / 180.0 * math.pi

def to_degrees(rad):
    """!
    Convert radians to degrees
    @param rad Value (radians)
    @return Value (degrees)
    """
    return rad / math.pi * 180.0

def arc_length_of_meridian(phi):
    """!
    Computes the ellipsoidal distance from the equator to a point at a given latitude.
    
    Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    
    @param phi Latitude of the point, in radians.
    @return The ellipsoidal distance of the point from the equator, in meters.
    """
    n = (SM_A - SM_B) / (SM_A + SM_B)
    alpha = ((SM_A + SM_B) / 2.0) * (1.0 + (math.pow(n, 2) / 4.0) + (math.pow(n, 4) / 64.0))
    beta = (-3.0 * n / 2.0) + (9.0 * math.pow(n, 3) / 16.0) + (-3.0 * math.pow(n, 5) / 32.0)
    gamma = (15.0 * math.pow(n, 2) / 16.0) + (-15.0 * math.pow(n, 4) / 32.0)
    delta = (-35.0 * math.pow(n, 3) / 48.0) + (105.0 * math.pow(n, 5) / 256.0)
    epsilon = (315.0 * math.pow(n, 4) / 512.0)
    # Now calculate the sum of the series and return
    return (alpha * (phi + (beta * math.sin(2.0 * phi))
            + (gamma * math.sin(4.0 * phi))
            + (delta * math.sin(6.0 * phi))
            + (epsilon * math.sin(8.0 * phi))))

def utm_central_meridian_deg(zone):
    """!
    @brief Determines the central meridian for the given UTM zone.

    Range of the central meridian is the radian equivalent of [-177,+177].

    @param zone A value designating the UTM zone, range [1,60].
    @return The central meridian for the given UTM zone, in degrees
    """
    return -183.0 + (zone * 6.0)

def utm_central_meridian(zone):
    """!
    @brief Determines the central meridian for the given UTM zone.

    Range of the central meridian is the radian equivalent of [-177,+177].

    @param zone A value designating the UTM zone, range [1,60].
    @return The central meridian for the given UTM zone, in radians
    """
    return to_radians(utm_central_meridian_deg(zone))

def footpoint_latitude(y):
    """!
    Computes the footpoint latitude for use in converting transverse Mercator coordinates to ellipsoidal coordinates.
    
    Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    
    @param y The UTM northing coordinate, in meters.
    @return The footpoint latitude, in radians.
    """
    # Precalculate n (Eq. 10.18)
    n = (SM_A - SM_B) / (SM_A + SM_B)
    # Precalculate alpha_ (Eq. 10.22)
    # (Same as alpha in Eq. 10.17)
    alpha = ((SM_A + SM_B) / 2.0) * (1 + (math.pow(n, 2) / 4) + (math.pow(n, 4) / 64))
    # Precalculate row_ (Eq. 10.23)
    y_alpha = y / alpha
    # Precalculate beta_ (Eq. 10.22)
    beta = (3.0 * n / 2.0) + (-27.0 * math.pow(n, 3) / 32.0) + (269.0 * math.pow(n, 5) / 512.0)
    # Precalculate gamma_ (Eq. 10.22)
    gamma = (21.0 * math.pow(n, 2) / 16.0) + (-55.0 * math.pow(n, 4) / 32.0)
    # Precalculate delta_ (Eq. 10.22)
    delta = (151.0 * math.pow(n, 3) / 96.0) + (-417.0 * math.pow(n, 5) / 128.0)
    # Precalculate epsilon_ (Eq. 10.22)
    epsilon = (1097.0 * math.pow(n, 4) / 512.0)
    # Now calculate the sum of the series (Eq. 10.21)
    return (y_alpha + (beta * math.sin(2.0 * y_alpha))
        + (gamma * math.sin(4.0 * y_alpha))
        + (delta * math.sin(6.0 * y_alpha))
        + (epsilon * math.sin(8.0 * y_alpha)))

def utm_central_meridian(zone):
    return to_radians(utm_central_meridian_deg(zone))

def map_lat_lon_to_xy(phi, lambda1, lambda0):
    """!
    Converts a latitude/longitude pair to Transverse Mercator x and y coordinates
    
    Converts a latitude/longitude pair to x and y coordinates in the
    Transverse Mercator projection.  Note that Transverse Mercator is not
    the same as UTM; a scale factor is required to convert between them.
    
    Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    
    @param phi Latitude of the point, in radians.
    @param lambda1 Longitude of the point, in radians.
    @param lambda0 Longitude of the central meridian to be used, in radians.
    @return The x coordinate of the computed point.
    @return The y coordinate of the computed point.
    """
    ep2 = (math.pow(SM_A, 2) - math.pow(SM_B, 2)) / math.pow(SM_B, 2)
    c = math.cos(phi)
    nu2 = ep2 * math.pow(c, 2)
    n = math.pow(SM_A, 2) / (SM_B * math.sqrt(1 + nu2))
    t = math.tan(phi)
    t2 = t * t
    l = lambda1 - lambda0
    """Precalculate coefficients for l**n in the equations below
     so a normal human being can read the expressions for easting and northing
     -- l**1 and l**2 have coefficients of 1.0"""
    l3_coefficient = 1.0 - t2 + nu2
    l4_coefficient = 5.0 - t2 + 9 * nu2 + 4.0 * (nu2 * nu2)
    l5_coefficient = 5.0 - 18.0 * t2 + (t2 * t2) + 14.0 * nu2 - 58.0 * t2 * nu2
    l6_coefficient = 61.0 - 58.0 * t2 + (t2 * t2) + 270.0 * nu2 - 330.0 * t2 * nu2
    l7_coefficient = 61.0 - 479.0 * t2 + 179.0 * (t2 * t2) - (t2 * t2 * t2)
    l8_coefficient = 1385.0 - 3111.0 * t2 + 543.0 * (t2 * t2) - (t2 * t2 * t2)

    # Calculate easting (x)
    x = (n * c * l
        + (n / 6.0 * math.pow(c, 3) * l3_coefficient * math.pow(l, 3))
        + (n / 120.0 * math.pow(c, 5) * l5_coefficient * math.pow(l, 5))
        + (n / 5040.0 * math.pow(c, 7) * l7_coefficient * math.pow(l, 7)))

    # Calculate northing (y)
    y = (arc_length_of_meridian(phi)
        + (t / 2.0 * n * math.pow(c, 2) * math.pow(l, 2))
        + (t / 24.0 * n * math.pow(c, 4) * l4_coefficient * math.pow(l, 4))
        + (t / 720.0 * n * math.pow(c, 6) * l6_coefficient * math.pow(l, 6))
        + (t / 40320.0 * n * math.pow(c, 8) * l8_coefficient * math.pow(l, 8)))
    return x, y

def map_xy_to_lat_lon(x, y, lambda0):
    """!
    @brief Converts Transverse Mercator to latitude/longitude
    
    Converts x and y coordinates in the Transverse Mercator projection to
    a latitude/longitude pair.  Note that Transverse Mercator is not
    the same as UTM; a scale factor is required to convert between them.
    
    Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    
    @param x The easting of the point, in meters.
    @param y The northing of the point, in meters.
    @param lambda0 Longitude of the central meridian to be used, in radians.
    @return Latitude in radians.
    @return Longitude in radians.
    """
    # Get the value of phi_f, the footpoint latitude.
    phi_f = footpoint_latitude(y)
    ep2 = (math.pow(SM_A, 2) - math.pow(SM_B, 2)) / math.pow(SM_B, 2)
    cf = math.cos(phi_f)
    nuf2 = ep2 * math.pow(cf, 2)
    # Precalculate Nf and initialize nf_power
    nf = math.pow(SM_A, 2) / (SM_B * math.sqrt(1 + nuf2))
    nf_power = nf
    tf = math.tan(phi_f)
    tf2 = tf * tf
    tf4 = tf2 * tf2
    # Precalculate fractional coefficients for x**n in the equations
    # below to simplify the expressions for latitude and longitude.
    x1_fraction = 1.0 / (nf_power * cf)
    nf_power *= nf # now equals Nf**2)
    x2_fraction = tf / (2.0 * nf_power)
    nf_power *= nf # now equals Nf**3)
    x3_fraction = 1.0 / (6.0 * nf_power * cf)
    nf_power *= nf # now equals Nf**4)
    x4_fraction = tf / (24.0 * nf_power)
    nf_power *= nf # now equals Nf**5)
    x5_fraction = 1.0 / (120.0 * nf_power * cf)
    nf_power *= nf # now equals Nf**6)
    x6_fraction = tf / (720.0 * nf_power)
    nf_power *= nf # now equals Nf**7)
    x7_fraction = 1.0 / (5040.0 * nf_power * cf)
    nf_power *= nf # now equals Nf**8)
    x8_fraction = tf / (40320.0 * nf_power)
    # Precalculate polynomial coefficients for x**n. 
    # -- x**1 does not have a polynomial coefficient.
    x2_polynomial = -1.0 - nuf2
    x3_polynomial = -1.0 - 2 * tf2 - nuf2
    x4_polynomial = (5.0 + 3.0 * tf2 + 6.0 * nuf2 - 6.0 * tf2 * nuf2 - 3.0 * (nuf2 * nuf2)
                        - 9.0 * tf2 * (nuf2 * nuf2))
    x5_polynomial = 5.0 + 28.0 * tf2 + 24.0 * tf4 + 6.0 * nuf2 + 8.0 * tf2 * nuf2
    x6_polynomial = -61.0 - 90.0 * tf2 - 45.0 * tf4 - 107.0 * nuf2 + 162.0 * tf2 * nuf2
    x7_polynomial = -61.0 - 662.0 * tf2 - 1320.0 * tf4 - 720.0 * (tf4 * tf2)
    x8_polynomial = 1385.0 + 3633.0 * tf2 + 4095.0 * tf4 + 1575 * (tf4 * tf2)
    # Calculate latitude
    phi = (phi_f + x2_fraction * x2_polynomial * (x * x)
            + x4_fraction * x4_polynomial * math.pow(x, 4)
            + x6_fraction * x6_polynomial * math.pow(x, 6)
            + x8_fraction * x8_polynomial * math.pow(x, 8))
    # Calculate longitude
    lambda1 = (lambda0 + x1_fraction * x
            + x3_fraction * x3_polynomial * math.pow(x, 3)
            + x5_fraction * x5_polynomial * math.pow(x, 5)
            + x7_fraction * x7_polynomial * math.pow(x, 7))
    return phi, lambda1

def lat_lon_to_utm(latitude, longitude):
    """!
    Converts a latitude/longitude pair to x and y coordinates in the UTM projection.
    @param latitude Latitude to convert
    @param longitude Longitude to convert
    @return The UTM zone used for calculating the values of x and y.
    @return x The x coordinate (easting) of the computed point. (in meters)
    @return y The y coordinate (northing) of the computed point. (in meters)
    """
    zone = int(((longitude + 180.0) / 6) + 1)
    x, y = map_lat_lon_to_xy(to_radians(latitude),
                    to_radians(longitude),
                    utm_central_meridian(zone))

    # Adjust easting and northing for UTM system.
    x = x * UTM_SCALE_FACTOR + 500000.0
    y = y * UTM_SCALE_FACTOR
    if y < 0.0:
        y += 10000000.0
    return zone, x, y

def utm_to_lat_lon(x, y, zone, is_southern_hemisphere):
    """!
    Convert UTM to latitude/longitude.
    
    Converts x and y coordinates in the Universal Transverse Mercator
    projection to a latitude/longitude pair.
    
    The UTM zone parameter should be in the range [1,60].
    
    @param x The easting of the point, in meters.
    @param y The northing of the point, in meters.
    @param zone The UTM zone in which the point lies.
    @param is_southern_hemisphere True if the point is in the southern hemisphere; false otherwise.
    @return lat The latitude of the point, in degrees.
    @return lon The longitude of the point, in degrees.
    """
    x -= 500000.0
    x /= UTM_SCALE_FACTOR
    # If in southern hemisphere, adjust y accordingly.
    if (is_southern_hemisphere):
        y -= 10000000.0
    y /= UTM_SCALE_FACTOR
    central_meridian = utm_central_meridian(zone)
    lat, lon = map_xy_to_lat_lon(x, y, central_meridian)
    return to_degrees(lat), to_degrees(lon)
