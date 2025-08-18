
import math
from tree_search import *


class PathToFoodDomain(SearchDomain):


    def __init__(self, body, food, sight, sight_range, size, map, traverse, multiplayer):
        self.body = body

        self.sight = sight
        self.sight_range = sight_range
        self.size = size
        self.map = map
        self.traverse = traverse
        self.multiplayer = multiplayer

        self.other_players = []
        if multiplayer:
            self.other_players = self.get_other_players()

        #print(f"Other players: {self.other_players}")



    def actions(self, state):

        actlist = ['up', 'down', 'left', 'right']
        act_ops = [(0,-1), (0,1), (-1,0), (1,0)]

        
        if self.traverse == False:
            x, y = state
            for i in range(4):
                dx, dy = act_ops[i]
                newx = (x + dx) 
                newy = (y + dy) 

                if newx < 0 or newx >= self.size[0] or newy < 0 or newy >= self.size[1]:
                    actlist.remove(['up', 'down', 'left', 'right'][i])
                
        #print('*'*50)
        #print(f"Ações possíveis a partir de {state}: {actlist}")
        
        
       
        return actlist
    
    def result(self, state, action):
        x, y = state
        nextstate = []

        if self.traverse == True:
            if action == 'up':
                # Movimenta para cima circularmente, sem +1
                nextstate = [x, (y - 1) % self.size[1]]

            elif action == 'down':
                # Movimenta para baixo circularmente, sem +1
                nextstate = [x, (y + 1) % self.size[1]]
            elif action == 'left':
                # Movimenta para esquerda circularmente, sem +1
                nextstate = [(x - 1) % self.size[0], y]
            elif action == 'right':
                # Movimenta para direita circularmente, sem +1
                nextstate = [(x + 1) % self.size[0], y]

        else:
            if action == 'up':
                # Movimenta para cima
                nextstate = [x, y - 1]

            elif action == 'down':
                # Movimenta para baixo
                nextstate = [x, y + 1]
            elif action == 'left':
                # Movimenta para esquerda
                nextstate = [x - 1, y]
            elif action == 'right':
                # Movimenta para direita
                nextstate = [x + 1, y]

        
        
        return nextstate


    def cost(self, state, newstate, body):
       
        x, y = newstate 
        cost = 1
        
        if self.traverse == False:
            if self.map[x][y] == 1:
                #print("Wall")
                return 1001

        
        
        if [x,y] in body:
            #print("Body: ")
            return 1001

        if self.multiplayer:
            if self.traverse:
                if str(x) in self.sight and str(y) in self.sight[str(x)] and self.sight[str(x)][str(y)] == 3:
                    return 101

            if [x,y] in self.other_players:
                return 1001

            for i, j in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Up, Down, Left, Right
                new_x = (x + i) % self.size[0]
                new_y = (y + j) % self.size[1]

                if [new_x, new_y] in self.other_players:
                    return 101
                    
        
        return cost
    

    def heuristic(self, state, goal):
        x1, y1 = state

        if isinstance(goal[0], list):
            min_distance = float('inf')
            for g in goal:
                x2, y2 = g
                if self.traverse:
                    dx = min(abs(x2 - x1), self.size[0] - abs(x2 - x1))
                    dy = min(abs(y2 - y1), self.size[1] - abs(y2 - y1))
                else:
                    dx = x2 - x1
                    dy = y2 - y1
                distance = dx**2 + dy**2
                if distance < min_distance:
                    min_distance = distance
            return min_distance
        else:
            x2, y2 = goal
            if self.traverse:
                dx = min(abs(x2 - x1), self.size[0] - abs(x2 - x1))
                dy = min(abs(y2 - y1), self.size[1] - abs(y2 - y1))
            else:
                dx = x2 - x1
                dy = y2 - y1
            return dx**2 + dy**2
        
    
    
    
    def satisfies(self, head, food):
        
        if isinstance(food[0], list):
            for f in food:
                if head == f:
                    return True
            return False
        else:
            return food == head



    def get_other_players(self):
        other_players = []
        for x in self.sight.keys():
            for y in self.sight[x].keys():
                if self.sight[x][y] == 4 and [int(x), int(y)] not in self.body:
                    #print("Body", self.body, "[]", [int(x), int(y)])
                    other_players.append([int(x), int(y)])
        
        return other_players