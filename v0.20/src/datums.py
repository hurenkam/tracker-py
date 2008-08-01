#
# datums.py - v0.1 - GPS Datum conversions and calcultations
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#
# Parts of this software (GetWgs84FromRd) were taken from a Javascript
# by Ed Stevenhagen, and are copied with his permission provided authors
# are retained and the following statement included:
#
# 1. Transformation of rectangular TD-co-ordinates into geographical
# co-ordinates on the Bessel ellipsoid
# (Dutch stereographic projection) by  ir. T.G. Schut (NGT Geodesia
# 1992-6).
# 2. Implementation in Javascript by Stevenhagen <at> xs4all.nl
#
#
# The UTM<->WGS84 calculations here are ported from javascript code
# by Charles L. Taylor, wha has the following banner upon his webpage
# ( http://home.hiwaay.net/~taylorc/toolbox/geography/geoutm.html )
# regarding his code:
#
#    Programmers: The JavaScript source code in this document may be
#    copied and reused without restriction.
#


# Author(s):
#
#    Ed Stevenhagen	Stevenhagen <at> xs4all.nl
#       Original Javascript version for RD to WGS84 calculation
#
#    Charles L. Taylor
#       Original Javascript version for UTM<->WGS84 calculations
#
#    Nick Burch
#       Distance and Bearing calculations (from geo_helper.py)
#
#    Mark Hurenkamp	Mark.Hurenkamp <at> xs4all.nl
#	    Port to python

import math

# RD to WGS84 Calculation

def GetWgs84FromRd(x,y):
    x0 = 155000.0
    y0 = 463000.0

    f0 = 52.15610556
    l0 = 5.387638889

    a01 = 3236.0331637
    b10 = 5261.3028966
    a20 =  -32.5915821
    b11 =  105.9780241
    a02 =   -0.2472814
    b12 =    2.4576469
    a21 =   -0.8501341
    b30 =   -0.8192156
    a03 =   -0.0655238
    b31 =   -0.0560092
    a22 =   -0.0171137
    b13 =    0.0560089
    a40 =    0.0052771
    b32 =   -0.0025614
    a23 =   -0.0003859
    b14 =    0.0012770
    a41 =    0.0003314
    b50 =    0.0002574
    a04 =    0.0000371
    b33 =   -0.0000973
    a42 =    0.0000143
    b51 =    0.0000293
    a24 =   -0.0000090
    b15 =    0.0000291

    dx=(x-x0)*pow(10,-5);
    dy=(y-y0)*pow(10,-5);

    df = a01 * dy + a20 * (dx ** 2) + a02 * (dy ** 2) + a21 * (dx ** 2) * dy + a03 * (dy ** 3)
    df+= a40 * (dx ** 4) + a22 * (dx ** 2) * (dy ** 2) + a04 * (dy ** 4) + a41 * (dx ** 4) * dy
    df+= a23 * (dx ** 2) * (dy ** 3) + a42 * (dx ** 4) * (dy ** 2) + a24 * (dx ** 2) * (dy ** 4)
    f = f0 + df/3600

    dl = b10 * dx + b11 * dx * dy + b30 * (dx ** 3) + b12 * dx * (dy ** 2) + b31 * (dx ** 3) * dy
    dl+= b13 * dx * (dy ** 3) + b50 * (dx ** 5) + b32 * (dx ** 3) * (dy ** 2) + b14 * dx * (dy ** 4)
    dl+= b51 * (dx ** 5) * dy + b33 * (dx ** 3) * (dy ** 3) + b15 * dx * (dy ** 5)
    l = l0 + dl/3600

    fWgs= f + (-96.862 - 11.714 * (f-52)- 0.125 * (l-5)) / 100000
    lWgs= l + (-37.902 +  0.329 * (f-52)-14.667 * (l-5)) / 100000

    return (fWgs,lWgs)


sm_a = 6378137.0
sm_b = 6356752.314
sm_EccSquared = 6.69437999013e-03

