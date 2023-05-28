def get_color(value):
    #Maps a value between 1 and 2000 to a color between blue and red

    # Define the blue and red color values
    blue = (0, 0, 255)
    red = (255, 0, 0)
    
    # Interpolate between blue and red based on the value
    # NOTE: change 999 to increase the upper bound for the color red 
    t = (value - 1) / 999 
    color = tuple(int(round((1 - t) * b + t * r)) for b, r in zip(blue, red))
    
    # Convert the color to hexadecimal format
    return '#{:02x}{:02x}{:02x}'.format(*color)


def hsv_to_rgb(h, s, v):
    # Converts an HSV color value to an RGB color value
    if s == 0.0:
        return (v, v, v)
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - (s * f))
    t = v * (1.0 - (s * (1.0 - f)))
    if i % 6 == 0:
        return (v, t, p)
    elif i == 1:
        return (q, v, p)
    elif i == 2:
        return (p, v, t)
    elif i == 3:
        return (p, q, v)
    elif i == 4:
        return (t, p, v)
    else:
        return (v, p, q)
    
def scale_value(value):
    # Scales a value between 0 and 10439 to a value between 1 and 10
    return (value - 0) / (10439 - 0) * (100 - 10) + 10