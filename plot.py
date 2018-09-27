# -*- coding: utf-8 -*-
"""
Created on Thu May 31 14:55:42 2018

@author: Benedikt
"""
from matplotlib.lines import Line2D as plt_line2D
import matplotlib.patches as patches
from sympy import Segment2D
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

def plot_force(force,ax_force,color):
        
        if round(force.amount,5) != 0:
            line = plt_line2D([force.p1.x,force.p2.x],[force.p1.y,force.p2.y],linewidth = 0)
            ax_force.add_line(line) 
            ax_force.arrow(force.p2.x, force.p2.y, force.dx, force.dy,zorder = 2, color = str(color), length_includes_head=True, head_width=0.5, head_length=0.5)
            ax_force.autoscale()
           
        return ax_force

def plot_system(ax_system,system):
    
    # add Elements
    for i in range(len(system.element_list)):
        x = [system.node_list[system.element_list[i][0][0]][0].x,system.node_list[system.element_list[i][0][1]][0].x]
        y = [system.node_list[system.element_list[i][0][0]][0].y,system.node_list[system.element_list[i][0][1]][0].y]
        line = plt_line2D(x,y)
        
        # add elementnumbers: empty rectangle filled with text in center
        element_segment = Segment2D(system.node_list[system.member_forces[i][1][0]][0],system.node_list[system.member_forces[i][1][1]][0])
        dx = element_segment.p2.x-element_segment.p1.x
        dy = element_segment.p2.y-element_segment.p1.y
        
        width = element_segment.length
        height = system.largest_element_length*0.25
        if dy == 0:
            angle = 0
            # choose point with smaller x-coordinate as xy
            if element_segment.p1.x < element_segment.p2.x:
                xy = [element_segment.p1.x,element_segment.p1.y]
            else:
                xy = [element_segment.p2.x,element_segment.p2.y]
            
            center_text = [element_segment.p1.x+0.5*dx,element_segment.p1.y]
                
        elif dx == 0:
            angle = 90
            # choose node with smaller y-coordinate as xy
            if element_segment.p1.y < element_segment.p2.y:
                xy = [element_segment.p1.x,element_segment.p1.y]
            else:
                xy = [element_segment.p2.x,element_segment.p2.y]
                
            center_text = [element_segment.p1.x,element_segment.p1.y+0.5*dy] # was element_segment.p1.x-0.5*height
        else:
            # calculate angle
            
            angle = np.degrees(np.arctan(float(dy/dx)))
            # choose node at lower left
            if angle < 0:
                angle = angle + 360
            if (angle > 0) and (angle < 180):
                xy = [element_segment.p1.x,element_segment.p1.y]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)
            elif angle > 180 and angle <= 270:
                xy = [element_segment.p2.x,element_segment.p2.y]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)
            elif angle > 270:
                xy = [element_segment.p1.x,element_segment.p1.y]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)
            
        patch = patches.Rectangle(xy, width, height, angle, ec=(0,0,0,0), fc=(1,0,0,0))      
        
        
        
        ax_system.add_patch(patch)
        ax_system.annotate('S %d' %i,(center_text[0],center_text[1]))
        
        ax_system.add_line(line)
        
    
    
        
    # add joints
    for i in range(len(system.node_list)):
        ax_system.plot(system.node_list[i][0].x,system.node_list[i][0].y,'ko')
        ax_system.annotate(str(system.node_list[i][1]),[system.node_list[i][0].x,system.node_list[i][0].y],)
        
    # add ex_forces
    for i in range(len(system.ex_forces_list)):
        ax_system = plot_force(system.ex_forces_list[i][0],ax_system,'r')
        ax_system.annotate('F %s = %s kN'% (system.ex_forces_list[i][2],system.ex_forces_list[i][0].amount),[system.ex_forces_list[i][0].p2.x,system.ex_forces_list[i][0].p2.y])
    
    # add boundary conditions
    for i in range(len(system.boundary_list)):
        # ToDo: find way to plot ALR
        
        
        if system.boundary_list[i][0] is True:
            #ax_system.plot(system.node_list[system.boundary_list[i][2]][0].x,system.node_list[system.boundary_list[i][2]][0].y,'r^')
            point = system.node_list[system.boundary_list[i][2]][0]
            dx = 0.07*system.largest_amount*system.scale
            dy = dx*1.5
            x = [point.x, point.x+dx, point.x-dx]
            y = [point.y, point.y-dy, point.y-dy]
            xy = np.array([x,y])
            xy = np.transpose(xy)
            patch = patches.Polygon(xy, color = 'r')
            ax_system.add_patch(patch)
        if system.boundary_list[i][1] is True:
            #ax_system.plot(system.node_list[system.boundary_list[i][2]][0].x,system.node_list[system.boundary_list[i][2]][0].y,'r>')
            point = system.node_list[system.boundary_list[i][2]][0]
            dy = 0.07*system.largest_amount*system.scale
            dx = dy*1.5
            x = [point.x, point.x-dx, point.x-dx]
            y = [point.y, point.y+dy, point.y-dy]
            xy = np.array([x,y])
            xy = np.transpose(xy)
            patch = patches.Polygon(xy, color = 'r')
            ax_system.add_patch(patch)
    # set axis
    ax_system.axis('equal')
    return ax_system