def FootpointLatitude(y):
    #
    # Computes the footpoint latitude for use in converting transverse
    # Mercator coordinates to ellipsoidal coordinates.
    #
    # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    #   GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    #
    # Inputs:
    #   y - The UTM northing coordinate, in meters.
    #
    # Returns:
    #   The footpoint latitude, in radians.
    #

    # Precalculate n (Eq. 10.18) */
    n = (sm_a - sm_b) / (sm_a + sm_b)

    # Precalculate alpha_ (Eq. 10.22) */
    # (Same as alpha in Eq. 10.17) */
    alpha_ = ((sm_a + sm_b) / 2.0) \
            * (1 + (math.pow (n, 2.0) / 4) + (math.pow (n, 4.0) / 64))

    # Precalculate y_ (Eq. 10.23) */
    y_ = y / alpha_

    # Precalculate beta_ (Eq. 10.22) */
    beta_ = (3.0 * n / 2.0) + (-27.0 * math.pow (n, 3.0) / 32.0) \
            + (269.0 * math.pow (n, 5.0) / 512.0)

    # Precalculate gamma_ (Eq. 10.22) */
    gamma_ = (21.0 * math.pow (n, 2.0) / 16.0) \
            + (-55.0 * math.pow (n, 4.0) / 32.0)

    # Precalculate delta_ (Eq. 10.22) */
    delta_ = (151.0 * math.pow (n, 3.0) / 96.0) \
            + (-417.0 * math.pow (n, 5.0) / 128.0)

    # Precalculate epsilon_ (Eq. 10.22) */
    epsilon_ = (1097.0 * math.pow (n, 4.0) / 512.0)

    # Now calculate the sum of the series (Eq. 10.21) */
    result = y_ + (beta_ * math.sin (2.0 * y_)) \
            + (gamma_ * math.sin (4.0 * y_)) \
            + (delta_ * math.sin (6.0 * y_)) \
            + (epsilon_ * math.sin (8.0 * y_))

    return result


# MapXY to WGS84 Calculation
def GetWgs84FromMapXY(x,y,lambda0):
    #
    # MapXYToLatLon
    #
    # Converts x and y coordinates in the Transverse Mercator projection to
    # a latitude/longitude pair.  Note that Transverse Mercator is not
    # the same as UTM; a scale factor is required to convert between them.
    #
    # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    #   GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    #
    # Inputs:
    #   x - The easting of the point, in meters.
    #   y - The northing of the point, in meters.
    #   lambda0 - Longitude of the central meridian to be used, in radians.
    #
    # Returns:
    #   philambda - A 2-element containing the latitude and longitude
    #               in radians.
    #
    # Remarks:
    #   The local variables Nf, nuf2, tf, and tf2 serve the same purpose as
    #   N, nu2, t, and t2 in MapLatLonToXY, but they are computed with respect
    #   to the footpoint latitude phif.
    #
    #   x1frac, x2frac, x2poly, x3poly, etc. are to enhance readability and
    #   to optimize computations.
    #


    # Get the value of phif, the footpoint latitude. */
    phif = FootpointLatitude (y)

    # Precalculate ep2 */
    ep2 = (math.pow (sm_a, 2.0) - math.pow (sm_b, 2.0)) / math.pow (sm_b, 2.0)

    # Precalculate cos (phif) */
    cf = math.cos (phif)

    # Precalculate nuf2 */
    nuf2 = ep2 * math.pow (cf, 2.0)

    # Precalculate Nf and initialize Nfpow */
    Nf = math.pow (sm_a, 2.0) / (sm_b * math.sqrt (1 + nuf2))
    Nfpow = Nf

    # Precalculate tf */
    tf = math.tan (phif);
    tf2 = tf * tf;
    tf4 = tf2 * tf2;

    # Precalculate fractional coefficients for x**n in the equations
    # below to simplify the expressions for latitude and longitude. */
    x1frac = 1.0 / (Nfpow * cf)

    Nfpow *= Nf    # now equals Nf**2) */
    x2frac = tf / (2.0 * Nfpow)

    Nfpow *= Nf    # now equals Nf**3) */
    x3frac = 1.0 / (6.0 * Nfpow * cf)

    Nfpow *= Nf    # now equals Nf**4) */
    x4frac = tf / (24.0 * Nfpow)

    Nfpow *= Nf    # now equals Nf**5) */
    x5frac = 1.0 / (120.0 * Nfpow * cf)

    Nfpow *= Nf    # now equals Nf**6) */
    x6frac = tf / (720.0 * Nfpow)

    Nfpow *= Nf    # now equals Nf**7) */
    x7frac = 1.0 / (5040.0 * Nfpow * cf)

    Nfpow *= Nf    # now equals Nf**8) */
    x8frac = tf / (40320.0 * Nfpow)

    # Precalculate polynomial coefficients for x**n.
    # -- x**1 does not have a polynomial coefficient. */
    x2poly = -1.0 - nuf2

    x3poly = -1.0 - 2 * tf2 - nuf2

    x4poly = 5.0 + 3.0 * tf2 + 6.0 * nuf2 - 6.0 * tf2 * nuf2 \
        - 3.0 * (nuf2 *nuf2) - 9.0 * tf2 * (nuf2 * nuf2)

    x5poly = 5.0 + 28.0 * tf2 + 24.0 * tf4 + 6.0 * nuf2 + 8.0 * tf2 * nuf2

    x6poly = -61.0 - 90.0 * tf2 - 45.0 * tf4 - 107.0 * nuf2 + 162.0 * tf2 * nuf2

    x7poly = -61.0 - 662.0 * tf2 - 1320.0 * tf4 - 720.0 * (tf4 * tf2)

    x8poly = 1385.0 + 3633.0 * tf2 + 4095.0 * tf4 + 1575 * (tf4 * tf2)

    # Calculate latitude */
    philambda0 = phif + x2frac * x2poly * (x * x) \
            + x4frac * x4poly * math.pow (x, 4.0) \
            + x6frac * x6poly * math.pow (x, 6.0) \
            + x8frac * x8poly * math.pow (x, 8.0)

    # Calculate longitude */
    philambda1 = lambda0 + x1frac * x \
            + x3frac * x3poly * math.pow (x, 3.0) \
            + x5frac * x5poly * math.pow (x, 5.0) \
            + x7frac * x7poly * math.pow (x, 7.0)

    return (RadToDeg(philambda0),RadToDeg(philambda1))



