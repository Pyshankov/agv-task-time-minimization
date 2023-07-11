import time
import math
import argparse
import imutils

import numpy as np
import cv2 as cv
import  heapq

class Cell(object): 
    def __init__(self, unique_id, length = 1.5,  x = 0, y = 0):
        self.unique_id = unique_id
        self.length = length
        self.x = x
        self.y = y
        self.occupied_tote = False
        self.occupied_agv = False

    def __str__(self):
        return f'{self.unique_id}'    
        
class DirectedEdge(object): 
    def __init__(self, cell_from, cell_to, weight = 1.0):
        self.cell_from = cell_from
        self.cell_to = cell_to
        self.weight = weight

    def assign_weight(self, new_weight):
        self.weight = new_weight

class Task(object): 
    def __init__(self, type, origin, destinations, priority):
        self.type = type
        self.origin = origin
        self.destinations = destinations
        self.priority = priority


class Route(object): 
    def __init__(self):
        self.cell_sequence = []

    def add_cell(self, cell): 
        self.cell_sequence.append(cell)   
        # mark sell, add info: 
        # - expected arrival timestamp
        # -  


class AGV(object): 
    def __init__(self, position, task, velocity):
        self.position = position
        self.task = task
        self.velocity = velocity #avg veloity for vehicle while moving (could be described as a function which  inludes accelertion as well)
        self.task = None

    def assign_task(self, task):
        self.task = task

class WarehouseGraph(object): 
    def __init__(self, cells = range(0,3), directed_edges = [(0,1, 10.0), (1,2, 50.0), (0,2, 10.0)]):
        self.cells = {}
        self.cell_mappings = {}
        for cell in cells:
            self.cells[cell] = Cell(cell)
        for d_edge in directed_edges:
            if d_edge[0] not in self.cell_mappings:
                self.cell_mappings[d_edge[0]] = []
            self.cell_mappings[d_edge[0]].append(DirectedEdge(Cell(d_edge[0]), Cell(d_edge[1]), d_edge[2])) 
                

    def bfs(self, origin, destination): 
        # bfs search the shortest path, weighs constructed from projection of other agvs
        # update the weighted Graph in the End
        class Node:
            def __init__(self, indx):
                self.d=float('inf') #current distance from source node
                self.parent=None
                self.finished=False
                self.indx = indx
        
        nodes = {}
        queue = [] 
        for cell in self.cells:
            nodes[cell]=Node(indx = cell)
        
        nodes[origin].d = 0
        heapq.heappush(queue, (0, origin))

        while queue:         
            d, node =  heapq.heappop(queue)
            
            if nodes[node].finished:
                continue
            nodes[node].finished=True
            # print ((d, node), end = " ")

            if node in self.cell_mappings: 
                for neighbour in self.cell_mappings[node]:
                    next_cell = neighbour.cell_to.unique_id
                    if nodes[next_cell].finished:
                        continue
                    new_d = d + neighbour.weight
                    if new_d < nodes[next_cell].d:
                        nodes[next_cell].d = new_d
                        nodes[next_cell].parent = nodes[node]
                        heapq.heappush(queue,(new_d,next_cell))
        
        res =  []
        if nodes[destination].finished:
            current = nodes[destination]
            while origin != current.indx:
                res.append(current.indx)
                current = current.parent
            res.append(origin)
            return res[::-1]
        else:
            return []






    



