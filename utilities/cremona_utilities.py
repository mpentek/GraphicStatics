#cremona utilities
from entitites.segment2d import update
from utilities.geometric_utilities import get_magnitude_and_direction
from utilities.plo_cremona_plan import plot_cremona_plan
#remove diagonals 
def preprocess_cremonaplan(Cremona_plan,bel_chord,unbel_chord,Verbindung,model,nodes,elements):
    Cremona_plan, bel_chord =  set_force_bel_chord(Cremona_plan,bel_chord, model,nodes)
    low_diagonals = get_low_diagonals(Cremona_plan,bel_chord,Verbindung,model,nodes)
    Cremona_plan,bel_chord,Verbindung,model,nodes = remove_diagonals_from_cremona(low_diagonals,Cremona_plan,bel_chord,Verbindung,model,nodes)
    Cremona_plan,bel_chord,unbel_chord,Verbindung,model,nodes,elements = remove_diagonals_from_system(low_diagonals,Cremona_plan,bel_chord,unbel_chord,Verbindung,model,nodes,elements)
    return Cremona_plan,bel_chord,unbel_chord,Verbindung,model,nodes,elements

#Für optimiertes System Kräfte in einem Chord konstant, hier bel_chord
def set_force_bel_chord(cremona,bel_chord, model,nodes):
    #Kräfte auf bestimmte Länge setzen
    new_amount = 100 #ToDO: später eventuell Nutzereingabe
    for i in bel_chord:
        #Kraft anpassen
        magnitude = bel_chord[i].magnitude
        bel_chord[i].magnitude = new_amount * (magnitude/abs(magnitude))
        #member anpassen
        #bestimmen welcher Punkt verschoben werden soll
        if i in cremona.members:
            start = cremona.members[i].nodes[0]
            if start.is_constrain == True:
                end = cremona.members[i].nodes[1]
                #Marker setzen (wird später bei entfernen der Diagonalen benötigt)
                end.is_constrain = 'mem'
            else:
                end = start
                start = cremona.members[i].nodes[1]
                bel_chord[i].magnitude = - bel_chord[i].magnitude # damit Punkt nicht in falsche Richtung verschoben wird
        #Marker setzen (wird später bei entfernen der Diagonalen benötigt)
            end.is_constrain = 'mem'       
        #neue Endkoordinaten bestimmen
            end_new_x = start.coordinates[0] + bel_chord[i].direction[0] * bel_chord[i].magnitude
            end_new_y = start.coordinates[1] + bel_chord[i].direction[1] * bel_chord[i].magnitude
            end.coordinates = [end_new_x,end_new_y]
    #Steigungen und Längen der angrenzenden Segmente anpassen
    for i in cremona.members:
        update(cremona.members[i])
    plot_cremona_plan(cremona)
           
        

    return cremona, bel_chord


def get_low_diagonals(Cremona_plan,bel_chord,Verbindung,model,nodes):
    mini = []
    a = 1 #da sonst jeder Knoten doppelt
    for i in bel_chord:
        if a < 0:
            a = a * (-1)
        else :
            a = a * (-1)
            dev = []
            node = bel_chord[i].node_id
            forces = nodes[node].forces
            #aus forces deviations suchen
            for i in range(len(forces)):
                if forces[i] in Verbindung:
                    dev.append(forces[i])
            #alle bis auf die größte am Knoten müssen später gelöscht werden
            if len(dev) > 1:
                größte = dev[0]
                for j in range(len(dev)):
                    if abs(model[dev[j]].magnitude)  < abs(model[größte].magnitude):
                        mini.append(dev[j])
                        mini.append(Cremona_plan.one_member[dev[j]])
                    if abs(model[dev[j]].magnitude)  > abs(model[größte].magnitude):
                        mini.append(größte)
                        mini.append(Cremona_plan.one_member[größte])
                        größte = dev[j]
    #            mini = sorted1[0]
    #           mini2 = Cremona_plan.one_member[mini]
    #           node2 = model[mini2].node_id
    #           forces2 = nodes[node2].forces
    #           #aus System löschen
    #           model.pop(mini)
    #           model.pop(mini2)
    #           #aus nodes löschen
    #           print('forces',forces,'forces2',forces2)
    #           for j in range(len(forces)):
    #             if mini == forces[j]:
    #                 nodes[node].forces.pop(j)
    #                 break
    #           for j in range(len(forces2)):
    #             if mini == forces2[j]:
    #                 nodes[node2].forces.pop(j)
    #                 break

    # print('model_after',model)
    # print('forces',nodes[node].forces,'forces2',nodes[node2].forces)
    return  mini