UTMScaleFactor = 0.9996;
pi = 3.14159265358979;

def DegToRad (deg):
    return (deg / 180.0 * pi)

def RadToDeg (rad):
    return (rad / pi * 180.0)

def UTMCentralMeridian(zone):
    #
    # Determines the central meridian for the given UTM zone.
    #
    # Inputs:
    #     zone - An integer value designating the UTM zone, range [1,60].
    #
    # Returns:
    #   The central meridian for the given UTM zone, in radians, or zero
    #   if the UTM zone parameter is outside the range [1,60].
    #   Range of the central meridian is the radian equivalent of [-177,+177].
    #
    return DegToRad (-183.0 + (zone * 6.0))


# UTM to WGS84 Calculation
def GetWgs84FromUTM(x,y,zone,southhemi):
    #
    # Converts x and y coordinates in the Universal Transverse Mercator
    # projection to a latitude/longitude pair.
    #
    # Inputs:
    #    x - The easting of the point, in meters.
    #    y - The northing of the point, in meters.
    #    zone - The UTM zone in which the point lies.
    #    southhemi - True if the point is in the southern hemisphere;
    #               false otherwise.
    #
    # Returns:
    #    latlon - A 2-element array containing the latitude and
    #            longitude of the point, in radians.
    #
    x -= 500000.0;
    x /= UTMScaleFactor

    # If in southern hemisphere, adjust y accordingly. */
    if (southhemi):
        y -= 10000000.0

    y /= UTMScaleFactor

    cmeridian = UTMCentralMeridian (zone)
    return GetWgs84FromMapXY (x, y, cmeridian)



def CalculateDistanceAndBearing(fromwgs,towgs):
    """Uses the spherical law of cosines to calculate the distance and bearing between two positions"""
    from_lat_dec  = fromwgs[0]
    from_long_dec = fromwgs[1]
    to_lat_dec    = towgs[0]
    to_long_dec   = towgs[1]

    # For each co-ordinate system we do, what are the A, B and E2 values?
    # List is A, B, E^2 (E^2 calculated after)
    abe_values = {
	    'wgs84': [ 6378137.0, 6356752.3141, -1 ],
	    'osgb' : [ 6377563.396, 6356256.91, -1 ],
	    'osie' : [ 6377340.189, 6356034.447, -1 ]
        }

    # The earth's radius, in meters, as taken from an average of the WGS84
    #  a and b parameters (should be close enough)
    earths_radius = (abe_values['wgs84'][0] + abe_values['wgs84'][1]) / 2.0

    # Turn them all into radians
    from_theta = float(from_lat_dec)  / 360.0 * 2.0 * math.pi
    from_landa = float(from_long_dec) / 360.0 * 2.0 * math.pi
    to_theta = float(to_lat_dec)  / 360.0 * 2.0 * math.pi
    to_landa = float(to_long_dec) / 360.0 * 2.0 * math.pi

    try:
        distance = math.acos(
                math.sin(from_theta) * math.sin(to_theta) +
                math.cos(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
		    ) * earths_radius
    except:
        distance = 0
        print "Exception when calculating distance in datums.py@358"

    bearing = math.atan2(
                math.sin(to_landa-from_landa) * math.cos(to_theta),
                math.cos(from_theta) * math.sin(to_theta) -
                math.sin(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
            )
    bearing = bearing / 2.0 / math.pi * 360.0

    return distance, bearing % 360



if __name__ == '__main__':
    print GetWgs84FromRd(140000,400000)

    # should be 42.6349, 0.8541
    print GetWgs84FromUTM(324055.7376140191,4722504.569118755,31,False)
