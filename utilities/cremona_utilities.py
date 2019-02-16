#cremona utilities
from entitites.segment2d import update
#remove diagonals 
def preprocess_cremonaplan(Cremona_plan,bel_chord,Verbindung,model,nodes):
    print('members',Cremona_plan.members)
    low_diagonals = get_low_diagonals(Cremona_plan,bel_chord,Verbindung,model,nodes)
    Cremona_plan,bel_chord,Verbindung,model,nodes = remove_diagonals(low_diagonals,Cremona_plan,bel_chord,Verbindung,model,nodes)


    return Cremona_plan,bel_chord,Verbindung,model,nodes

def get_low_diagonals(Cremona_plan,bel_chord,Verbindung,model,nodes):
    print('bel_chord',bel_chord)
    print('model',model)
    mini = []
    a = 1 #da sonst jeder Knoten doppelt
    for i in bel_chord:
        if a < 0:
            a = a * (-1)
        else :
            a = a * (-1)
            dev = []
            node = bel_chord[i].node_id
            print('node',node)
            forces = nodes[node].forces
            #aus forces deviations suchen
            for i in range(len(forces)):
                if forces[i] in Verbindung:
                    dev.append(forces[i])
            print(dev)
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
    print(mini)
    return  mini

def remove_diagonals(low_diagonals,Cremona_plan,bel_chord,Verbindung,model,nodes):
    for i in low_diagonals:
    #aus Cremonaplan entfernen:
        force = model[i]
        if i in Cremona_plan.members:
            Segment = Cremona_plan.members[i]
            #Endpunkte Segment zusammenlegen
            n1 = Segment.nodes[0]
            n2 = Segment.nodes[1]
            forces1 = Cremona_plan.points[n1.id].forces
            forces2 = Cremona_plan.points[n2.id].forces
            if n1 == n2:
                #nur Diagonale löschen nicht Punkt!!
                 Verbindung.pop(i)
                 for j in range(len(forces1)):
                    update(Cremona_plan.members[forces1[j]])
                    if i == forces1[j]:
                     popped = j
                 forces1.pop(popped)
            
                 Cremona_plan.points[n1.id].forces = forces1
                 Cremona_plan.members.pop(i)
            else:

                print('n1',n1.id,'n2',n2.id)
                Cremona_plan.points[n1.id].coordinates = Segment.midpoint
                print('forces1',forces1,'forces2',forces2)
                for j in range(len(forces2)):
                    if forces2[j] not in forces1:
                        forces1.append(forces2[j])
                    if n2 == Cremona_plan.members[forces2[j]].nodes[0]:
                        print('Segment nodes',Cremona_plan.members[forces2[j]].nodes[0].id,Cremona_plan.members[forces2[j]].nodes[1].id)
                        Cremona_plan.members[forces2[j]].nodes[0] = n1
                        print('S nodes after',Cremona_plan.members[forces2[j]].nodes[0].id,Cremona_plan.members[forces2[j]].nodes[1].id)
                    if n2 == Cremona_plan.members[forces2[j]].nodes[1]:
                        print('Segment nodes',Cremona_plan.members[forces2[j]].nodes[0].id,Cremona_plan.members[forces2[j]].nodes[1].id)
                        Cremona_plan.members[forces2[j]].nodes[1] = n1
                        print('S nodes after', Cremona_plan.members[forces2[j]].nodes[0].id,Cremona_plan.members[forces2[j]].nodes[1].id)
                print('f1 after', forces1)
                #aus Cremona_plan löschen:
                Verbindung.pop(i)
                for j in range(len(forces1)):
                    update(Cremona_plan.members[forces1[j]])
                    if i == forces1[j]:
                        popped = j
                forces1.pop(popped)
                
                Cremona_plan.points[n1.id].forces = forces1
                Cremona_plan.members.pop(i)
                Cremona_plan.points.pop(n2.id)
                print('f1',forces1)
    return Cremona_plan,bel_chord,Verbindung,model,nodes


    #neue Steigung der angrenzenden Kräfte bestimmen
    #Steigung im Cremona und System anpassen
    #aus Elementen entfernen
    #aus System entfernen:
    #aus model(elements) entfernen 
    #aus nodes entfernen


    


