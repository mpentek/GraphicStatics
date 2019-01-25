#class cremona_plan 
from utilities.geometric_utilities import sort_left_to_right, sort_right_to_left,getSecond, right_left
from node2d import Node2D
from segment2d import Segment2D
from utilities.mechanical_utilities import sort_clockwise
from utilities.plo_cremona_plan import plot_cremona_plan

class cremona_plan():
    def __init__(self,analysis):
       model = analysis.input_system["forces"]
       nodes = analysis.input_system["nodes"]
       elements = analysis.input_system["elements"]
       bottom_or_top = analysis.input_system["bel_chord"]

       

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
       sorted_member_forces = sort_left_to_right(member_forces, nodes)
      

      
    #    model['14i'].direction = [0.7071067811865476, -0.7071067811865476]+
    #    model['14j'].direction = [-0.7071067811865476, 0.7071067811865476]
    #    model['15i'].direction = [0.658504607868518, -0.7525766947068778]
    #    model['15j'].direction = [-0.658504607868518, 0.7525766947068778]
      
    #    model['16i'].direction = [-0.7071067811865476, -0.7071067811865476]
    #    model['16j'].direction = [0.7071067811865476, 0.7071067811865476]

       #Lasten für sort_clockwise richtig einordnen
       print(bottom_or_top)
       x_real = []
       y_real = []
       for i in ex_forces:
            x = model[i].direction[0]
            y = model[i].direction[1]
            x_real.append(x)
            y_real.append(y)

            if bottom_or_top == 'top':
               #y-Koordinate muss positiv sein
               if y < 0:
                 model[i].direction[0] = -x
                 model[i].direction[1] = abs(y)

            if bottom_or_top == 'bottom':
               #y_koordinate muss negativ sein
               if y > 0:
                 model[i].direction[0] = -x
                 model[i].direction[1] = -y

                

       #Kräfte an Knoten sortieren
       for i in nodes:
           sort_forces = []
           force_at_node = nodes[i].forces
           for j in range(len(force_at_node)):
               sort_forces.append(model[force_at_node[j]])
           sorted_forces = sort_clockwise(sort_forces, bottom_or_top)
           nodes[i].forces = sorted_forces
           print(i,sorted_forces)

    #    'nodes[2].forces = ['e2', '2i', '15i', '11i', '1j']
    #    nodes[1].forces = ['e1', '1i', '14i', '10i', '0j']
    #    nodes[4].forces = ['e4', '4i', '13i', '3j']
    #    nodes[3].forces =  ['e3', '3i', '16i', '12i', '2j']'
    #    model['14j'].direction = [0.7071067811865476, -0.7071067811865476]
           
       #Externe Lasten wieder 'richtig' einspeichern
       count = 0
       for i in ex_forces:
            model[i].direction[0] = x_real[count]
            model[i].direction[1] = y_real[count]
            count = count + 1
       

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

       self.points = dict(zip(node_id, points))
       self.ex_forces = dict(zip(sorted_ex,elements))

       elements = []
    

        #reactions "zeichnen/speichern"
       already_done = []
       for i in sorted_reactions:
           already_done.append(i)
           force = reactions[i]
           start.forces.append(i)

           x = force.direction[0]
           y = force.direction[1]
           

           x_amount = start.coordinates[0] + force.magnitude*x
           y_amount = start.coordinates[1] + force.magnitude*y
           start = Node2D(a,[x_amount,y_amount])
        
           start.forces.append(i)
               
           
           points.append(start)
           node_id.append(a)
           element = Segment2D(a-1,[points[a-1],points[a]])
           elements.append(element)
           a = a + 1

       self.points = dict(zip(node_id,points))
       self.reactions = dict(zip(sorted_reactions,elements))
    
       elements = [] 
       members = []
       self.members = {}

       for i in sorted_ex:
           #weitere forces an dem Knoten "einzeichnen"
           current_node = ex_forces[i].node_id
           print('node', current_node)
           other_forces = nodes[current_node].forces
           already_done.append(i)
           start = None
           change = 1


           while change == 1:
             for j in range(len(other_forces)):
                 print(other_forces[j])
                 if other_forces[j] in already_done:
                     if other_forces[j] in self.ex_forces:
                         start = self.ex_forces[other_forces[j]].nodes[1]
                         points.append(start)
                         node_id.append(a)
                         a = a + 1
                         
                     else:
                         change = 0 

                 if start != None:
                     if other_forces[j] not in already_done:
                         force = model[str(other_forces[j])]
                         start.forces.append(j)
                         print('start', start.coordinates)
           
                         x_amount = start.coordinates[0] + force.magnitude*force.direction[0]
                         y_amount = start.coordinates[1] + force.magnitude*force.direction[1]

                         print(force.direction, force.magnitude)

                         start = Node2D(a,[x_amount,y_amount])
                         start.forces.append(j)
                         print('start',start.coordinates)
           
                         points.append(start)
                         node_id.append(a)
                         element = Segment2D(a-1,[points[a-1],points[a]])
                         elements.append(element)
                         members.append(other_forces[j])
                         already_done.append(other_forces[j])
                         a = a + 1

                         
                         

                

       self.points = dict(zip(node_id, points))
       self.members = dict(zip(members,elements))

       

       #Elemente nach type aufteilen,
       type_forces = []
       for i in range(len(sorted_member_forces)):
           type_force = model[sorted_member_forces[i]].force_type
           type_forces.append(type_force)
           
       force_id = sorted_member_forces
       sorted_members = dict(sorted(zip(force_id,type_forces),key = getSecond))
       bel_chord = {}
       unbel_chord = {}
       Verbindung = {}
       

       #andere Elemente löschen
       for i in sorted_members:
           if sorted_members[i] == 1:
              bel_chord[i] = model[i]

       for i in sorted_members:
           if sorted_members[i] == 2:
              unbel_chord[i] = model[i]

       for i in sorted_members:
           if sorted_members[i] == 3:
              Verbindung[i] = model[i]

       #member unbel_chord einfügen
      
       #sort unbel_chord
       nodes_unbel = []
       force_id = []
       for i in unbel_chord:
           coo_node = nodes[unbel_chord[i].node_id].coordinates
           nodes_unbel.append(coo_node)
           force_id.append(i)
       sorted_unbel_chord = dict(sorted(sorted(zip(force_id,nodes_unbel),reverse = True),key = getSecond, reverse = True))
       print('here',sorted_unbel_chord)
    #    forces_unbel = []
    #    force_id = []

   
    #    sorted_unbel_chord = list(sorted(unbel_chord, reverse = True))
    #    length = int(len(sorted_unbel_chord)/2)
    #    print('1 sorted_unbel_chord', sorted_unbel_chord)
    #    a= 0
    #    b = 1
    #    for i in range(length):
    #        force = model[sorted_unbel_chord[a]]
    #        force1 = model[sorted_unbel_chord[b]]

    #        if nodes[force.node_id].coordinates[0] > nodes[force1.node_id].coordinates[1]:
    #           force_id.append(sorted_unbel_chord[a])
    #           force_id.append(sorted_unbel_chord[b])
    #           forces_unbel.append(force)
    #           forces_unbel.append(force1)
    #        else:
    #             force_id.append(sorted_unbel_chord[b])
    #             force_id.append(sorted_unbel_chord[a])
    #             forces_unbel.append(force1)
    #             forces_unbel.append(force)

    #        a = a+2 
    #        b = b+2


    #    sorted_unbel_chord = sort_right_to_left(dict(zip(force_id,forces_unbel)),nodes)
    #    print('sorted_unbel_chord', sorted_unbel_chord)

       #start bestimmen
       print('sorted_reactions', sorted_reactions)
       if model[sorted_reactions[0]].node_id == model[sorted_reactions[1]].node_id:
           start = self.reactions[sorted_reactions[1]].nodes[1]
           print('Version a')
       else:
           start = self.reactions[sorted_reactions[0]].nodes[1]
           print('Version b',sorted_reactions[0], start.coordinates )
       points.append(start)
       a= a+1
         
       #member einzeichnen
       print('sort',sorted_unbel_chord)
       for i in sorted_unbel_chord:  
    #    for i in range(len(sorted_unbel_chord)):  
             print(i,start.coordinates)      
            #  force = model[sorted_unbel_chord[i]]
             force = unbel_chord[i]

             start.forces.append(i)
             print('x', force.direction[0], 'y', force.direction[1])
           
             x_amount = start.coordinates[0] + force.magnitude*force.direction[0]
             y_amount = start.coordinates[1] + force.magnitude*force.direction[1]

             start = Node2D(a,[x_amount,y_amount])
             start.forces.append(i)
             print(start.coordinates)
           
             points.append(start)
             node_id.append(a)
             element = Segment2D(a-1,[points[a-1],points[a]])
             elements.append(element)
             members.append(i)
             already_done.append(i)
            #  members.append(sorted_unbel_chord[i])
            #  already_done.append(sorted_unbel_chord[i])
             a = a + 1
      

       self.points = dict(zip(node_id, points))
       self.members = dict(zip(members,elements))
       print('members', members)



       #plot_cremona_plan
       plot_cremona_plan(self)
       
       member_forces = []
       new_coordinates = []
       
       


        

    

    #Elemente einfügen    

    #    self.draw_cremona_plan()

    