def remove_diagonals_from_cremona(low_diagonals,Cremona_plan,bel_chord,Verbindung,model,nodes):
    for i in low_diagonals:
        print(i)
    #aus Cremonaplan entfernen:
        if i in Cremona_plan.members:
            Segment = Cremona_plan.members[i]
            #Endpunkte Segment zusammenlegen
            n1 = Segment.nodes[0]
            n2 = Segment.nodes[1]
            forces1 = Cremona_plan.points[n1.id].forces
            forces2 = Cremona_plan.points[n2.id].forces
            #Diagonale gleich 0
            if n1 == n2:
                #nur Diagonale löschen nicht Punkt!!
                 for j in range(len(forces1)):
                    update(Cremona_plan.members[forces1[j]])
                    if i == forces1[j]:
                     popped = j
                 forces1.pop(popped)
            
                 Cremona_plan.points[n1.id].forces = forces1
                 Cremona_plan.members.pop(i)
            #Diagonale ungleich 0
            else:
                p1 = Cremona_plan.points[n1.id]
                p2 = Cremona_plan.points[n2.id]
                #Punkt der nicht an bel_chord angeschlossen ist löschen
                #dazu Kräfte an anderen Punkt hängen
                if p1.is_constrain == 'mem':
                    for c in range(len(p2.forces)):
                         p1.forces.append(p2.forces[c])
                    n1 = p1
                    n2 = p2
                    print('Version a')
                else:
                     if p2.is_constrain == 'mem':
                          for c in range(len(p1.forces)):
                             p2.forces.append(p1.forces[c])
                          n1 = p2
                          n2 = p1
                          print('Version b')
                
                #Wenn beide Punkte nicht an bel_chord angeschlossen sind im Mittel zusammenlegen
                     else:
                         Cremona_plan.points[n1.id].coordinates = Segment.midpoint
                         for c in range(len(p2.forces)):
                            p1.forces.append(p2.forces[c])
                         n1 = p1
                         n2 = p2
                         print('Version c')
                #zu löschender Knoten aus Segmenten entfernen

                for j in range(len(n2.forces)):
                    if n2 == Cremona_plan.members[n2.forces[j]].nodes[0]:
                        Cremona_plan.members[n2.forces[j]].nodes[0] = n1
                    if n2 == Cremona_plan.members[n2.forces[j]].nodes[1]:
                        Cremona_plan.members[n2.forces[j]].nodes[1] = n1
    
                #aus Cremona_plan löschen:
                for j in range(len(forces1)):
                    update(Cremona_plan.members[forces1[j]])
                    if i == forces1[j]:
                        popped = j
                forces1.pop(popped)
                
                # Cremona_plan.points[n1.id].forces = forces1
                Cremona_plan.members.pop(i)
                Cremona_plan.points.pop(n2.id)
    return Cremona_plan,bel_chord,Verbindung,model,nodes

#aus System entfernen:
def remove_diagonals_from_system(low_diagonals,Cremona_plan,bel_chord,unbel_chord,Verbindung,model,nodes,elements):
    for i in low_diagonals:
        node = model[i].node_id
        forces = nodes[node].forces
        for j in range(len(forces)):
            if i == forces[j]:
                popped =  j
        forces.pop(popped)
        model.pop(i)
        id_element = Cremona_plan.at_member[i]
        if id_element in elements:
            elements.pop(id_element)
        Verbindung.pop(i)
        Cremona_plan.one_member.pop(i)
        Cremona_plan.at_member.pop(i)

    #Steigungen aktualisieren
    for i in bel_chord:
        if i in Cremona_plan.members:
            x = Cremona_plan.members[i].x[1] - Cremona_plan.members[i].x[0]
            y = Cremona_plan.members[i].y[1] - Cremona_plan.members[i].y[0]
        else:
            var = Cremona_plan.one_member[i]
            x = - Cremona_plan.members[var].x[1] + Cremona_plan.members[var].x[0]
            y = - Cremona_plan.members[var].y[1] + Cremona_plan.members[var].y[0]
        components = [x,y]
        bel_chord[i].magnitude, bel_chord[i].direction = get_magnitude_and_direction(
            components)
        model[i].magnitude, model[i].direction = get_magnitude_and_direction(
            components)
    for i in unbel_chord:
         x = Cremona_plan.members[i].x[1] - Cremona_plan.members[i].x[0]
         y = Cremona_plan.members[i].y[1] - Cremona_plan.members[i].y[0]
         components = [x,y]
         unbel_chord[i].magnitude, unbel_chord[i].direction = get_magnitude_and_direction(
            components)
         model[i].magnitude, model[i].direction = get_magnitude_and_direction(
            components)
    # for i in Verbindung:
    #     if i in Cremona_plan.members:
    #          x = Cremona_plan.members[i].x[1] - Cremona_plan.members[i].x[0]
    #          y = Cremona_plan.members[i].y[1] - Cremona_plan.members[i].y[0]
    #     else:
    #         var = Cremona_plan.one_member[i]
    #         x = - Cremona_plan.members[var].x[1] + Cremona_plan.members[var].x[0]
    #         y = - Cremona_plan.members[var].y[1] + Cremona_plan.members[var].y[0]
    #     components = [x,y]
    #     Verbindung[i].magnitude, Verbindung[i].direction = get_magnitude_and_direction(
    #         components)
    #     model[i].magnitude, model[i].direction = get_magnitude_and_direction(
    #         components)
        
    return Cremona_plan,bel_chord,unbel_chord,Verbindung,model,nodes,elements


    


