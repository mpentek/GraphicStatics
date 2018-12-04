"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

TOL = 1e-8

def cross_product(vectors):
    return vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0]

def are_parallel(lines):
    # this is the 2d cross product
    if abs(cross_product([lines[0]['direction'], lines[1]['direction']])) <= TOL:
        return True
    else:
        return False

def get_intersection(lines):
    if are_parallel(lines):
        print("The lines are PARALLEL")
        return None
    else:
        a1,b1,c1 = lines[0]['coefficients']
        a2,b2,c2 = lines[1]['coefficients']
        if abs(b2) <= TOL: #line vertikal -> Teilen durch 0 -> vertauschen
            a1,b1,c1 = lines[1]['coefficients']
            a2,b2,c2 = lines[0]['coefficients']

        x = ((-1*(b2-b1)/b2+1)*c2-c1)/((a1-a2)+a2*(b2-b1)/b2)
        y = (-a2*x - c2)/b2

        ## TODO: check for redundancy
        # http://www.pdas.com/lineint.html
        # denom:= a1*b2 - a2*b1
        # x:=(b1*c2 - b2*c1)/denom;
        # y:=(a2*c1 - a1*c2)/denom;

        a1,b1,c1 = lines[0]['coefficients']
        a2,b2,c2 = lines[1]['coefficients']

        denom = a1*b2 - a2*b1
        x = (b1*c2 - b2*c1)/denom
        y = (a2*c1 - a1*c2)/denom
        return [x, y]

def get_line_coefficients(points):
    p1 = points[0]
    p2 = points[1]
    # gibt a,b und c aus ax+by+c
    a = p1[1]-p2[1]
    b = p2[0]-p1[0]
    c = -(a* p1[0]+b*p1[1])
    return [a,b,c]

def get_line(point, direction):
    points = [point]
    points.append([point[0] + direction[0],
                   point[1] + direction[1]])

    line = {}
    line['direction'] = direction
    line['coefficients'] = get_line_coefficients(points)
    return line