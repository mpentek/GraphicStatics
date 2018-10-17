# define 2D Point 
import math

TOL = 1e-8

class Point2D:
 """input: x,y - coordinate"""
 _ambient_dimension = 2

 def __init__(self,x,y):
  self.x = x
  self.y = y
  self.length = 0


 def setPoint2D(self,x,y):
  self.x = x
  self.y = y


 def translatePoint2D(self,deltax,deltay):
  self.x = self.x + deltax
  self.y = self.y + deltay

 def multipliPoint2D(self, factor):
     self.x= self.x * factor 
     self.y= self.y * factor


  #Abstand zwischen zwei Punkten
 def distance(self, Point):
     deltax= Point.x - self.x
     deltay = Point.y- self.y 
     d = math.sqrt((deltax* deltax) + (deltay * deltay))
     return d