def plot_fr_poly(ax_fr_poly,closed, res_fr_polygon, fr_polygon):
    
    for i in range(len(fr_polygon)):
        ax_fr_poly = plot_force(fr_polygon[i],ax_fr_poly,'b')
    
    if closed is not True:
        ax_fr_poly = plot_force(res_fr_polygon,ax_fr_poly,'r')
    
    return ax_fr_poly

def plot_poleline(ax_poleline,pole,poleline):
    from functions import extend_line
    
    # add pole
    ax_poleline.plot(pole.x,pole.y,'ko')
    
    # get boundaries of axis
    [x_min,x_max] = ax_poleline.get_xlim()
    [y_min,y_max] = ax_poleline.get_ylim()
    
    x = [poleline.p1.x,poleline.p2.x]
    y = [poleline.p1.y,poleline.p2.y]
    
    x,y = extend_line(x,y,x_min,x_max,y_min,y_max) 
    
    line = plt_line2D(x,y)
    line.set_color('k')
    line.set_linestyle('--')
    ax_poleline.add_line(line)
        
    return ax_poleline

def plot_fun_poly(ax_fun_poly,res_fun_poly, polelines, intersections,system):
    from functions import extend_line    
   
    # add system to plot
    # add Elements
    for i in range(len(system.element_list)):
        x = [system.node_list[system.element_list[i][0][0]][0].x,system.node_list[system.element_list[i][0][1]][0].x]
        y = [system.node_list[system.element_list[i][0][0]][0].y,system.node_list[system.element_list[i][0][1]][0].y]
        line = plt_line2D(x,y,color=(0,0,0,0.5))
        ax_fun_poly.add_line(line)
    # add ex_forces
    for i in range(len(system.ex_forces_list)):
        ax_fun_poly = plot_force(system.ex_forces_list[i][0],ax_fun_poly,'k')
            
    # add intersections to plot    
    for i in range(len(intersections)):
        ax_fun_poly.plot(intersections[i].x,intersections[i].y, 'ko')
    
    # get boundaries of axis
    [x_min,x_max] = ax_fun_poly.get_xlim()
    [y_min,y_max] = ax_fun_poly.get_ylim()
    
    
    # add forcelines
    for i in range(len(system.ex_forces_list)):
        x = [system.ex_forces_list[i][0].p1.x,system.ex_forces_list[i][0].p2.x]
        y = [system.ex_forces_list[i][0].p1.y,system.ex_forces_list[i][0].p2.y]
        
        x,y = extend_line(x,y,x_min,x_max,y_min,y_max)    
      
        force_line = plt_line2D(x,y)
        force_line.set_color('r')
        force_line.set_linestyle('--')
        ax_fun_poly.add_line(force_line)

    # add lines ongoing to boundaries
    for i in range(len(polelines)):
        x = [polelines[i].p1.x,polelines[i].p2.x]
        y = [polelines[i].p1.y,polelines[i].p2.y]
        
        x,y = extend_line(x,y,x_min,x_max,y_min,y_max) 
        
        line = plt_line2D(x,y)
        line.set_color('k')
        line.set_linestyle('--')
        ax_fun_poly.add_line(line)
        
    

    # add resultant
    ax_fun_poly= plot_force(res_fun_poly,ax_fun_poly,'r')
            
    return ax_fun_poly

