# class cremona_plan
from utilities.geometric_utilities import sort_left_to_right, sort_right_to_left, getSecond, right_left, TOL
from node2d import Node2D
from segment2d import Segment2D
from utilities.mechanical_utilities import sort_clockwise
from utilities.plot_cremona_plan import plot_cremona_plan
from utilities.plot_utilities import plot_computation_model
from numpy import sign
from math import sqrt
from utilities.cremona_utilities import preprocess_cremonaplan


class cremona_plan():
    def __init__(self, analysis):
        model = analysis.input_system["forces"]
        nodes = analysis.input_system["nodes"]
        sys_elements = analysis.input_system["elements"]
        bottom_or_top = analysis.input_system["bel_chord"]
    #    fixities = analysis.input_system['fixities']

        self.points = {}
        self.ex_forces = {}

        # i und j einander zuordnen
        str_i = []
        str_j = []
        el_id = []
        self.one_member = {}  # i und i
        self.at_member = {}  # member i oder member j
        for i in sys_elements:
            var1 = str(i) + 'i'
            var2 = str(i) + 'j'
            str_i.append(var1)
            str_j.append(var2)
            el_id.append(i)
        for i in range(len(str_i)):
            self.one_member[str_i[i]] = str_j[i]
            self.one_member[str_j[i]] = str_i[i]
            self.at_member[str_i[i]] = el_id[i]
            self.at_member[str_j[i]] = el_id[i]

        force_id = analysis.input_system["forces"].keys()
        str_keys = ""
        for i in force_id:
            str_keys = str_keys + str(i)

        # bei den ex_forces beginnt der Index bei 1!
        number_ex_forces = str_keys.count("e")
        number_reactions = str_keys.count("r")

        b = number_ex_forces + number_reactions

        # in versch Kräfte aufteilen
        ex_forces = dict(list(model.items())[:number_ex_forces])
        reactions = dict(list(model.items())[number_ex_forces: b])
        member_forces = dict(list(model.items())[b:])

        sorted_ex = sort_left_to_right(ex_forces, nodes)
        popped = []
        Hallo = []
        correct = 0
        # externe Kräfte am selben Knoten zusammenlegen
        for i in range(1, len(sorted_ex)):
            f1 = sorted_ex[i-1]
            f2 = str(sorted_ex[i])
            node1 = model[f1].node_id
            node2 = model[f2].node_id
            if node1 == node2:
                popped.append(f2)
                Hallo.append(i + correct)
                correct -= 1
                x_amount = ex_forces[f1].direction[0]*ex_forces[f1].magnitude + \
                    ex_forces[f2].direction[0]*ex_forces[f2].magnitude
                y_amount = ex_forces[f1].direction[1]*ex_forces[f1].magnitude + \
                    ex_forces[f2].direction[1]*ex_forces[f2].magnitude
                new_amount = sqrt((x_amount) * x_amount+(y_amount)*y_amount)
                model[f1].direction = [
                    x_amount/abs(x_amount), y_amount/abs(y_amount)]
                model[f1].magnitude = new_amount
                ex_forces[f1].direction = [
                    x_amount/new_amount, y_amount/new_amount]
                ex_forces[f1].magnitude = new_amount
                forces = nodes[node2].forces
                pop_point = None
                for j in range(len(forces)):
                    if f2 == forces[j]:
                        pop_point = j
                forces.pop(pop_point)

        analysis.input_system["forces"] = model

    #    sorted_ex = sorted_ex_2

        for i in range(0, len(popped)):
            model.pop(popped[i])
            ex_forces.pop(popped[i])
        for i in range(len(Hallo)):
            sorted_ex.pop(Hallo[i])

        sorted_reactions = sort_right_to_left(reactions, nodes)
        sorted_member_forces = sort_left_to_right(member_forces, nodes)
        print(sorted_member_forces)

    #    model['14i'].direction = [0.7071067811865476, -0.7071067811865476]+
    #    model['14j'].direction = [-0.7071067811865476, 0.7071067811865476]
    #    model['15i'].direction = [0.658504607868518, -0.7525766947068778]
    #    model['15j'].direction = [-0.658504607868518, 0.7525766947068778]

    #    model['16i'].direction = [-0.7071067811865476, -0.7071067811865476]
    #    model['16j'].direction = [0.7071067811865476, 0.7071067811865476]

        # Lasten für sort_clockwise richtig einordnen
        x_real = []
        y_real = []
        for i in ex_forces:
            x = model[i].direction[0]
            y = model[i].direction[1]
            x_real.append(x)
            y_real.append(y)

            if bottom_or_top == 'top':
                # y-Koordinate muss positiv sein
                if y < 0:
                    model[i].direction[0] = -x
                    model[i].direction[1] = abs(y)

            if bottom_or_top == 'bottom':
                # y_koordinate muss negativ sein
                if y > 0:
                    model[i].direction[0] = -x
                    model[i].direction[1] = -y

        # Kräfte an Knoten sortieren
        for i in nodes:
            sort_forces = []
            force_at_node = nodes[i].forces
            for j in range(len(force_at_node)):
                sort_forces.append(model[force_at_node[j]])
            sorted_forces = sort_clockwise(sort_forces, bottom_or_top)
            nodes[i].forces = sorted_forces

    #    'nodes[2].forces = ['e2', '2i', '15i', '11i', '1j']
    #    nodes[1].forces = ['e1', '1i', '14i', '10i', '0j']
    #    nodes[4].forces = ['e4', '4i', '13i', '3j']
    #    nodes[3].forces =  ['e3', '3i', '16i', '12i', '2j']'
    #    model['14j'].direction = [0.7071067811865476, -0.7071067811865476]

        # Externe Lasten wieder 'richtig' einspeichern
        count = 0
        for i in ex_forces:
            model[i].direction[0] = x_real[count]
            model[i].direction[1] = y_real[count]
            count = count + 1

        # Externe Lasten in Cremonaplan "speichern/zeichnen"

        points = [Node2D(0, [0, 0])]
        start = Node2D(0, [0, 0])
        elements = []
        a = 1
        node_id = [0]

        for i in sorted_ex:
            force = ex_forces[i]
            start.forces.append(i)

            x_amount = start.coordinates[0] + \
                force.magnitude*force.direction[0]
            y_amount = start.coordinates[1] + \
                force.magnitude*force.direction[1]
            start = Node2D(a, [x_amount, y_amount])
            start.forces.append(i)
            # Punkte der externen Last als Fix setzen
            start.is_constrain = True

            points.append(start)
            node_id.append(a)
            element = Segment2D(a-1, [points[a-1], points[a]])
            elements.append(element)
            a = a + 1

        self.points = dict(zip(node_id, points))
        for i in self.points:
            self.ex_forces = dict(zip(sorted_ex, elements))

        elements = []

        # reactions "zeichnen/speichern"
        already_done = []
        for i in sorted_reactions:
            already_done.append(i)
            force = reactions[i]
            start.forces.append(i)

            x = force.direction[0]
            y = force.direction[1]

            x_amount = start.coordinates[0] + force.magnitude*x
            y_amount = start.coordinates[1] + force.magnitude*y
            start = Node2D(a, [x_amount, y_amount])

            start.forces.append(i)
            # Knoten AL-Kräfte fest setzen
            start.is_constrain = True

            points.append(start)
            node_id.append(a)
            element = Segment2D(a-1, [points[a-1], points[a]])
            elements.append(element)
            a = a + 1

        self.points = dict(zip(node_id, points))
        self.reactions = dict(zip(sorted_reactions, elements))

        elements = []
        members = []
        self.members = {}

        for i in sorted_ex:
            # weitere forces an dem Knoten "einzeichnen"
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
                            points.append(start)
                            node_id.append(a)
                            a = a + 1

                        else:
                            change = 0

                    if start != None:
                        if other_forces[j] not in already_done:
                            force = model[str(other_forces[j])]
                            start.forces.append(other_forces[j])

                            x_amount = start.coordinates[0] + \
                                force.magnitude*force.direction[0]
                            y_amount = start.coordinates[1] + \
                                force.magnitude*force.direction[1]

                            start = Node2D(a, [x_amount, y_amount])
                            start.forces.append(other_forces[j])

                            points.append(start)
                            node_id.append(a)
                            element = Segment2D(a-1, [points[a-1], points[a]])
                            elements.append(element)
                            members.append(other_forces[j])
                            already_done.append(other_forces[j])
                            a = a + 1

        self.points = dict(zip(node_id, points))
        for i in self.points:
            self.members = dict(zip(members, elements))

        # Elemente nach type aufteilen,
        type_forces = []
        for i in range(len(sorted_member_forces)):
            watch_force = model[sorted_member_forces[i]]
            type_force = sys_elements[self.at_member[watch_force.id]].opt_type
            print('watch', watch_force.id,'type',type_force)
            type_forces.append(type_force)

        force_id = sorted_member_forces
        sorted_members = dict(
            sorted(zip(force_id, type_forces), key=getSecond))
        bel_chord = {}
        unbel_chord = {}
        Verbindung = {}

        # andere Elemente löschen
        for i in sorted_members:
            if sorted_members[i] == 1:
                bel_chord[i] = model[i]

        for i in sorted_members:
            if sorted_members[i] == 2:
                unbel_chord[i] = model[i]

        for i in sorted_members:
            if sorted_members[i] == 3:
                Verbindung[i] = model[i]

        print('bel', bel_chord, 'un',unbel_chord, 'VEr',Verbindung)

        # member unbel_chord einfügen

        # sort unbel_chord
        nodes_unbel = []
        force_id = []
        for i in unbel_chord:
            coo_node = nodes[unbel_chord[i].node_id].coordinates
            nodes_unbel.append(coo_node)
            force_id.append(i)
        multiply = []
        if bottom_or_top == 'top':
            multiply.append(1)
        if bottom_or_top == 'bottom':
            multiply.append(-1)
        for i in self.ex_forces:
            y = self.ex_forces[i].y[1]-self.ex_forces[i].y[0]
            if y > 0:
                multiply.append(1)
                break
            if y < 0:
                multiply.append(-1)
                break
    #    if model[force_id[0]].direction[0]>=0:
    #        multiply.append(1)
    #    else:
    #        multiply.append(-1)

        sorted_unbel_chord = dict(sorted(zip(force_id, nodes_unbel)))

        # start bestimmen
        points.pop(-1)
        if model[sorted_reactions[0]].node_id == model[sorted_reactions[1]].node_id:
            start = self.reactions[sorted_reactions[1]].nodes[1]
        else:
            start = self.reactions[sorted_reactions[0]].nodes[1]
        points.append(start)
        a = a
        hin = 1
        # member einzeichnen
        for i in sorted_unbel_chord:
            force = unbel_chord[i]

            start.forces.append(i)

            x_amount = start.coordinates[0] + force.magnitude * \
                abs(force.direction[0])*multiply[0]*multiply[1]*hin
            mirrored = abs(force.direction[0]) * \
                multiply[0]*multiply[1]*hin*force.magnitude

            if sign(mirrored) == sign(force.direction[0]):
                direction = force.direction[1]
            else:
                direction = -force.direction[1]

            y_amount = start.coordinates[1] + force.magnitude*direction

            start = Node2D(a, [x_amount, y_amount])
            start.forces.append(i)
            hin = hin * (-1)

            points.append(start)
            node_id.append(a)
            element = Segment2D(a-1, [points[a-1], points[a]])
            elements.append(element)
            members.append(i)
            already_done.append(i)
            #  members.append(sorted_unbel_chord[i])
            #  already_done.append(sorted_unbel_chord[i])
            a = a + 1

        self.points = dict(zip(node_id, points))
        self.members = dict(zip(members, elements))

        # remove dubbelpoints
    #    print('points', self.points.items(),'\n','ex_forces', self.ex_forces, '\n', 'reactions',self.reactions,'\n', 'members', self.members)
        # first value "save as" second value "save from" b
        same_point = [[0, 0]]
        # sort the points
        for i in self.points:
            x = self.points[i].coordinates[0]
            y = self.points[i].coordinates[1]
         #    print('id',self.points[i].id,[x,y])
            change = 0

            for j in range(len(same_point)):

                x_coo = self.points[same_point[j][0]].coordinates[0]
                y_coo = self.points[same_point[j][0]].coordinates[1]

            #    print('middle',self.points[8].forces)
                if x_coo - TOL <= x <= x_coo + TOL and y_coo - TOL <= y <= y_coo + TOL:
                    same_point.append([same_point[j][0], i])
                    change = 1
                    break
                    # dann pop points[i] und speicher Kräfte an dem Punkt coordinates[j]
            if change == 0:
                same_point.append([i, i])
                # sonst append points[i]
        # remove them
        for i in range(len(same_point)):
            stay = same_point[i][0]
            remove = same_point[i][1]

            if remove != stay:
                for c in range(len(self.points[remove].forces)):
                    if self.points[remove].forces[c] not in self.points[stay].forces:
                        self.points[stay].forces.append(
                            self.points[remove].forces[c])

                for j in self.ex_forces:
                    n1 = self.ex_forces[j].nodes[0].id
                    n2 = self.ex_forces[j].nodes[1].id

                    if remove == n1:
                        self.ex_forces[j].nodes[0] = self.points[stay]
                    if remove == n2:
                        self.ex_forces[j].nodes[1] = self.points[stay]

                for j in self.reactions:
                    n1 = self.reactions[j].nodes[0].id
                    n2 = self.reactions[j].nodes[1].id

                    if remove == n1:
                        self.reactions[j].nodes[0] = self.points[stay]
                    if remove == n2:
                        self.reactions[j].nodes[1] = self.points[stay]

                for j in self.members:
                    n1 = self.members[j].nodes[0].id
                    n2 = self.members[j].nodes[1].id

                    if remove == n1:
                        self.members[j].nodes[0] = self.points[stay]
                        n1 = self.members[j].nodes[0].id

                    if remove == n2:
                        self.members[j].nodes[1] = self.points[stay]
                        n2 = self.members[j].nodes[1].id

                self.points.pop(remove)

    #    print('8i',self.members['8i'].nodes[0].id,self.members['8i'].nodes[1].id)
    #    print('check_forces', self.points[1].forces,self.points[2].forces,self.points[3].forces,self.points[4].forces)
    #    for i in self.points:
    #        print(i,self.points[i].forces)
    #    print('segment_check')
    #    for i in self.ex_forces:
    #        print(i,self.ex_forces[i].nodes[0].id,self.ex_forces[i].nodes[1].id)
    #    for i in self.reactions:
    #        print(i,self.reactions[i].nodes[0].id,self.reactions[i].nodes[1].id)
    #    for i in self.members:
    #        print(i,self.members[i].nodes[0].id,self.members[i].nodes[1].id)

        plot_cremona_plan(self)

        # process Cremonaplan

        self, self.bel_chord, self.unbel_chord, self.Verbindung, model, nodes, elements = preprocess_cremonaplan(
            self, bel_chord, unbel_chord, Verbindung, model, nodes, sys_elements, bottom_or_top)
        # input-system aktualisieren und Cremonaplan plotten
        plot_cremona_plan(self)

        analysis.computation_model["forces"] = analysis.input_system['forces']
        analysis.computation_model["nodes"] = nodes
        analysis.computation_model["elements"] = elements
