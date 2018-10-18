'''LineSegment with attributes: points, length, slope, midpoint'''
from math import sqrt
from line import Line2D
from point import Point2D

TOL = 1e-8

class Segment2D:
    def __init__(self, p1, p2):
        if p1 == p2:
            self.p1 = p1
            self.p2 = p2
        if (p1.x > p2.x) == True:
                self.p1 = p1
                self.p2 = p2
        #elif (p1.x == p2.x) == True and (p1.y > p2.y) == True:
        elif abs(p1.x - p2.x) <= TOL and (p1.y > p2.y) == True:
                    self.p1, self.p2 = p2, p1
        else:
            self.p1 = p1
            self.p2 = p2

        self.points = (self.p1, self.p2)

        # so here it is u component
        self.dx = self.p2.x - self.p1.x
        # so here it is v component
        self.dy = self.p2.y - self.p1.y
        self.length = sqrt(self.dx**2+self.dy**2)

        mx = p1.x + (self.dx/2)
        my = p1.y + (self.dy/2)
        self.midpoint = [mx,my] #Patches need iterable array not Point2D -> false: Point2D(mx,my)

    # erstellen einer Linie senkrecht auf dem Segment
    def perpendicular_line(self,Point):

        # maybe the other way around?
        # p2x = Point.x + self.dy
        # p2y = Point.y - self.dx
        p2x = Point.x - self.dy
        p2y = Point.y + self.dx
        p2 = Point2D(p2x,p2y)
        new_line = Line2D(Point, p2)
        return new_line

    def intersection(self,line):
            if isinstance(line, Line2D):
                new_line = Line2D(self.p1,self.p2)
                S1 = line.intersection(new_line)
                #überprüfen, ob S1 innerhalb Segment
                if S1 is not None:
                    l_segment = sqrt(self.dx*self.dx+self.dy*self.dy)
                    l1 = sqrt((self.p1.x-S1[0].x)**2+(self.p1.y-S1[0].y)**2)
                    l2 = sqrt((self.p2.x-S1[0].x)**2+(self.p2.y-S1[0].y)**2)
                    # if l_segment - TOL <= l1+l2 <= l_segment + TOL:
                    if abs((l1+l2)-l_segment) <= TOL:
                        return S1
                    else:
                        return None
                else:
                    return None