def plot_method_of_joints(ax_method_of_joints,system,closed,res_fr_polygon,fr_polygon,node_number,member_force,unknown_forces,member_lines,intersection):
    
    from functions import extend_line
    
    # plot known forces
    for i in range(len(fr_polygon)):
        ax_method_of_joints = plot_force(fr_polygon[i],ax_method_of_joints,'b')
    
    # plot intersection points
    points = []
    points.append(fr_polygon[0].p2)
    points.append(fr_polygon[-1].p1)    
    if len(intersection) != 0:
        points.append(intersection)
    
    for i in range(len(points)):
        ax_method_of_joints.plot(points[i].x,points[i].y,'ko')
    
    # plot member lines
    [x_min,x_max] = ax_method_of_joints.get_xlim()
    [y_min,y_max] = ax_method_of_joints.get_ylim()
    for i in range(0,unknown_forces):
        if round(float(member_force[i].amount),5) != 0:
            line = member_lines[i][0]
            
            x = [line.p1.x,line.p2.x]
            y = [line.p1.y,line.p2.y]
            x,y = extend_line(x,y,x_min,x_max,y_min,y_max)
            
            line = plt_line2D(x,y)
            line.set_color('r')
            line.set_linestyle('--')
            ax_method_of_joints.add_line(line)
        
    # plot member forces
    if unknown_forces == 1:
        member_force[0].translate_head_to_point(fr_polygon[0].p2)
        ax_method_of_joints = plot_force(member_force[0],ax_method_of_joints,'r')
        
    if unknown_forces == 2:
        #member force[0]
        member_force[0].translate_head_to_point(fr_polygon[0].p2)
        
        # set direction of force: 
        delta_x_nodes = fr_polygon[0].p2.x-intersection.x
        delta_y_nodes = fr_polygon[0].p2.y-intersection.y
          
        if np.sign(delta_x_nodes) == np.sign(member_force[0].dx) and np.sign(delta_y_nodes) == np.sign(member_force[0].dy) : #force points from fr_polygon[0] to intersection
            pass
        else:
            member_force[0].mirror_at_foodpoint()
                    
        ax_method_of_joints = plot_force(member_force[0],ax_method_of_joints,'r')
        
        #member force[1]
        member_force[1].translate_food_to_point(fr_polygon[-1].p1)
        
        # set direction of force: 
        delta_x_nodes = round(float(intersection.x-fr_polygon[-1].p1.x),5)
        delta_y_nodes = round(float(intersection.y-fr_polygon[-1].p1.y),5)
          
        if np.sign(delta_x_nodes) == np.sign(round(float(member_force[0].dx),5)) and np.sign(delta_y_nodes) == np.sign(round(float(member_force[0].dy),5)) : #force points from fr_polygon[0] to intersection
            pass
        else:
            member_force[0].mirror_at_foodpoint()
       
        ax_method_of_joints = plot_force(member_force[1],ax_method_of_joints,'r')
    
    return ax_method_of_joints

