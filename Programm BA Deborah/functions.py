# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:01:22 2018

@author: Benedikt
"""
from Segment import   Segment2D
from Punkte import Point2D
from Linie import Line2D
from Class_Force import Force
import numpy as np
from plot import plot_fr_poly, plot_fun_poly,plot_method_of_joints,plot_poleline,plot_cremona, plot_cutting_line
import matplotlib.pyplot as plt
import math


def extend_line(x,y,x_min,x_max,y_min,y_max):
    dx = x[1]-x[0]
    dy = y[1]-y[0]
    
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
    
    dx = point.x - line.p1.x
    dy = point.y-line.p1.y
    
    new_line = translate_delta(line,dx,dy)
    
    return new_line
    
def translate_delta(line,dx,dy):
    
    p1_x = line.p1.x+dx
    p1_y = line.p1.y+dy
    p2_x = line.p2.x+dx
    p2_y = line.p2.y+dy
    
    p1 = Point2D(p1_x,p1_y)
    p2 = Point2D(p2_x,p2_y)
    
    new_line = Line2D(p1,p2)
    
    return new_line

def force_polygon(ax_fr_poly,scale,forces):
    closed = False
    start = Point2D(0,0)
   
    fr_polygon = []
    
    for i in range(len(forces)):
        dx = forces[i][0].p1.x-forces[i][0].p2.x
        dy = forces[i][0].p1.y-forces[i][0].p2.y
        p1 = Point2D(start.x+dx,start.y+dy)
        fr_polygon.append(Force(p1,dx,dy,forces[i][0].amount,scale)) 
        start = p1
        
    # resultant
    res_amount = fr_polygon[0].p2.distance(fr_polygon[-1].p1)/scale
    if round(float(res_amount),5) == 0:
        closed = True

    res_dx = fr_polygon[-1].p1.x
    res_dy = fr_polygon[-1].p1.y
    res_fr_polygon = Force(fr_polygon[-1].p1,res_dx,res_dy,res_amount,scale,True)
    
    if ax_fr_poly is not None:
        ax_fr_poly = plot_fr_poly(ax_fr_poly, closed, res_fr_polygon, fr_polygon)
    
    
    return ax_fr_poly, closed, res_fr_polygon, fr_polygon
        

def funicular_polygon(ax_fr_poly,ax_fun_poly,forces,system):
    
    ax_fr_poly, _, res_fr_poly, fr_poly = force_polygon(ax_fr_poly,system.scale,forces)
    
    ax_fr_poly.relim()
    
    x_min,x_max = ax_fr_poly.get_xlim()
    y_min,y_max = ax_fr_poly.get_ylim()
    pole = Point2D(x_min + 2*system.largest_amount*system.scale ,y_min + 0.5*(y_max-y_min))
    
    polelines = [Line2D(pole,fr_poly[0].p2)]
    ax_fr_poly = plot_poleline(ax_fr_poly,pole,polelines[0])
    
    #create baseline underneath system for beautiful plot
    baseline = Line2D(Point2D(0,-system.largest_element_length*0.2),Point2D(1,-system.largest_element_length*0.2)) 
    intersections = system.ex_forces_list[0][0].line.intersection(baseline)
    
    polelines[0] = translate_to_point(polelines[0],intersections[0])
       
    
    for i in range(len(forces)-1):
        line_i = Line2D(pole,fr_poly[i].p1)
        ax_fr_poly = plot_poleline(ax_fr_poly,pole,line_i)
        
        line_i = translate_to_point(line_i,intersections[-1])

        polelines.append(line_i)
        
        intersections.append(polelines[-1].intersection(forces[i+1][0].line)[0])
    
    last_line = Line2D(pole,fr_poly[-1].p1)
    ax_fr_poly = plot_poleline(ax_fr_poly,pole,last_line)
    
    last_line = translate_to_point(last_line,intersections[-1])
    
    polelines.append(last_line)
    
    intersections.append(polelines[-1].intersection(polelines[0])[0])
    
    res_fun_poly = res_fr_poly
    res_fun_poly.translate_head_to_point(intersections[-1])
    
    
    
    ax_fun_poly = plot_fun_poly(ax_fun_poly,res_fun_poly, polelines, intersections,system)
    
    return ax_fr_poly, ax_fun_poly, res_fun_poly
        

def method_of_joints(ax_method_of_joints,acting_forces,node_number,unknown_forces,system):

    #create lines for unknown members
    member_lines = []
    
    i = 0
    while i < system.n_nodes:
        if system.solved_geometry[node_number][i] != 0:
            for k in range(len(system.member_forces)): #find the force in member_forces
                      if system.member_forces [k][1] == [node_number,i] or system.member_forces [k][1] == [i,node_number] :
                          member_id = k
            
            second_node_number = i
            member_lines.append([Line2D(system.node_list[node_number][0],system.node_list[i][0]),member_id,second_node_number]) 
        
        else: #solved_geometry == 0 --> no member or has been calculated
            if system.geometry[node_number][i] == 1: # --> has been calculated
                  for k in range(len(system.member_forces)): #find the force in member_forces
                      if system.member_forces [k][1] == [node_number,i] or system.member_forces [k][1] == [i,node_number] :
                          member_force = system.member_forces[k][0]
                              
                          # set direction of force: + pointing from node, - pointing to node
                          delta_x_nodes = system.node_list[i][0].x-system.node_list[node_number][0].x
                          delta_y_nodes = system.node_list[i][0].y-system.node_list[node_number][0].y
                          
                          if np.sign(delta_x_nodes) == np.sign(member_force.dx) and np.sign(delta_y_nodes) == np.sign(member_force.dy) : #force points from node_number to node i
                              pass
                          else:
                              member_force.mirror_at_foodpoint()
                        
                          if member_force.amount < 0: 
                              member_force.mirror_at_foodpoint()
                              
                          member_force.translate_food_to_point(system.node_list[node_number][0])
                              
                          acting_forces.append([member_force,node_number,len(acting_forces)])
                          break 
                      
        i += 1
        
    #force polygon of all acting forces on node
    _,closed,res_fr_polygon,fr_polygon = force_polygon(None, system.scale,acting_forces)
    
    if unknown_forces == 0:
         if closed == False:
             print('Error: Node is not in equilibrium: Node',node_number)
    intersection = []
    
    if unknown_forces == 1:
        #unknwon_force = res fr_polygon, watch direction
        dx = res_fr_polygon.dx
        dy = res_fr_polygon.dy
        dx1 = member_lines[0][0].p2.x-member_lines[0][0].p1.x
        dy1 = member_lines[0][0].p2.y-member_lines[0][0].p1.y
            
        amount = res_fr_polygon.amount
            
        if np.sign(dx) == np.sign(dx1) or np.sign(dy) != np.sign(dy1): #set sign 
            amount = 0 - amount
           
        
        acting_point = system.node_list[node_number][0]
            
             
        member_force = [Force(acting_point,dx,dy,amount,system.scale,scaled = True)]
        
        system.member_forces[member_lines[0][1]][0] = member_force[0]
            
        system.solved_geometry[node_number][member_lines[0][2]] = 0
        system.solved_geometry[member_lines[0][2]][node_number] = 0
        
    
    elif unknown_forces == 2:
        
        member_lines[0][0] = translate_to_point(member_lines[0][0],fr_polygon[0].p2)
        member_lines[1][0] = translate_to_point(member_lines[1][0],fr_polygon[-1].p1)
        
        intersection = [member_lines[0][0].intersection(member_lines[1][0])[0]]
        
        member_force = [None]*2
        
        #member 0
        dx = fr_polygon[0].p2.x-intersection[0].x
        dy = fr_polygon[0].p2.y-intersection[0].y
        dx1 = member_lines[0][0].p1.x-member_lines[0][0].p2.x
            
        amount = fr_polygon[0].p2.distance(intersection[0])/system.scale
            
        if np.sign(dx) == np.sign(dx1): #set sign
            amount = amount * -1
          
            
         
        acting_point = Point2D(system.node_list[node_number][0].x,system.node_list[node_number][0].y)
            
        member_force[0] = Force(acting_point,dx,dy,amount,system.scale,scaled = True)
        
        system.member_forces[member_lines[0][1]][0] = member_force[0]
            
        system.solved_geometry[node_number][member_lines[0][2]] = 0
        system.solved_geometry[member_lines[0][2]][node_number] = 0
        
        #member 1
        dx = fr_polygon[-1].p1.x-intersection[0].x
        dy = fr_polygon[-1].p1.y-intersection[0].y
        dx1 = member_lines[1][0].p2.x-member_lines[1][0].p1.x
            
        amount = float(fr_polygon[-1].p1.distance(intersection[0])/system.scale)
            
        if np.sign(dx) == np.sign(dx1): #set sign
            amount = 0 - amount
           
        
        acting_point = Point2D(system.node_list[node_number][0].x+dx,system.node_list[node_number][0].y+dy)
            
             
        member_force[1] = Force(acting_point,dx,dy,amount,system.scale,scaled = True)
        
        system.member_forces[member_lines[1][1]][0] = member_force[1]
            
        system.solved_geometry[node_number][member_lines[1][2]] = 0
        system.solved_geometry[member_lines[1][2]][node_number] = 0  
        
    #plot
    ax_method_of_joints = plot_method_of_joints(ax_method_of_joints,system,closed,res_fr_polygon,fr_polygon,node_number,member_force,unknown_forces,member_lines,intersection)
   
        
    
    return ax_method_of_joints, system.solved_geometry #not necessary

def find_cuttingline(system):
    
    # create element_lines
    element_lines = []

    for i in range(len(system.member_forces)):
        element_lines.append(Segment2D(system.node_list[system.member_forces[i][1][0]][0], system.node_list[system.member_forces[i][1][1]][0]))
        
    for i in range(len(system.member_forces)):
        if system.member_forces[i][0] is None: #member force is unknown
            
            # get midpoint of member
            node_1 = element_lines[i].p1
            node_2 = element_lines[i].p2
            mid_x = 0.5 * (node_1.x+node_2.x)
            mid_y = 0.5 * (node_1.y+node_2.y)
            midpoint = Point2D(mid_x,mid_y)
            
            # create possible cutting lines
            cutting_lines = []
            for alpha in range(-20,21,10):
                alpha = np.radians(alpha)
                line_alpha = element_lines[i].perpendicular_line(midpoint)
                line_alpha = line_alpha.rotate(alpha,midpoint)
                if isinstance(line_alpha,Line2D) == False:
                    print('line_alpha is not a Line2D object')
                cutting_lines.append(line_alpha)
            
            # get number of intersections for each cutting line
          
            for line_number in range(len(cutting_lines)):
                intersected_elements = []

                for element_number in range(len(element_lines)):
                    if element_lines[element_number].intersection(cutting_lines[line_number]) != []:
                        intersected_elements.append(element_number)
                if len(intersected_elements) <= 3:
                    member_number = i
                    cuttingline = cutting_lines[line_number]
                    print('Cut through member %d with line %d' %(member_number,line_number))
                    
                    #plot
                    cutting_line_fig = plt.figure('cuttingline')
                    ax_cutting_line = cutting_line_fig.add_subplot(111)
                    
                    ax_cutting_line = plot_cutting_line(ax_cutting_line,system,cuttingline)
                    ax_cutting_line.axis('equal')
                    
                    return member_number,cuttingline,intersected_elements
        

def find_subsystem(cutted_member,cuttingline,intersected_elements,system):
    # find all nodes on one side of the cutting line
     new_node_list = []
     for i in range(len(system.node_list)):
        # cuttingline = mx + t
        m_cuttingline = (cuttingline.p2.y-cuttingline.p1.y)/(cuttingline.p2.x-cuttingline.p1.x)
        t_cuttingline = cuttingline.p1.y - m_cuttingline * cuttingline.p1.x
        x_value_line =  (system.node_list[i][0].y - t_cuttingline)/m_cuttingline # get x value of cuttingline for y value of node
        
# =============================================================================
#         # nicest solution would be to create new_json by deleting entries from original json
#         # then create subsystem = System(new_json)
#         
#         with open(system.json_name, "r") as old, open("to.json", "r") as to:
#             to_insert = json.load(old)
#             destination = json.load(to)
#             destination.append(to_insert) #The exact nature of this line varies. See below.
#         with open("to.json", "w") as to:
#             json.dump(to, destination)
# =============================================================================
       
        if system.node_list[i][0].x < x_value_line: # node is on leftside of cuttingline
            new_node_list.append(system.node_list[i])
        else:
            pass
    
     # find all ex_forces on nodes, including boundary conditions
     new_ex_forces_list = []
     for i in range(len(new_node_list)):
        for k in range(len(system.ex_forces_list)):
            if system.ex_forces_list[k][1] == new_node_list[i][1]:
                new_ex_forces_list.append(system.ex_forces_list[k])
        for k in range(len(system.reactions_x)):
            if system.reactions_x[k][1] == new_node_list[i][1] and round(float(system.reactions_x[k][0].amount),5) != 0:
                new_ex_forces_list.append(system.reactions_x[k]) # ToDo: set id
        for k in range(len(system.reactions_y)):
            if system.reactions_y[k][1] == new_node_list[i][1]and round(float(system.reactions_y[k][0].amount),5) != 0:
                new_ex_forces_list.append(system.reactions_y[k])
    
    
     return new_ex_forces_list, new_node_list
 
    
def calculate_subsystem_forces(ax_sect_fr_poly, ax_sect_fun_poly,intersected_elements,new_ex_forces_list,new_node_list,system):
   
    ax_sect_fr_poly, ax_sect_fun_poly, res_fun_poly = funicular_polygon(ax_sect_fr_poly,ax_sect_fun_poly,new_ex_forces_list,system)
        
    # create sub_member_forces
    # find nodes of element
    sub_member_forces =  []
    sub_member_lines = []
    for i in range(len(intersected_elements)):
         node1 = system.element_list[intersected_elements[i]][0][0] 
         node2 = system.element_list[intersected_elements[i]][0][1]
          
         # find the one node which is in the subsystem, new_node_list
         node = 0 
         for k in range(len(new_node_list)):
             if node1 == new_node_list[k][1]:
                 node = node1
                 sub_member_line = Line2D(system.node_list[node1][0],system.node_list[node2][0]) 
                 #defines line so, that line.p1 is node in our subsystem, line.p2 is outside the subsystem
             if node != node1: #node1 wasnt in new_node_list
                 node = node2
                 sub_member_line = Line2D(system.node_list[node2][0],system.node_list[node1][0])
       
         sub_member_forces.append([None,node,intersected_elements[i],i])
         sub_member_lines.append(sub_member_line)
     
        
    
    if len(intersected_elements) == 3: #must be 3 otherwise subsystems arent connected properly (statische bestimmtheit)
        point_of_action = res_fun_poly.line.intersection(sub_member_lines[0])[0] # intersection of R and first member force
        point2 = sub_member_lines[1].intersection(sub_member_lines[2])[0] # intersection of other two member forces
        line = Line2D(point_of_action,point2) # Res of other two member_forces must act on this line
        
        # Translate R to point_of_action
        res_fun_poly.translate_food_to_point(point_of_action)
        
        # Translate Line to head of R
        line = translate_to_point(line,res_fun_poly.p1)
        
        intersection = line.intersection(sub_member_lines[0])
        
        # sub_member_force[0]
        dx = res_fun_poly.p2.x-intersection[0].x
        dy = res_fun_poly.p2.y-intersection[0].y
        dx1 = sub_member_lines[0].p2.x-sub_member_lines[0].p1.x
            
        amount = float(res_fun_poly.p2.distance(intersection[0])/system.scale)
            
        if np.sign(dx) != np.sign(dx1): #set sign, True if sub_member_force[0] points in same direction as sub_member_lines[0] --> points away from node
            amount = 0 - amount
           
        acting_point = system.node_list[sub_member_forces[0][1]][0]
        sub_member_forces[0][0] = Force(acting_point,dx,dy,amount,system.scale,scaled = True)
        sub_member_forces[0][0].translate_food_to_point(acting_point)
        
        #Res of sub_member_force[1] and sub_member_force[2]
        dx = intersection[0].x-res_fun_poly.p1.x
        dy = intersection[0].y-res_fun_poly.p1.y
        dx1 = line.p2.x-line.p1.x
            
        amount = float(res_fun_poly.p1.distance(intersection[0])/system.scale)
            
        if np.sign(dx) != np.sign(dx1): #set sign
            amount = 0 - amount
           
        acting_point = point2
        res_12 = Force(acting_point,dx,dy,amount,system.scale,scaled = True)
        res_12.translate_food_to_point(acting_point)
        
        force1,force2 = res_12.resolve_on_lines(sub_member_lines[1],sub_member_lines[2])
        
        # set sign force1
        dx1 = sub_member_lines[1].p2.x-sub_member_lines[1].p1.x 
        amount = force1.amount
        if np.sign(force1.dx) != np.sign(dx1): #set sign
            amount = 0 - amount
            force1 = Force(force1.p1,force1.dx,force1.dy,amount,system.scale,scaled=True)
        
        #set sign force2
        dx2 = sub_member_lines[2].p2.x-sub_member_lines[2].p1.x 
        amount = force2.amount
        if np.sign(force2.dx) != np.sign(dx2): #set sign
            amount = 0 - amount
            force2 = Force(force2.p1,force2.dx,force2.dy,amount,system.scale,scaled=True)
            
        sub_member_forces[1][0] = force1
        sub_member_forces[2][0] = force2
        
    return sub_member_forces
            
def calculate_member_forces(ax_sub_fr_poly,ax_sub_fun_poly,fig_member_forces,system):
    while True:
        n_unsolved_nodes = 0 #reset to 0 before starting loop through all nodes
        steps_without_solving = 1 
        
        # go through rows = nodes
        for i in range(system.n_nodes): 
            # set_unknown_forces to 0 before continuing with next node
            n_unknown_forces = 0
            # check if node has been calculated yet
            if system.solved_geometry[i][-1] is False:
                # get number of unknown forces                      
                for j in range(system.n_columns_geometry):
                    if system.solved_geometry[i][j] != 0:
                        n_unknown_forces +=1
                # calculate unknown forces depending on number of unknown forces     
                if n_unknown_forces > 2:
                     # if more than two unknown forces go to next node and set unsolved_nodes +1 
                     n_unsolved_nodes +=1            
                elif n_unknown_forces == 2 or n_unknown_forces == 1 or n_unknown_forces == 0:
                    system.solved_geometry[i][-1] = True
                    acting_forces = system.get_acting_forces_on_node(i)
                    
                    
                    ax_fr_poly_node = fig_member_forces.add_subplot(system.n_nodes,2,i+1)
    
                    ax_fr_poly_node.set_title('Method of joints on node %s' %i)
                    
                    ax_fr_poly_node.axis('equal')
                    ax_fr_poly_node,system.solved_geometry = method_of_joints(ax_fr_poly_node,acting_forces,i,n_unknown_forces,system)
                    
                    ax_fr_poly_node.set_adjustable('box')
                    steps_without_solving = 0
                
                          
               
        if n_unsolved_nodes == 0: # loop ends if every node has been calculated
            break
        
        if steps_without_solving != 0 and n_unsolved_nodes != 0: # all nodes have been checked, some need to be calculated but couldnt
            print('method of joints cant solve system')
            print('go on with method of sections, this might take some time')
            
            # create subsystem and calculate 3 member_forces with fr_poly and fun_poly
            element_number,cutting_line,intersected_elements = find_cuttingline(system)
            new_ex_forces_list,new_node_list = find_subsystem(element_number,cutting_line,intersected_elements,system)
            
            sub_member_forces = calculate_subsystem_forces(ax_sub_fr_poly, ax_sub_fun_poly,intersected_elements,new_ex_forces_list,new_node_list,system)
             
            system.update_known_forces(sub_member_forces)
            
            
        
        plt.show()
    
    return ax_sub_fr_poly,ax_sub_fun_poly, fig_member_forces

def sort_clockwise(forces,node,system):
    angles = []
    for i in range(len(forces)):
        if type(forces[i][1]) == type([]): # is member_force
            node1 = system.node_list[forces[i][1][0]][0]
            node2 = system.node_list[forces[i][1][1]][0]
            if node1 == node:
                angle = calculate_angle(node2,node)
            else:
                angle = calculate_angle(node1,node)
        else: # is boundary or ex_force
            if round(float(forces[i][0].amount),5) < 0:
                forces[i][0].mirror_at_headpoint()
                angle = calculate_angle(forces[i][0].p2,node)
                forces[i][0].mirror_at_headpoint() # set back to how it was
            else:
                angle = calculate_angle(forces[i][0].p2,node)
        angles.append([angle,forces[i]])
        
            
    # sort forces by angle 
    sorted_forces = sorted(angles, key=lambda angles : angles[0])
    
    #eliminiate angle
    for i in range(len(sorted_forces)):
        sorted_forces[i] = sorted_forces[i][1]
    
    return sorted_forces

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

def cremona_plan(ax_cremona,system):
    # create list of all system forces, Flag tells if it was added to cremona plan
    all_forces_drawn = []
    for i in range(len(system.member_forces)):
        all_forces_drawn.append([system.member_forces[i],False])
    for i in range(len(system.ex_forces_list)):
        all_forces_drawn.append([system.ex_forces_list[i],False])
    for i in range(len(system.reactions_x)):
        all_forces_drawn.append([system.reactions_x[i],False])
    for i in range(len(system.reactions_y)):
        all_forces_drawn.append([system.reactions_y[i],False])
    
    # sort by id
    all_forces_drawn = sorted(all_forces_drawn, key=lambda all_forces_drawn : all_forces_drawn[0][2])
    
    cremona_plan = []
    # draw force_polygon of ex_forces and boundaries 
    first_step_forces = all_forces_drawn[len(system.member_forces):]
    
    #eliminate forces with amount 0
    list_of_nones = []
    for i in range(len(first_step_forces)):
        if round(float(first_step_forces[i][0][0].amount),5) == 0:
            list_of_nones.append(i)
        
    for i in range(len(list_of_nones)):
        first_step_forces.pop(list_of_nones[i])
    
    # sort forces from left to right
    sort_forces = []
    for i in range(len(first_step_forces)):
        x_coo = system.node_list[first_step_forces[i][0][1]][0].x
        sort_forces.append([x_coo,first_step_forces[i]])
    first_step_forces = sorted(sort_forces, key = lambda sort_forces : sort_forces[0])

    # eliminate boolean and x_coo as force_polygon needs list of forces
    for i in range(len(first_step_forces)):
        first_step_forces[i] = first_step_forces[i][1][0]
    
    #if two or more forces on one node use sort_clockwise
    for i in range(len(first_step_forces)):
         on_same_node = []
         for j in range(i,len(first_step_forces)):
            if first_step_forces[i][1] == first_step_forces[j][1]:
                on_same_node.append(first_step_forces[j])
         if len(on_same_node)>1:
            on_same_node = sort_clockwise(on_same_node,system.node_list[first_step_forces[i][1]][0],system)
            first_step_forces[i:i+len(on_same_node)]=on_same_node
        
    # create force_polygon
    _,closed,res_first_step,poly_first_step = force_polygon(None,system.scale,first_step_forces)
  
    
    # transform force_polygon to lines
    lines_first_fr_poly = []
    for i in range(len(poly_first_step)):
        lines_first_fr_poly.append([poly_first_step[i].line,first_step_forces[i][2]])
        cremona_plan.append(lines_first_fr_poly[-1])
        all_forces_drawn[first_step_forces[i][2]][1] = True
        

    # loop over all nodes
    for node_number in range(len(system.node_list)):
        node = system.node_list[node_number][0]
        # get all forces on node
        acting_forces = system.get_acting_forces_on_node(node_number)
        to_add = system.get_member_forces_on_node(node_number)
        for i in range(len(to_add)):
            acting_forces.append(to_add[i])
        
        # delete forces with amount = 0
        list_of_nones = []
        for i in range(len(acting_forces)):
            if round(float(acting_forces[i][0].amount),5) == 0:
                list_of_nones.append(i)
            
        for i in range(len(list_of_nones)):
            acting_forces.pop(list_of_nones[i])
        
        # sort forces clockwise to follow bow's notation
        sorted_forces = sort_clockwise(acting_forces,node,system)
        
        # reset directions depending on node and sign
        for i in range(len(acting_forces)):
             if type(acting_forces[i][1]) == type([]): # is member_force
                  # set direction of force: + pointing from node, - pointing to node
                  member_force = acting_forces[i][0]
                  node1_id = acting_forces[i][1][0]
                  node2_id = acting_forces[i][1][1]
                  if node2_id == node_number:
                      other_node_id = node1_id
                  else:
                      other_node_id = node2_id
                  delta_x_nodes = system.node_list[other_node_id][0].x-node.x
                  delta_y_nodes = system.node_list[other_node_id][0].y-node.y
                  
                  if np.sign(delta_x_nodes) == np.sign(member_force.dx) and np.sign(delta_y_nodes) == np.sign(member_force.dy) : #force points from node_number to node i
                      pass
                  else:
                      member_force.mirror_at_foodpoint()
                
                  if member_force.amount < 0: 
                      member_force.mirror_at_foodpoint()
                      
                  member_force.translate_food_to_point(system.node_list[node_number][0])
             else: # is boundary or ex_force
               pass # was set back in sort_clockwise so still in original direction
                 
            
        # create force_polygon on node
        _,closed,res_fr_poly,fr_poly = force_polygon(None,system.scale,sorted_forces)
        
        # transform force_polygon to lines
        lines_fr_poly = []
        for i in range(len(fr_poly)):
            lines_fr_poly.append([fr_poly[i].line,sorted_forces[i][2]])
            
        # translate force_polyogn to given place in cremona plan
        
        # get dx and dy
        # search force inside all_force_drawn to check if it has been drawn
        found_dx_dy = False
        for i in range(len(fr_poly)):
            force_id = sorted_forces[i][2]
            for j in range(len(all_forces_drawn)): # look for same id in drawn forces
                if all_forces_drawn[j][0][2] == force_id: 
                    # found force
                    if all_forces_drawn[j][1]: # check if it was drawn
                        # was drawn
                        # find in cremona_plan
                        for n in range(len(cremona_plan)):
                            if cremona_plan[n][1] == force_id:
                                equal_line = cremona_plan[n][0]    
                        # calculate translation
                        dx = equal_line.p1.x - lines_fr_poly[i][0].p1.x
                        dy = equal_line.p1.y - lines_fr_poly[i][0].p1.y
                        # check if p2s match
                        new_p2 = Point2D(lines_fr_poly[i][0].p2.x+dx,lines_fr_poly[i][0].p2.y+dy)
                        
                        if round(float(new_p2.x),5) != round(float(equal_line.p2.x),5) or round(float(new_p2.y),5) != round(float(equal_line.p2.y),5):
                            # dont match --> change dx and dy
                            dx = equal_line.p2.x - lines_fr_poly[i][0].p1.x
                            dy = equal_line.p2.y - lines_fr_poly[i][0].p1.y
                        
                        found_dx_dy = True
                    else: # wasnt drawn
                        break #check for next force
                    
            if found_dx_dy:
                break
       
        # translate all lines in lines_fr_poly and add to cremona_plan
        for i in range(len(lines_fr_poly)):
            cremona_plan.append([translate_delta(lines_fr_poly[i][0],dx,dy),lines_fr_poly[i][1]])
        
        # set True in all_forces_drawn
        for i in range(len(lines_fr_poly)):
            all_forces_drawn[lines_fr_poly[i][1]][1] = True
        
      
    ax_cremona = plot_cremona(ax_cremona,cremona_plan,lines_first_fr_poly)
        
    return ax_cremona
                            
                    
        
        


   