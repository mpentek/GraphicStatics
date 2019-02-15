#cremona utilities

#remove diagonals 
def preprocess_cremonaplan(Cremona_plan,bel_chord,Verbindung,model,nodes):
    low_diagonals = get_low_diagonals(Cremona_plan,bel_chord,Verbindung,model,nodes)

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


