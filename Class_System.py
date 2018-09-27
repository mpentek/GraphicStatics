# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:01:55 2018

@author: Benedikt
"""
import json
import copy
from sympy import Point2D
from Class_Force import Force
from functions import funicular_polygon


class System():
    def __init__(self,json_name):
        self.json_name = json_name
        self.import_from_json()
        self.n_nodes = len(self.node_list)
        self.create_geometry_matrix()        
        self.create_solved_geometry_matrix()
        self.n_columns_geometry = len(self.geometry[0])
        self.create_member_forces()
        
        
       
    
    def import_from_json(self):

        with open(self.json_name) as f:
            self.data = json.load(f)  
        
        # get node_list:
        nodes = self.data['nodes']
        self.node_list = []
        for i in range(len(nodes)):
            self.node_list.append([Point2D(nodes[i]['x-coordinate'],nodes[i]['y-coordinate']),nodes[i]['id']])
                    
        # get elements:
        elements = self.data['elements']
        self.element_list = []
        for i in range(len(elements)):
            self.element_list.append([elements[i]['connectivity'],elements[i]['id']])
        self.n_members = len(self.element_list)
        
        # get external forces:
        ex_forces = self.data['external_forces']
        self.ex_forces_list = []
        for i in range(len(ex_forces)):
            node_id = ex_forces[i]['node_id']
            acting_point = self.node_list[node_id][0]
            force_i = Force(acting_point,ex_forces[i]['components'][0],ex_forces[i]['components'][1],ex_forces[i]['amount'])
            self.ex_forces_list.append([force_i,node_id,ex_forces[i]['id']+self.n_members-1])
    
        # get boundary_conditions:
        boundary = self.data['boundary_conditions']
        self.boundary_list = []
        counter = 0
        for i in range(len(boundary)):
            self.boundary_list.append([boundary[i]['fixity'][0],False,boundary[i]['applied_onto_node'],counter+self.n_members+len(self.ex_forces_list)])
            counter +=1
            self.boundary_list.append([False,boundary[i]['fixity'][1],boundary[i]['applied_onto_node'],counter+self.n_members+len(self.ex_forces_list)])
            counter +=1

        # get scale
        amount_list = []
        for i in range(len(self.ex_forces_list)):
            amount_list.append(self.ex_forces_list[i][0].amount)
        self.largest_amount = max(amount_list)
        
        element_length_list =[]
        for i in range(len(self.element_list)):
            element_length_list.append(self.node_list[self.element_list[i][0][0]][0].distance(self.node_list[self.element_list[i][0][1]][0]))
        self.largest_element_length = max(element_length_list)
        
        self.scale = 0.5 * self.largest_element_length / self.largest_amount
        
        # change scale in ex_forces_list
        for i in range(len(self.ex_forces_list)):
            self.ex_forces_list[i][0].change_scale(self.scale)
            
        
    def create_geometry_matrix(self):
        self.len_geometry = len(self.node_list)
        self.geometry = [[0]*(self.len_geometry+4) for i in range(self.len_geometry)]
     
        
        # add members
        for i in range(len(self.element_list)):
            a,b = self.element_list[i][0]
            self.geometry[a][b] = 1
            self.geometry[b][a] = 1
        
        #add external forces
        for i in range(len(self.ex_forces_list)):
            node = self.ex_forces_list[i][1]
            id = self.ex_forces_list[i][2]
            self.geometry[node][self.len_geometry] = id
            
        # add boundary
        for i in range(len(self.boundary_list)):
            for j in range(len(self.boundary_list[0])):
                if self.boundary_list[i][j] is True:
                    node = self.boundary_list[i][2]
                    id = self.boundary_list[i][3]
                    self.geometry[node][self.len_geometry+1+j] = id
                    
        
        # add solved = False
        for i in range(self.len_geometry):
            self.geometry[i][-1] = False
                        
    def create_solved_geometry_matrix(self):
        self.solved_geometry = copy.deepcopy(self.geometry)
        for i in range(self.n_nodes):
            self.solved_geometry[i][self.n_nodes]=0 #all forces are known
                               
    def create_member_forces(self):
        self.member_forces = []
        for i in range(len(self.element_list)):
            self.member_forces.append([None,self.element_list[i][0],self.element_list[i][1]])
            
    
    def calculate_reactions(self, ax_fr_poly, ax_fun_poly):
        
        nodes_y = []
        nodes_x = []
       
        #get number of reactions from boundary_list
        for i in range(len(self.boundary_list)):
            if self.boundary_list[i][0]:
                nodes_y.append(self.boundary_list[i][2])
            if self.boundary_list[i][1]:
                nodes_x.append(self.boundary_list[i][2])
               
        self.n_reactions_x = len(nodes_x)
        
        ax_fr_poly, ax_fun_poly, res_fun_poly = funicular_polygon(ax_fr_poly, ax_fun_poly, self.ex_forces_list,self) 
        
        #horizontal reaction 
        self.reactions_x = []
        
        if self.n_reactions_x == 1:
            node_number = nodes_x[0]
            node = self.node_list[node_number][0]
            dx = -res_fun_poly.dx
            dy = 0
            if [dx,dy] == [0,0]:
                amount = 0
                x_force = Force(node,dx,dy,amount,self.scale,scaled = True)
                self.reactions_x.append([x_force,node_number,self.boundary_list[1][3]])
            else:
                amount = (res_fun_poly.p2.x-res_fun_poly.p1.x)/self.scale
                x_force = Force(node,dx,dy,amount,self.scale,scaled = True)
                self.reactions_x.append([x_force,node_number,self.boundary_list[1][3]])
            
        elif self.n_reactions_x == 2:
            for i in range(2):
                node_i = self.node_list[nodes_x[i]][0]
                dx = -res_fun_poly.dx*0.5
                dy = 0
                if [dx,dy] == [0,0]:
                    self.n_reactions_x -= 1
                else:
                    amount = (res_fun_poly.p2.x-res_fun_poly.p1.x)/self.scale*0.5
                    self.reactions_x.append([Force(node_i,dx,dy,amount,scaled = True),nodes_x[i],self.boundary_list[1+2*i][3]])
                  
        
        #vertical reactions by inverse_proportion
        self.reactions_y = [] 
        
        res_fun_poly_y = res_fun_poly.get_y_component()
        
        [y_force1, y_force2] = res_fun_poly_y.inverse_proportion(self.node_list[nodes_y[0]][0:-1][0],self.node_list[nodes_y[1]][0:-1][0],res_fun_poly.line)
        
        y_force1.get_opponent_force()
        y_force2.get_opponent_force()
        
        self.reactions_y.append([y_force1,self.boundary_list[0][2],self.boundary_list[0][3]]) 
        self.reactions_y.append([y_force2,self.boundary_list[2][2],self.boundary_list[2][3]])
        
        # update solved_geometry
        for i in range(self.n_nodes):
            self.solved_geometry[i][self.n_nodes+1]=0 #all vertical reactions are known
            self.solved_geometry[i][self.n_nodes+2]=0 #all horizontal reactions are known
        return ax_fr_poly,ax_fun_poly
            
    
    def get_acting_forces_on_node(self,node_number):
       
        #add forces and reactions to node_forces
        acting_forces = []
        force_lines = []
        i = 0
        while i < 3:
            if self.geometry[node_number][self.n_nodes+i] != 0:
                
                if i == 0: # get ex_forces
                    for j in range(len(self.ex_forces_list)):
                        if self.ex_forces_list[j][1] == node_number and round(float(self.ex_forces_list[j][0].amount),5) != 0:
                            acting_forces.append(self.ex_forces_list[j])
                            force_lines.append(acting_forces[-1][0].line)
                
                elif i == 1: # get reactions_y
                    if len(self.reactions_y) == 0:
                        break
                    else:
                        for j in range(len(self.reactions_y)):
                            if self.reactions_y[j][1] == node_number and round(float(self.reactions_y[j][0].amount),5) != 0:
                                acting_forces.append(self.reactions_y[j])
                                force_lines.append(acting_forces[-1][0].line)
                        
                elif i == 2: # get reactions_x
                    if len(self.reactions_x) == 0:
                        break
                    else:
                        for j in range(len(self.reactions_x)):
                            if self.reactions_x[j][1] == node_number and round(float(self.reactions_x[j][0].amount),5) != 0:
                                acting_forces.append(self.reactions_x[j])
                                force_lines.append(acting_forces[-1][0].line)
            i += 1
        
        return acting_forces
    
    def get_member_forces_on_node(self,node_number):
        node_member_forces = []
        for i in range(self.n_members):
            if self.member_forces[i][1][0] == node_number or self.member_forces[i][1][1] == node_number:
                node_member_forces.append(self.member_forces[i])
        return node_member_forces
        
    def update_known_forces(self,new_forces):
        for i in range(len(new_forces)):
            self.member_forces[new_forces[i][2]][0]=new_forces[i][0]
            node1_id = self.member_forces[new_forces[i][2]][1][0]
            node2_id = self.member_forces[new_forces[i][2]][1][1]
            
            self.solved_geometry[node1_id][node2_id] = 0
            self.solved_geometry[node2_id][node1_id] = 0
    
        

