# cython: language_level=3
import cython
from datetime import datetime, timedelta
import json
from libc.math cimport abs as c_abs

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef dict calculate_transit_data(dict natal_data, dict transit_data, double filter_orb=-1.0):
    """Optimized transit calculations"""
    cdef:
        dict filtered_data = {}
        list aspects = []
        double orbit
        str aspect_name, planet1_name, planet2_name
    
    # Copy relevant data (preserve the full structure)
    filtered_data = transit_data.copy()
    
    # Get aspects from the correct nested location
    aspects = filtered_data.get('subject', {}).get('aspects', [])
    
    # Filter aspects if orb specified (using -1.0 as sentinel value)
    if filter_orb >= 0:
        filtered_aspects = []
        for aspect in aspects:
            orbit = abs(float(aspect.get('orbit', 0)))
            if orbit <= filter_orb:
                filtered_aspects.append(aspect)
        filtered_data['subject']['aspects'] = filtered_aspects
    
    return filtered_data