def plot_results(ax_results,system):
    for i in range(len(system.element_list)):
        
        # add Rectangles and Elementnumbers
        element_segment = Segment2D(system.node_list[system.member_forces[i][1][0]][0],system.node_list[system.member_forces[i][1][1]][0])
        dx = element_segment.p2.x-element_segment.p1.x
        dy = element_segment.p2.y-element_segment.p1.y
        
        width = element_segment.length
        height = system.largest_element_length*0.25
        if dy == 0:
            angle = 0
            # choose point with smaller x-coordinate as xy
            if element_segment.p1.x < element_segment.p2.x:
                xy = [element_segment.p1.x,element_segment.p1.y]
            else:
                xy = [element_segment.p2.x,element_segment.p2.y]
            
            center_text = [element_segment.p1.x+0.5*dx,element_segment.p1.y]
                
        elif dx == 0:
            angle = 90
            # choose node with smaller y-coordinate as xy
            if element_segment.p1.y < element_segment.p2.y:
                xy = [element_segment.p1.x,element_segment.p1.y]
            else:
                xy = [element_segment.p2.x,element_segment.p2.y]
                
            center_text = [element_segment.p1.x,element_segment.p1.y+0.5*dy]
        else:
            # calculate angle
            
            angle = np.degrees(np.arctan(float(dy/dx)))
            # choose node at lower left
            if angle < 0:
                angle = angle + 360
            if (angle > 0) and (angle < 180):
                xy = [element_segment.p1.x,element_segment.p1.y]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)
            elif angle > 180 and angle <= 270:
                xy = [element_segment.p2.x,element_segment.p2.y]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)
            elif angle > 270:
                xy = [element_segment.p1.x,element_segment.p1.y]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)
            
        if round(float(system.member_forces[i][0].amount),5) == 0:
             center = element_segment.midpoint
             radius = 0.05 * element_segment.length
             
             patch = patches.Circle(center,radius,ec=(0,0,0,0.9), fc=(1,0,0,0.25))
             
             
        elif round(float(system.member_forces[i][0].amount),5) > 0:
            height = round(float(system.member_forces[i][0].amount),5)*system.scale*0.1
            
            patch = patches.Rectangle(xy, width, height, angle, ec=(0,0,0,0.9), fc=(0,0,1,0.5))     
        
        elif round(float(system.member_forces[i][0].amount),5) < 0:
            height = round(float(system.member_forces[i][0].amount),5)*system.scale*0.1
            
            patch = patches.Rectangle(xy, width, height, angle, ec=(0,0,0,0.9), fc=(1,0,0,0.5))  
        
        
        
        ax_results.add_patch(patch)
        ax_results.annotate('S %d' %i,(center_text[0],center_text[1]))

            
    # add Elements
    for i in range(len(system.element_list)):
        x = [system.node_list[system.element_list[i][0][0]][0].x,system.node_list[system.element_list[i][0][1]][0].x]
        y = [system.node_list[system.element_list[i][0][0]][0].y,system.node_list[system.element_list[i][0][1]][0].y]
        line = plt_line2D(x,y)
        line.set_color('k')
        ax_results.add_line(line)
        
    # add joints
    for i in range(len(system.node_list)):
        ax_results.plot(system.node_list[i][0].x,system.node_list[i][0].y,'ko')
        ax_results.annotate(str(system.node_list[i][1]),[system.node_list[i][0].x,system.node_list[i][0].y],)
    
    # create string with results and add to rectangle
    results_list = []
    for i in range(len(system.member_forces)):
        results_list.append('S %d = %.2f kN \n' %(i,system.member_forces[i][0].amount))
    results_str = ''.join(results_list)
           
    xy = [ax_results.get_xlim()[1],ax_results.get_ylim()[0]]
    height = ax_results.get_ylim()[1]-ax_results.get_ylim()[0]
    width = 5
    
    patch_results = patches.Rectangle(xy,width,height, ec=(0,0,0,0), fc=(1,0,0,0))
    ax_results.add_patch(patch_results)
    
    ax_results.annotate(results_str,(patch_results.xy[0]+1,patch_results.xy[1]+1))
    
    
    #add title
    ax_results.set_title('Results')
   
    return ax_results

def plot_cremona(ax_cremona,cremona_plan,first_step_poly_lines):
  
    for i in range(len(cremona_plan)):
        x = [cremona_plan[i][0].p1.x,cremona_plan[i][0].p2.x]
        y = [cremona_plan[i][0].p1.y,cremona_plan[i][0].p2.y]
        line = plt_line2D(x,y)
        line.set_color('k')
        ax_cremona.add_line(line)
        
    for i in range(len(first_step_poly_lines)):
        x = [first_step_poly_lines[i][0].p1.x,first_step_poly_lines[i][0].p2.x]
        y = [first_step_poly_lines[i][0].p1.y,first_step_poly_lines[i][0].p2.y]
        line = plt_line2D(x,y)
        line.set_color('r')
        ax_cremona.add_line(line)

    return ax_cremona


def safe_to_pdf(figures,name):
    name = name + '.pdf'
    with PdfPages(name) as pdf:
        for i in range(len(figures)):
            pdf.savefig(figures[i])
    return

def plot_cutting_line(ax_cutting_line, system, cuttingline):
    from functions import extend_line 
    
    # add Elements
    for i in range(len(system.element_list)):
        x = [system.node_list[system.element_list[i][0][0]][0].x,system.node_list[system.element_list[i][0][1]][0].x]
        y = [system.node_list[system.element_list[i][0][0]][0].y,system.node_list[system.element_list[i][0][1]][0].y]
        line = plt_line2D(x,y)
        line.set_color('k')
        ax_cutting_line.add_line(line)
        
    # add joints
    for i in range(len(system.node_list)):
        ax_cutting_line.plot(system.node_list[i][0].x,system.node_list[i][0].y,'ko')
        ax_cutting_line.annotate(str(system.node_list[i][1]),[system.node_list[i][0].x,system.node_list[i][0].y],)
 
           
    
    # add cuttinglines
    # get boundaries of axi
    [x_min,x_max] = [10,30]
    [y_min,y_max] = [-10,20]

        
    x = [cuttingline.p1.x,cuttingline.p2.x]
    y = [cuttingline.p1.y,cuttingline.p2.y]

    x,y = extend_line(x,y,x_min,x_max,y_min,y_max) 

    line = plt_line2D(x,y)
    line.set_color('r')
    ax_cutting_line.add_line(line)
        
    return ax_cutting_line

        