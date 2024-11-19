import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class Ant:
    def __init__(self, idx):
        self.idx = idx
        self.room = 'Sv'
    

class Room:
    def __init__(self, idx, name, contains=[], capacity=1):
        self.idx = idx
        self.name = name
        self.contains = contains
        self.capacity = capacity


def read_anthill_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    num_ants = int(lines[0].split('=')[1].strip())
    ants = []

    for i in range(num_ants):
        ant = Ant(f"f{i+1}")
        ants.append(ant)
        
    Rooms=[]
    room=Room(0,'Sv',ants,capacity=0)
    Rooms.append(room)
    
    
    tunnels = []
    
    for line in lines[1:]:
        line = line.strip()
        if line.startswith("S"):
            if "{" in line:
                room, capacity = line.split("{")
                room = room.strip()
                capacity = int(capacity.replace("}", "").strip())
                room=Room(len(Rooms),room,capacity=capacity)
                Rooms.append(room)
            elif " - " in line:
                start, end = line.split(" - ")
                tunnels.append((start.strip(), end.strip()))
            else:
                #rooms[line] = 1
                room=Room(len(Rooms),line,capacity=1)
                Rooms.append(room)
    room=Room(len(Rooms),'Sd',capacity=num_ants)
    Rooms.append(room)
    
    return num_ants,ants ,Rooms, tunnels

# Lecture du fichier et création du graphe
file_path = 'Fourmis/fourmiliere_cinq.txt'
num_ants,ants, Rooms, tunnels = read_anthill_file(file_path)
rooms=[]
for i in Rooms:
    nam=i.name
    cap=i.capacity
    rooms.append(f"{nam} : {cap}")
print(f"Nombre de fourmis : {num_ants}")
print(f"Salles : {rooms}")
print(f"Tunnels : {tunnels}")
for y in Rooms:
    if y.name=='Sv':
        print(len(y.contains))
def create_anthill_graph(Rooms, tunnels):
    G = nx.Graph()
    for i in Rooms:
        G.add_node(i.name, capacity=i.capacity)
    G.add_edges_from(tunnels)
    return G

# Créer le graphe
G = create_anthill_graph(Rooms, tunnels)

# Dessiner le graphe
nx.draw(G, with_labels=True, node_color='lightblue', node_size=800, font_size=10)
plt.title("Fourmilière - Représentation graphique")
plt.show()

# Créer une matrice d'adjacence à partir du graphe
adj_matrix = nx.to_numpy_array(G, nodelist=list(G.nodes))
node_list = list(G.nodes)


def simulate_ant_movement_with_adjacency_matrix(G, adj_matrix, node_list, num_ants, ants, Rooms):
    """
    Simulate the movement of ants from the vestibule (Sv) to the dormitory (Sd) using an adjacency matrix.
    """
    steps = []
    
    previous_rooms = {f'f{i+1}': None for i in range(num_ants)}
    rooms_capacity = nx.get_node_attributes(G, 'capacity')
    
    # Set unlimited capacity for the dormitory (Sd)
    rooms_capacity['Sd'] = float('inf')
    
    # Initialize lists for each room to track the ants inside them
    room_ants = {room.name: [] for room in Rooms}
    for ant in ants:
        room_ants[ant.room].append(ant)

    while any(ant.room != 'Sd' for ant in ants):
        step = []

        # Try to move ants already in intermediate rooms towards the exit (Sd) first
        for current_room in node_list:
            if current_room == 'Sd':
                continue

            # Get the index of the current room
            current_index = node_list.index(current_room)

            # Iterate over ants in the current room
            for ant in list(room_ants[current_room]):
                antname = ant.idx

                # Try to move directly to 'Sd' if possible
                sd_index = node_list.index('Sd')
                if adj_matrix[current_index, sd_index] == 1 and rooms_capacity['Sd'] > 0:
                    # Move the ant to 'Sd'
                    room_ants[current_room].remove(ant)
                    room_ants['Sd'].append(ant)
                    ant.room = 'Sd'
                    rooms_capacity[current_room] += 1
                    step.append(f"{antname} - {current_room} -> Sd")
                    continue

                # Look for an adjacent room with available capacity
                moved = False
                for neighbor_index in range(len(node_list)):
                    if adj_matrix[current_index, neighbor_index] == 1:  # Check adjacency
                        neighbor_room = node_list[neighbor_index]

                        # Skip if it's the previous room
                        if neighbor_room == previous_rooms[ant.idx]:
                            continue

                        # Check if the adjacent room has capacity
                        if rooms_capacity.get(neighbor_room, 1) > 0:
                            # Move the ant to the adjacent room
                            previous_rooms[ant.idx] = current_room
                            room_ants[current_room].remove(ant)
                            room_ants[neighbor_room].append(ant)
                            ant.room = neighbor_room
                            rooms_capacity[current_room] += 1
                            rooms_capacity[neighbor_room] -= 1
                            step.append(f"{antname} - {current_room} -> {neighbor_room}")
                            moved = True
                            break

                
        # Finally, try to move ants from 'Sv' if space is available
        for ant in list(room_ants['Sv']):
            antname = ant.idx
            current_room = 'Sv'
            
            # Get the index of 'Sv'
            current_index = node_list.index(current_room)

            # Look for an adjacent room with available capacity
            for neighbor_index in range(len(node_list)):
                if adj_matrix[current_index, neighbor_index] == 1:
                    neighbor_room = node_list[neighbor_index]

                    # Check if the adjacent room has capacity
                    if rooms_capacity.get(neighbor_room, 1) > 0:
                        previous_rooms[ant.idx] = current_room
                        room_ants['Sv'].remove(ant)
                        room_ants[neighbor_room].append(ant)
                        ant.room = neighbor_room
                        rooms_capacity[neighbor_room] -= 1
                        step.append(f"{antname} - {current_room} -> {neighbor_room}")
                        break
            

        # Record steps if any moves were made
        if step:
            #print(step)
            for room_name, ants_in_room in room_ants.items():
                for room in Rooms:
                    if room.name == room_name:
            # Update the 'contains' attribute with the current list of ants
                        room.contains = ants_in_room

            
            steps.append(step)
    
    return steps




# Exécuter la simulation
steps = simulate_ant_movement_with_adjacency_matrix(G, adj_matrix, node_list, num_ants,ants,Rooms)

# Afficher les étapes
for i, step in enumerate(steps):
    print(f"+++ E +++ {i+1}")
    for move in step:
        print(move)
    print()

def visualize_steps(G, steps):
    pos = nx.spring_layout(G)
    for i, step in enumerate(steps):
        plt.figure()
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=800, font_size=8)
        plt.title(f"Étape {i+1}")
        for move in step:
            
            ant, path = move.split(" - ")
            start, end = path.split(" -> ")
            plt.text(pos[end][0], pos[end][1], ant, fontsize=12, ha='left')
            for room in Rooms:
                
                if room.name==end:
                    contain=len(room.contains)
        plt.annotate(contain, xy=(pos[end][0],pos[end][1]), xytext=(0, 20), textcoords='offset points', bbox=dict(boxstyle="round", fc="red"))
        plt.pause(1.5)
        plt.show()

visualize_steps(G, steps)
for room in Rooms:
    print(room.name,len(room.contains))
