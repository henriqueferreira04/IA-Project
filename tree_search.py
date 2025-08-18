
# Module: tree_search
# 
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2020,
#  Inteligência Artificial, 2014-2023

from abc import ABC, abstractmethod

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
        
    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent, cost): 
        self.state = state
        self.parent = parent
        self.depth = 0 if not parent else parent.depth + 1
        self.cost = cost
        self.heuristic = 0
        self.body = [state]
        
        
        if parent != None:
            ##pensar em fazer -1
            self.cost += parent.cost 
            self.body = [state] + parent.body[:-1]

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:
    
    # construtor
    def __init__(self,problem, body, strategy='breadth'): 
        self.problem = problem
        
        body_nodes = [SearchNode(state, None, 0) for state in body]
        for i in range(len(body_nodes) - 2, -1, -1):

            body_nodes[i].parent = body_nodes[i +1]
            
        root = body_nodes[0]
        
        root.body = body
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.terminals = 0
        self.non_terminals = 0
        self.childs = 0 

        self.nodes_generated = len(body)  # Contador para nós gerados
        self.nodes_expanded = 0   # Contador para nós expandidos

        
        

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)

    # procurar a solucao
   
   
    def search(self, limit=None):
        #print("Initial state: ", self.problem.initial)
        #print("Goal state: ", self.problem.goal)

        visited = set()  # Use set para armazenar estados visitados
        while self.open_nodes:
            #print("Open nodes: ", len(self.open_nodes))
            node = self.open_nodes.pop(0)

            if node.cost > 500:
                return None
            
            #print("------------>state: ", node.state)
            #print("------------>cost: ", node.cost)
            #print(len(self.open_nodes))
            self.nodes_expanded += 1  # Conta o nó expandido

            if self.problem.goal_test(node.state):
                #print("Solution found!")
                self.solution = node
                #print(self.get_path(node))
                self.terminals = len(self.open_nodes) + 1
                return self.get_path(node)

            lnewnodes = []
            self.non_terminals += 1

            if limit is None or node.depth < limit:
                for a in self.problem.domain.actions(node.state):
                    newstate = self.problem.domain.result(node.state, a)
                    cost = self.problem.domain.cost(node.state, newstate, node.body)
                    newnode = SearchNode(newstate, node, cost)

                    # Incrementa o contador de nós gerados
                    self.nodes_generated += 1
                    newnode.heuristic = self.problem.domain.heuristic(newnode.state, self.problem.goal)

                    #print("newnode: ", newnode.state)
                    #print("cost: ", newnode.cost)
                    #print("heuristic: ", newnode.heuristic)

                    if newnode.cost < 1000 and tuple(newnode.state) not in visited:
                        lnewnodes.append(newnode)
                        visited.add(tuple(newnode.state))  # Marcar como visitado

                    self.childs += 1

                
                self.add_to_open(lnewnodes)

        #print("No solution found!")
        return None

    

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)

        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes

        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.cost)

        elif self.strategy == 'greedy':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.heuristic)

        elif self.strategy == 'a*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: (node.cost + node.heuristic))
            '''
            lnewnodes.sort(key=lambda node: (node.cost + node.heuristic))
            self.open_nodes = lnewnodes 
            '''
          

            

    def display_counters(self):
        print(f"Nós gerados: {self.nodes_generated}")
        print(f"Nós expandidos: {self.nodes_expanded}")
        print(f"Nós abertos ao final: {len(self.open_nodes)}")

    @property
    def length(self):
        return self.solution.depth
    
    @property
    def avg_branching(self):
        return self.childs / self.non_terminals
    
    @property
    def cost(self):
        return self.solution.cost
    



