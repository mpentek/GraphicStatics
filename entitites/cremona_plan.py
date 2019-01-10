#class cremona_plan 
from force2d import Force2D
from utilities.geometric_utilities import sort_left_to_right, sort_right_to_left,getSecond
from node2d import Node2D
from segment2d import Segment2D
from utilities.mechanical_utilities import sort_clockwise

class cremona_plan():
    def __init__(self,analysis):
       model = analysis.input_system["forces"]
       nodes = analysis.input_system["nodes"]
       

       self.points = {}
       self.ex_forces = {}
     
       force_id = analysis.input_system["forces"].keys()
       str_keys = ""
       for i in force_id:
           str_keys = str_keys + str(i)

       number_ex_forces = str_keys.count("e") #bei den ex_forces beginnt der Index bei 1!
       number_reactions = str_keys.count("r")

       b= number_ex_forces + number_reactions
       
       #in versch Kräfte aufteilen
       ex_forces = dict(list(model.items())[:number_ex_forces])
       reactions = dict(list(model.items())[number_ex_forces : b])
       member_forces = dict(list(model.items())[b : -1])

       sorted_ex = sort_left_to_right(ex_forces , nodes)
       sorted_reactions = sort_right_to_left(reactions, nodes)

       #Kräfte an Knoten sortieren
       for i in nodes:
           sort_forces = []
           force_at_node = nodes[i].forces
           for j in range(len(force_at_node)):
               sort_forces.append(model[force_at_node[j]])
           sorted_forces = sort_clockwise(sort_forces)
           nodes[i].forces = sorted_forces
    
       

       #Externe Lasten in Cremonaplan "speichern/zeichnen"
       points  = [Node2D(0,[0,0])]
       start = Node2D(0,[0,0])
       elements = []
       a = 1
       node_id = [0]

       for i in sorted_ex:
           force = ex_forces[i]
           start.forces.append(i)
           
           x_amount = start.coordinates[0] + force.magnitude*force.direction[0]
           y_amount = start.coordinates[1] + force.magnitude*force.direction[1]
           start = Node2D(a,[x_amount,y_amount])
           start.forces.append(i)
           
           points.append(start)
           node_id.append(a)
           element = Segment2D(a-1,[points[a-1],points[a]])
           elements.append(element)
           a = a + 1

       self.points = dict(zip(node_id,points))
       self.ex_forces = dict(zip(sorted_ex,elements))

       elements = [] 
       members = []
       already_done = []
       self.members = {}
       

       for i in sorted_ex:
           #weitere forces an dem Knoten "einzeichnen"
           current_node = ex_forces[i].node_id
           other_forces = nodes[current_node].forces
           already_done.append(i)
           start = None
           change = 1

           while change == 1:
             for j in range(len(other_forces)):
                 if other_forces[j] in already_done:
                     if other_forces[j] in self.ex_forces:
                         start = self.ex_forces[other_forces[j]].nodes[1]
                         
                     else:
                         change = 0 

                 if start != None:
                     if other_forces[j] not in already_done:
                         force = model[str(other_forces[j])]
                         start.forces.append(j)
           
                         x_amount = start.coordinates[0] + force.magnitude*force.direction[0]
                         y_amount = start.coordinates[1] + force.magnitude*force.direction[1]
                         start = Node2D(a,[x_amount,y_amount])
                         start.forces.append(j)
           
                         points.append(start)
                         node_id.append(a)
                         element = Segment2D(a-1,[points[a-1],points[a]])
                         elements.append(element)
                         members.append(other_forces[j])
                         already_done.append(other_forces[j])
                         a = a + 1
                         
                         

                

       self.points = dict(zip(node_id,points))
       self.members = dict(zip(members,elements))

       elements = []
       

       #reactions "zeichnen/speichern"
       for i in sorted_reactions:
           force = reactions[i]
           start.forces.append(i)
           
           x_amount = start.coordinates[0] + force.magnitude*force.direction[0]
           y_amount = start.coordinates[1] + force.magnitude*force.direction[1]
           start = Node2D(a,[x_amount,y_amount])
           start.forces.append(i)
           
           points.append(start)
           node_id.append(a)
           element = Segment2D(a-1,[points[a-1],points[a]])
           elements.append(element)
           a = a + 1

       self.points = dict(zip(node_id,points))
       self.reactions = dict(zip(sorted_reactions,elements))

       

       #Elemente nach type aufteilen
       type_forces = []
       for i in member_forces:
           type_force = member_forces[i].force_type
           type_forces.append(type_force)
           
       force_id = list(member_forces.keys())
       sorted_members = dict(sorted(zip(force_id,type_forces),key = getSecond))
       bel_chord = {}
       unbel_chord = {}
       Verbindung = {}

       #andere Elemente löschen
       for i in sorted_members:
           if sorted_members[i] == 1:
              bel_chord[i] = 1

       for i in sorted_members:
           if sorted_members[i] == 2:
              unbel_chord[i] = 2

       for i in sorted_members:
           if sorted_members[i] == 3:
              Verbindung[i] = 3

       #KnotenGG am bel_chord "zeichnen/speichern"
       
       member_forces = []
       new_coordinates = []
       
       


        

    

    #Elemente einfügen    

    #    self.draw_cremona_plan()

    