

"""Example client."""
import asyncio
import getpass
import json
import os
import random
import websockets
from tree_search import *
from snake import *
import math
import colorama
import time
import sys

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def adjacent_to_snake(food, sight, size):
    for i in range(-1, 2):
        for j in range(-1, 2):
            x = (food[0] + i) % size[0]
            y = (food[1] + j) % size[1]
            if str(x) in sight and str(y) in sight[str(x)] and sight[str(x)][str(y)] == 4:
                return True
    return False




async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
 
        solution_path = []
        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                
                print(
                    state
                )  # print the state, you can use this to further process the game state
                
                t1 = time.time()
                # Print the value associated with the key 'food'
                key = ""
                if 'map' in state:
                    size = state['size']
                    original_map = state['map']
                    original_map_copy = [row.copy() for row in original_map]
                    

                    food_position = [[x, y] for x in range(size[0]) for y in range(size[1]) if original_map[x][y] == 2]
                    super_FOOD = []

                    time_total = 0
                    
                    for food in food_position:
                        original_map[food[0]][food[1]] = 0

                    matrix_map = [row.copy() for row in original_map]
                    solution_path = []
                    
                    marked_places = []

                    multiplayer = False
                    count_steps = 0


                

                if 'sight' in state:
                    
                    
                    sight = state['sight']
                    body = state['body'] 
                    head = state['body'][0]
                    traverse = state['traverse']
                    sight_range = state['range']
                    steps = state['step']

                    
                    #print("\nSight: ", sight)

                    
                    
                    farthest_point = None
                    l_all_coords = []
                    l_points = []
                    closest_coords = []
                    
                    t3 = time.time()
                    temp_matrix = [row.copy() for row in matrix_map]
                    count_steps += 1
                    if count_steps == 200:
                        multiplayer = False

                    for x in sight.keys():
                        for y in sight[x].keys():
                            x = int(x)
                            y = int(y)

                            if [x, y] in body:
                                sight[str(x)][str(y)] = 0

                            
                            if sight[str(x)][str(y)] == 4:
                                multiplayer = True
                                count_steps = 0
                            '''
                            if temp_matrix[int(x)][int(y)] == 'X' or temp_matrix[int(x)][int(y)] == 1:
                                continue
                            '''
                            
                            if traverse == False:
                                    #quero que se a comida estiver no outro lado do mapa, como o mapa nao é rotativo, ignore a comida
                                    dx = abs(x - head[0])
                                    dy = abs(y - head[1])

                                    if dx > sight_range + 1 or dy > sight_range + 1:
                                        continue

                            distance = manhattan_distance([x, y], head)

                            

                            if matrix_map[x][y] == 0:
                                
                                matrix_map[x][y] = 'X'

                                marked_places.append([x, y])
                                if len(marked_places) > 700:
                                    
                                    marked = marked_places.pop(0)
                                    matrix_map[marked[0]][marked[1]] = 0

                                 
                                #discovered_points = get_discovered_points(temp_matrix, x, y, sight_range, size, head, body[1])
                                
                                discovered_points = 0
                                for i in range(-(sight_range + 1), sight_range + 2):
                                    xi = (int(x) + i) % size[0]

                                    if i == -(sight_range + 1) or i == sight_range + 2 or i == 0:
                                        yj = int(y)
                                    else:
                                        yj = (int(y) + sight_range) % size[1]

                                    
                                    if temp_matrix[xi][yj] == 'X':  
                                        discovered_points += 1
                                
            
                                if [x, y] not in body and (sight[str(x)][str(y)] != 1 if traverse == False else True):
                                    l_points += [[x, y, discovered_points, distance]]

                            
                            if distance == 1 and sight[str(x)][str(y)] != 4 and (sight[str(x)][str(y)] != 1 if traverse == False else True):
                                body_parts = 0
                                checked_pos = {}
                                # Check for surrounding body parts
                                for i in range(-1, 2):
                                    for j in range(-1, 2):
                                        xi = (x + i) % size[0]
                                        yj = (y + j) % size[1]
                                        
                                        if str(xi) in sight and str(yj) in sight[str(xi)] and (xi, yj) not in checked_pos:
                                            cell = sight[str(xi)][str(yj)]
                                            if cell == 4 or (cell == 1 if traverse == False else False):
                                                body_parts += 1
                                                
                                                # Check surrounding positions of this cell
                                                nested_body_parts = 0
                                                for ni in range(-1, 2):
                                                    for nj in range(-1, 2):
                                                        nxi = (xi + ni) % size[0]
                                                        nyj = (yj + nj) % size[1]

                                                        if str(nxi) in sight and str(nyj) in sight[str(nxi)] and (nxi, nyj) not in checked_pos:
                                                            nested_cell = sight[str(nxi)][str(nyj)]
                                                            if nested_cell == 4 or (nested_cell == 1 if traverse == False else False):
                                                                nested_body_parts += 1
                                                    
                                                        checked_pos[(nxi, nyj)] = nested_body_parts
                                                                
                                                # Add nested body parts to the main count
                                                body_parts += nested_body_parts
                                                checked_pos[(xi, yj)] = body_parts

                                closest_coords.append([x, y, body_parts])

                            l_all_coords += [[x, y, distance] if sight[str(x)][str(y)] == 0 else [x, y, float('inf')]]
                            
                                
                            # or sight[x][y] == 3
                            
                            if sight[str(x)][str(y)] == 2 or sight[str(x)][str(y)] == 3:
                                
                                if sight[str(x)][str(y)] == 3 and multiplayer and traverse and (steps < 2850 or sight_range > 3) and sight_range >= 3:
                                    continue

                                if [x, y] not in food_position:
                                    if sight[str(x)][str(y)] == 3 and [x, y] not in super_FOOD:
                                        super_FOOD.append([x, y])

                                    food_position.append([x, y])
                                    
                                matrix_map[x][y] = 'X'

                    #print("CLOSEST COORDS: ", closest_coords)
                    t4 = time.time()
                    #print("Time for sight: ", t4 - t3)
                    # Print the matrix map in a more readable format
                    

                    #print("sight_range: ", sight_range)
                    l_points = [
                        point for point in l_points
                        if not adjacent_to_snake((point[0], point[1]), sight, size)
                    ]

                    l_points.sort(
                        key=lambda point: (

                            point[2] if (min(point[0], size[0] - point[0], point[1], size[1] - point[1]) > 1) else float('inf'),  # Distância de Manhattan
                            -point[3],  # Maior distância Manhattan
                            -point[3] if point[3] > sight_range else float('inf')  # Maior distância > sight_range
                        )
                    )
                    
                   
                    #print("Least Discovered: ", l_points)
                    #print("l_points: ", l_points)
                    
                    #farthest_point = max((point for point in l_all_coords if point[0:2] not in body and (sight[str(point[0])][str(point[1])] != 1 if traverse == False else True)), key=lambda point: point[2])[0:2] 
                    #print("Farthest Point: ", farthest_point)

                    
                    
                    #print("\nhead: ", head)
                    #print("\nfood: ", state['food']) 
                    #print("\nbody: ", body)
                    
                    #print("\nTraverse: ", traverse)

                    food = None
                    if food_position != []:
                        
                        min_distance = float('inf')
                        food_to_remove = None
                        for foodx,foody in food_position:
                            if [foodx, foody] == head or adjacent_to_snake([foodx, foody], sight, size):
                                food_to_remove = [foodx, foody]
                                
                            else:
                                distance = manhattan_distance([foodx, foody],head)
                                if(distance < min_distance):
                                    min_distance = distance
                                    food = [foodx,foody]


                        #print("FoodList:", food_position)

                        if food_to_remove:
                            food_position.remove(food_to_remove)

                            if food_to_remove in super_FOOD:
                                super_FOOD.remove(food_to_remove)

                            if original_map_copy[food_to_remove[0]][food_to_remove[1]] == 2:
                                original_map[food_to_remove[0]][food_to_remove[1]] = 0
                            '''   
                            else:
                                matrix_map = [row.copy() for row in original_map]
                            '''

                    #print("Foodlist: ", food_position)
                    #print("l_points: ", l_points)

                    if food:
                        if manhattan_distance(head, food) > manhattan_distance(head ,food) and original_map_copy[food[0]][food[1]] != 2: 
                            food_position.remove(food)

                    
                    if food == None:
                    
                        if l_points != []:
                            food = l_points
                            
                        if food == None:
                            #print("No food")
                            
                            while True:
                                food = marked_places[0]
                                #matrix_map[food[0]][food[1]] = 0
                                

                                if str(food[0]) not in sight or (str(food[0]) in sight and str(food[1]) not in sight[str(food[0])]):
                                    break
                                else:
                                    marked_places.pop(0)
                                    
                            #matrix_map = [row.copy() for row in original_map]
                    

                    #print("\nFood: ", food)
                    food_position.sort(key=lambda food: manhattan_distance(state['body'][0], food))
                    #print("traverse: ", traverse)
                    domain = PathToFoodDomain(body, food_position, sight, sight_range, size, matrix_map, traverse, multiplayer)

                    solution_path = []

                    t3 = time.time()

                    if isinstance(food[0], list):
                        food = l_points[0][0:2]

                    count = 0
                    go_to = []
                    while True:
                        x = random.randint(0, size[0] - 1)
                        y = random.randint(0, size[1] - 1)
                        if [x, y] not in body and str(x) not in sight and matrix_map[x][y] != 1 and manhattan_distance([x, y], food) > 7:
                            go_to.append([x, y])
                            count += 1
                            
                            if count == 3:
                                break
                    
                    
                    

                    problem = SearchProblem(domain, head, food)
                    tree = SearchTree(problem,body, strategy="a*")
                
                    solution_path = tree.search()
                    #print("Solution Path before: ", solution_path)
                    
                    new_body = None
                    solution_exit_path = None
                    possible = True


                    if original_map_copy[food[0]][food[1]] != 2 and solution_path:
                        
                        new_body = solution_path[-len(body):][::-1]
                        domain = PathToFoodDomain(new_body, food_position, sight, sight_range, size, matrix_map, traverse, multiplayer)
                        problem = SearchProblem(domain, food, go_to)
                        tree = SearchTree(problem, new_body, strategy="a*")
                        solution_exit_path = tree.search()

                        if not solution_exit_path:

                            domain = PathToFoodDomain(body, food_position, sight, sight_range, size, matrix_map, traverse, multiplayer)
                            problem = SearchProblem(domain, head, go_to)
                            tree = SearchTree(problem, body, strategy="a*")
                            solution_path = tree.search()

                            if not solution_path:
                                possible = False
                                if food in food_position:
                                    food_position.remove(food)

                    
                    #print("Closest Coords: ", closest_coords)
                    #print("Is possible: ", possible)
                    
                    closest_coords.sort(key=lambda point: point[2])    

                    if solution_path and not possible:
                        '''
                        block = 0
                        for x in range(-1, 2):
                            for y in range(-1, 2):
                                xi = (head[0] + x) % size[0]
                                yj = (head[1] + y) % size[1]
                                if (str(xi) in sight and str(yj) in sight[str(xi)] and sight[str(xi)][str(yj)] == 1) or xi == 0 or xi == size[0] - 1 or yj == 0 or yj == size[1] - 1:
                                    block += 1

                        if block > 5:
                            possible = True
                        '''
                        
                        #print("Not possible")
                        #print("Path:", solution_path)

                        if len(closest_coords) > 1:
                            for coord in closest_coords:
                                #print("Coor", coord[0:2])
                                if coord[0:2] in solution_path:
                                    closest_coords.remove(coord)
                                    

                    #print("Closest Coords 2.0: ", closest_coords)
                    t4 = time.time()
                    #print("Time for search: ", t4 - t3)
                    #print("l_points: ", l_points)
                    

                    
                    #print("-"*50)
                    #tree.display_counters()
                    #print("-"*50)

                    

                    #print("Solution Path after: ", solution_path)

                    solution_path1 = None
                    solution_exit_path1 = None
                    if solution_path:
                        solution_path1 = solution_path[len(body):]

                    if solution_exit_path:
                        solution_exit_path1 = solution_exit_path

                    
                    coord = None
                    if solution_path == None or (solution_path and not possible):
                        coord = closest_coords[0][0:2]

                    else:
                        if len(solution_path) > len(body):
                            coord = solution_path[len(body)]
                        

                    
                    if coord == None:
                        coord = solution_path[len(body)-1]
                    
                    #print("Coord: ", coord)
                    if coord != None:
                        if coord[0] == head[0] and coord[1] == (head[1] - 1) % (size[1]):  # Para 'up'
                            key = "w"
                        elif coord[0] == head[0] and coord[1] == (head[1] + 1) % (size[1]):  # Para 'down'
                            key = "s"
                        elif coord[0] == (head[0] - 1) % (size[0]) and coord[1] == head[1]:  # Para 'left'
                            key = "a"
                        elif coord[0] == (head[0] + 1) % (size[0]) and coord[1] == head[1]:  # Para 'right'
                            key = "d"

                    else:
                        key = ""


                    '''
                    print("-" * 80)
                    for y in range(len(matrix_map[0])):
                        for x in range(len(matrix_map)):
                            ele = matrix_map[x][y]
                            # Seleção de cor para impressão
                            if [x, y] == body[0]:
                                print(colorama.Fore.WHITE + str(4), end=" ")
                            elif [x,y] == body[-1]:
                                print(colorama.Fore.BLACK + str(4), end=" ")
                            elif str(x) in sight and str(y) in sight[str(x)] and sight[str(x)][str(y)] == 4 and [x, y] not in body:
                                print(colorama.Fore.LIGHTCYAN_EX + str(9), end=" ")
                            else:
                                if [x, y] == food:
                                    print(colorama.Fore.LIGHTYELLOW_EX + str(2), end=" ")
                                elif [x, y] in body:
                                    print(colorama.Fore.GREEN + str(4), end=" ")
                                elif [x, y] in go_to:
                                    print(colorama.Fore.YELLOW + str(5), end=" ")
                                elif solution_path1 and[x, y] in solution_path1:
                                    print(colorama.Fore.RED + str(ele), end=" ")
                                elif solution_exit_path1 and [x, y] in solution_exit_path1:
                                    print(colorama.Fore.LIGHTRED_EX + str(ele), end=" ")
                                elif str(x) in sight and str(y) in sight[str(x)]:
                                    print(colorama.Fore.CYAN + str(ele), end=" ")
                                elif ele == 0:
                                    print(colorama.Fore.WHITE + str(ele), end=" ")
                                elif ele == 1:
                                    print(colorama.Fore.BLUE + str(ele), end=" ")
                                elif ele == 2:
                                    print(colorama.Fore.YELLOW + str(ele), end=" ")  # Change food color to yellow
                                elif ele == 3:
                                    print(colorama.Fore.YELLOW + str(ele), end=" ")
                                elif ele == 'X':
                                    if traverse == False:
                                        ele = 'Y'
                                    print(colorama.Fore.MAGENTA + str(ele), end=" ")
                                
                        print("")
                    print(colorama.Style.RESET_ALL)
                    print("-" * 80)
                    '''
                    
                    
                t2 = time.time()
                if (t2 - t1) > time_total:
                    time_total = t2 - t1
                #print("Time: ", t2 - t1) 
                print("Highest Tme: ", time_total)


                
                    
                await websocket.send(
                            json.dumps({"cmd": "key", "key": key})
                        )  # send key command to server - you must implement this send in the AI agent
                            
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
       # Wait before retrying to avoid rapid reconne
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NAME", "hemapefe")
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
