class GPSInfoError(Exception): pass

def rational_to_float(rational):
    if not isinstance(rational, tuple):
        raise GPSInfoError
    if not len(rational) == 2:
        raise GPSInfoError
    if rational[1] == 0:
        raise GPSInfoError
    return float(rational[0]) / rational[1]

def to_degrees(degs, mins, secs):
    degs = rational_to_float(degs)
    mins = rational_to_float(mins)
    secs = rational_to_float(secs)
    return degs + mins / 60. + secs / 3600.

def parse_gps_info(adict):
    if not adict[1] in 'NS' or not adict[3] in 'EW':
        raise GPSInfoError

    if not len(adict[2]) == 3 or not len(adict[4]) == 3:
        raise GPSInfoError

    xpos = to_degrees(*adict[2]) * (-1 if adict[1] == 'S' else 1)
    ypos = to_degrees(*adict[4]) * (-1 if adict[3] == 'W' else 1)
    return xpos, ypos
