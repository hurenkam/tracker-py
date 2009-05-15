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
# Author(s):
#
#    Ed Stevenhagen	Stevenhagen <at> xs4all.nl
#	Original Javascript version for RD to WGS84 calculation
#
#    Nick Burch
#       Distance and Bearing calculations (from geo_helper.py)
#
#    Mark Hurenkamp	Mark.Hurenkamp <at> xs4all.nl
#	Port to python

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

    distance = math.acos(
                math.sin(from_theta) * math.sin(to_theta) +
                math.cos(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
		    ) * earths_radius

    bearing = math.atan2(
                math.sin(to_landa-from_landa) * math.cos(to_theta),
                math.cos(from_theta) * math.sin(to_theta) -
                math.sin(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
            )
    bearing = bearing / 2.0 / math.pi * 360.0

    return distance, bearing % 360



if __name__ == '__main__':
    print GetWgsFromRd(140000,400000)
