# -*- coding: utf-8 -*-
"""
Created on Wed May  2 13:03:45 2018

@author: Benedikt
"""

from Punkte import Point2D
from Linie import Line2D
import numpy as np


class Force:
    """point of action, dx, dy, amount"""
    def __init__(self,acting_point,dx,dy,amount,scale = 0.25, scaled = False):
        if type(acting_point) == Point2D:
            self.p1 = acting_point
        else:         
            self.p1 = Point2D(acting_point[1],acting_point[2])
            
        self.scale = scale
        self.scaled = scaled
        self.p2 = Point2D(self.p1.x-dx,self.p1.y-dy)
        self.dx = float(dx)
        self.dy = float(dy)
        self.amount = float(amount)
        self.amount_abs = float(abs(amount))
        
        #don't try to scale if dx, dy and amount == 0
        if self.dx == 0 and self.dy == 0 and amount == 0:
            self.scaled = True
        
        #scale to length and scale of drawing
        if self.scaled == False:
            self.scale_force()
        
        if round(self.amount,5) != 0:
            self.line = Line2D(self.p1,self.p2)                     
    
    def scale_force(self): 
        
        if round(self.amount,5) != 0:
            self.dx = float(self.dx*self.amount_abs*self.scale/self.p1.distance(self.p2))
            self.dy = float(self.dy*self.amount_abs*self.scale/self.p1.distance(self.p2))
            if [self.dx,self.dy] == [0,0]:
                self.p2 = self.p1
            else:            
                self.p2 = Point2D(self.p1.x-self.dx,self.p1.y-self.dy)

    def inverse_proportion(self,p1,p2,other_force_line = False):
    
        base_line = Line2D(p1,p2)
        
        if other_force_line is not False: 
            intersection2 = other_force_line.intersection(base_line)[0]
            self.translate_head_to_point(intersection2)
        
        p3 = Point2D(p1.x-self.dx,p1.y-self.dy)
        prop_line = Line2D(p3,p2)
        intersection0 = Point2D(self.line.intersection(base_line)[0].x-self.dx, self.line.intersection(base_line)[0].y-self.dy)
        intersection1 = self.line.intersection(prop_line)[0]
        intersection2 = self.line.intersection(base_line)[0]
            
        dx_1 = intersection2.x-intersection1.x
        dy_1 = intersection2.y-intersection1.y
        amount_1 = intersection1.distance(intersection2)/self.scale
        force_p1 = Force(p1,dx_1,dy_1,amount_1,self.scale,scaled = True)
        
        dx_2 = intersection1.x-intersection0.x
        dy_2 = intersection1.y-intersection0.y
        amount_2 = intersection0.distance(intersection1)/self.scale
        force_p2 = Force(p2,dx_2,dy_2,amount_2,self.scale,scaled = True)

        return force_p1,force_p2
    
    def resolve_on_lines(self,line1,line2):
        
        from functions import translate_to_point
        
        # create polygon
        line1 = translate_to_point(line1,self.p1)
        line2 = translate_to_point(line2,self.p2)
        intersection = line1.intersection(line2)[0]
        
        #force 1
        dx1 = self.p1.x-intersection.x
        dy1 = self.p1.y-intersection.y
        
        amount1 = float(self.p1.distance(intersection)/self.scale)
        acting_point1 = self.p1
        force1 = Force(acting_point1,dx1,dy1,amount1,self.scale,scaled = True)
        force1.translate_food_to_point(acting_point1)
        
        #force 2
        dx2 = intersection.x-self.p2.x
        dy2 = intersection.y-self.p2.y
        
        amount2 = float(self.p2.distance(intersection)/self.scale)
        acting_point2 = intersection
        force2 = Force(acting_point2,dx2,dy2,amount2,self.scale,scaled = True)
        force2.translate_food_to_point(acting_point2)
        
        return force1,force2
    
    def get_y_component(self):
        y_amount = self.amount * float(abs(self.dy / np.sqrt((np.square(self.dy)+np.square(self.dx)))))
        y_force = Force(self.p1,0,self.dy,y_amount,self.scale)
        return y_force
    
    def get_opponent_force(self):
        acting_point = self.p1
        self.mirror_at_foodpoint()
        self.translate_head_to_point(acting_point)
    
    def mirror_at_foodpoint(self):
        self.dx = -self.dx
        self.dy = -self.dy
        self.p1 = Point2D(self.p2.x+self.dx,self.p2.y+self.dy)
        
    def mirror_at_headpoint(self):
        head = self.p1
        self.mirror_at_foodpoint()
        self.translate_head_to_point(head)
        
    def translate_head_to_point(self,point):
        self.p1 = point
        self.p2 = Point2D(self.p1.x-self.dx,self.p1.y-self.dy)
        
        if round(self.amount,5) != 0:
            self.line = Line2D(self.p1,self.p2)
                          
    def translate_food_to_point(self,point):
        self.p2 = point
        self.p1 = Point2D(self.p2.x+self.dx,self.p2.y+self.dy)
        
        if round(self.amount,5) != 0:
            self.line = Line2D(self.p1,self.p2)
        
    def report(self):
        print('acting point =',self.p1)
        print('food =', self.p2)
        print('dx =', self.dx)
        print('dy =', self.dy)
        print('amount =',round(self.amount,5))
        
    def change_scale(self,new_scale):
        self.scale = new_scale
        self.scale_force()
    
    
    ''' if __name__ == '__main__':
    # this was run as a main script
        from Class_Force import Force
        
        acting_point = Point2D(0,0)
        b = Force(acting_point,0,-1,10)
        f3,f4 = b.inverse_proportion(Point2D(-5,0),Point2D(10,0))
        f3.report()
        f4.report()
        
        yb = b.get_y_component()
        yb.report()
        
        b.get_opponent_force()
        b.report()'''
        

