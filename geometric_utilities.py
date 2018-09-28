# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:01:22 2018

@author: Benedikt
"""

import numpy as np
import matplotlib.pyplot as plt
import math

# PMT remove sympy dependency
from sympy import Point2D, Line2D, Segment2D

# own modules
#from plot import plot_fr_poly, plot_fun_poly,plot_method_of_joints,plot_poleline,plot_cremona, plot_cutting_line
#from force import Force

## PMT
'''
differentiate between geometric utilitites
like extend line, etc. ==>> will be completed with
line intersection (own implementation) and similar
and mechanical (or force) utilities
like force polygon, etc.
this file should NOT contain plot related function!

CHECK naming, maybe not better
head ==>> was renamed to start: head_to_point -> start_to_point
food(t) ==>> was renamed to end: foot_to_point -> end_to_point
MAYBE rather head and tail?
'''

def extend_line(x,y,x_min,x_max,y_min,y_max):
    dx = x[1]-x[0]
    dy = y[1]-y[0]

    ## PMT check for horizontal line?
    if round(float(dx),5) == 0: # vertical line
        y = [y_min,y_max]
        x = [x[0],x[0]]
    else: # calculate line with y = mx+t
        m = dy/dx
        t = y[0]-m*x[0]

        y = [m*x_min+t,m*x_max+t]
        x = [x_min,x_max]

    return x,y

def translate_to_point(line, point):

    dx = point.x-line.p1.x
    dy = point.y-line.p1.y

    return translate_delta(line,dx,dy)

def translate_delta(line,dx,dy):

    p1_x = line.p1.x+dx
    p1_y = line.p1.y+dy
    p2_x = line.p2.x+dx
    p2_y = line.p2.y+dy

    p1 = Point2D(p1_x,p1_y)
    p2 = Point2D(p2_x,p2_y)

    return Line2D(p1,p2)

def calculate_angle(point,origin):
    dx = point.x - origin.x
    dy = point.y - origin.y

    distance = point.distance(origin)
    if dx>=0:
        angle = -math.asin(dy/distance)
    elif dx < 0 and dy < 0:
        angle = -math.asin(dy/distance)+math.pi*0.5
    elif dx < 0 and dy >= 0:
        angle = math.asin(dy/distance)+math.pi

    return angle



