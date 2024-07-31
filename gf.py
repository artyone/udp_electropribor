import numpy as np
from functools import cache

def coord_circle(radius, angle_deg):
    angle = np.deg2rad(angle_deg)
    rotatedX = radius * np.cos(angle) - 0 * np.sin(angle)
    rotatedY = radius * np.sin(angle) + 0 * np.cos(angle)
    return rotatedX, rotatedY

def get_gf():
    D_ANT_L = 0.45
    D_ANT_B = 0.95
    D_V = 0.225
    gf = (
        (*coord_circle(D_ANT_L/2, 0),       D_V*0),  #0 1 этаж
        (*coord_circle(D_ANT_L/2, 22.5*1),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*2),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*3),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*4),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*5),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*6),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*7),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*8),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*9),  D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*10), D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*11), D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*12), D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*13), D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*14), D_V*0),
        (*coord_circle(D_ANT_L/2, 22.5*15), D_V*0),

        # след этаж---------------------------
        (*coord_circle(D_ANT_L/2, 0),       D_V*1),   #16 2 этаж
        (*coord_circle(D_ANT_L/2, 22.5*1),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*2),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*3),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*4),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*5),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*6),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*7),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*8),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*9),  D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*10), D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*11), D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*12), D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*13), D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*14), D_V*1),
        (*coord_circle(D_ANT_L/2, 22.5*15), D_V*1),
        # след этаж---------------------------
        (*coord_circle(D_ANT_L/2, 0),       D_V*2),   #32 3 этаж
        (*coord_circle(D_ANT_L/2, 22.5*1),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*2),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*3),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*4),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*5),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*6),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*7),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*8),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*9),  D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*10), D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*11), D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*12), D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*13), D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*14), D_V*2),
        (*coord_circle(D_ANT_L/2, 22.5*15), D_V*2),    
        # центр-------------------------------
        (*coord_circle(0, 0),               D_V*0),  #48  центральный ряд
        (*coord_circle(0, 0),               D_V*1),
        (*coord_circle(0, 0),               D_V*2),
        # доп гидрофоны на большем диаметре-------
        (*coord_circle(D_ANT_B/2, 0),       D_V*0),  #51  4 гидрофона большого диаметра
        (*coord_circle(D_ANT_B/2, 90),      D_V*0),
        (*coord_circle(D_ANT_B/2, 180),     D_V*0),
        (*coord_circle(D_ANT_B/2, 270),     D_V*0)
    )

    return gf

@cache
def get_sig(phi, um, fz, vt, sampling, gf):
    phi = np.deg2rad(phi)
    gf = np.array(gf)
    t = np.linspace(0, 1, sampling)
    ep = np.asmatrix([np.cos(um) * np.cos(phi), np.cos(um) * np.sin(phi), np.sin(um)])
    res = np.array(np.exp(-1j * (2 * np.pi * (fz / vt)* gf *ep.T)))

    coefs = np.arctan2(res.imag, res.real)
    data = np.sin(2 * np.pi * fz * t + coefs)
    
    return data