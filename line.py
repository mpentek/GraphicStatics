#selfdefined line 2D
from point import Point2D
from math import cos, sin 

TOL = 1e-8

class Line2D:
    
    def __init__(self,p1,p2):

        self.p1 = p1
        self.p2 = p2
        
        #Richtungsvektoren
        self.u = p2.x - p1.x
        self.v = p2.y - p1.y
        
    def coefficients(self):
       # gibt a,b und c aus ax+by+c
       a = self.p1.y-self.p2.y
       b = self.p2.x-self.p1.x
       c = -(a*self.p1.x+b*self.p1.y)
       return [a,b,c]

    '''
       return a*x+b*y+c '''
    
    #checks if a certain point is on the line
    def isonline(self, point):

        if isinstance(point, Point2D):
            a,b,c = self.coefficients()
            value = a*point.x+b*point.y+c
            if abs(value) <= TOL:
                return True
            else:
                return False 

        else:
            raise ValueError('Please enter a valid Point2D object')

    # checks if two lines have an intersection or not
    def isparallel(self,line):
    
       if line.u == 0:
           if (-TOL) <= self.u <= TOL:
               return True
           else:
               return False
        
       if line.v == 0:
           if (-TOL) <= self.v <= TOL:
               return True
           else:
               return False

       a= self.u/line.u
       b = self.v/line.v
       if (b-TOL) <= a <= (b+TOL):
           return True
       else:
            return False 
       
    def intersection(self,line):

     if isinstance(line, Line2D):
  
         #bei parallelen Geraden keinen Schnittpunkt berechnen
         if self.isparallel(line):
             S1 = []
             
             print("The lines are PARALLEL")
             return S1
       
         else:
             a1,b1,c1 = self.coefficients()
             a2,b2,c2 = line.coefficients()
             if b2 == 0: #line vertikal -> Teilen durch 0 -> vertauschen
                 a1,b1,c1 = line.coefficients()
                 a2,b2,c2 = self.coefficients()

             x = ((-1*(b2-b1)/b2+1)*c2-c1)/((a1-a2)+a2*(b2-b1)/b2)
             y = (-a2*x - c2)/b2

             S1 = [Point2D(x,y)]
             return S1 
   
    #Linie um einen bestimmten Punkt rotieren
    def rotate(self,alpha,point):

        if self.isonline(point) == True:
         x= self.p2.x - self.p1.x
         y = self.p2.y - self.p1.y 
         newx = x * cos(alpha) - y * sin(alpha)
         newy = x * sin(alpha) + y* cos(alpha)
    
         self.p1.x,self.p1.y = point.x, point.y
         self.p2.x = self.p1.x + newx
         self.p2.y = self.p1.y + newy 
         new_Line = Line2D(self.p1, self.p2)
         return new_Line