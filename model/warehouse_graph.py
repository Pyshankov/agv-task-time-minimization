
import imutils

import numpy as np
import cv2 as cv
import  heapq
import json
from model.models import *

def build_graph_v1(): 
    cell_indx = range(1,71)
    directed_edges = []
    # to left only:  
    for idx in range (9,11): 
        directed_edges.append((idx, idx - 1, 1))

    # to right only:  
    for idx in range (62,70): 
        directed_edges.append((idx - 1, idx, 1))
    # down only:  
    for idx in [1, 51]:
        directed_edges.append((idx, idx + 10, 1))

    # left and down: 
    for idx in range (52,59): 
        directed_edges.append((idx, idx - 1, 1))
        directed_edges.append((idx, idx + 10, 1))
    for idx in range (2,9): 
        directed_edges.append((idx, idx - 1, 1))
        directed_edges.append((idx, idx + 10, 1))

    # up only: 
    for idx in [ 70]:
        directed_edges.append((idx, idx - 10, 1))

    # up and left:     
    for idx in [59, 60, 49, 50, 39, 40, 29, 30, 19, 20]:
        directed_edges.append((idx, idx - 10, 1))
        directed_edges.append((idx, idx - 1, 1))


    # up and right:     
    for idx in [69]:
        directed_edges.append((idx, idx - 10, 1))
        directed_edges.append((idx, idx + 1, 1))

    # down and right:     
    for idx in [11]:
        directed_edges.append((idx, idx + 10, 1))
        directed_edges.append((idx, idx + 1, 1))

    # up, down and left:  
    for idx in [18, 28, 38, 48]:
        directed_edges.append((idx, idx - 10, 1))
        directed_edges.append((idx, idx + 10, 1))
        directed_edges.append((idx, idx - 1, 1))

    # up, down and right:  
    for idx in [21, 31, 41]:
        directed_edges.append((idx, idx - 10, 1))
        directed_edges.append((idx, idx + 10, 1))
        directed_edges.append((idx, idx + 1, 1))
    
    #up, down, left, right
    for rng in [range(12, 18), range(22, 28), range(32, 38), range(42, 48)]:
        for idx in rng:
            directed_edges.append((idx, idx - 10, 1))
            directed_edges.append((idx, idx + 10, 1))
            directed_edges.append((idx, idx - 1, 1))
            directed_edges.append((idx, idx + 1, 1))

    graph = WarehouseGraph(cells = cell_indx, directed_edges = directed_edges)
    
    for idx in [12,13,22,23,32,33,42,43, 16,17,26,27,36,37,46,47]:
        graph.cells[idx].tote = Tote(idx)
        graph.cells[idx].occupied_tote = True
    
    return  graph

def build_graph_v2(): 
    cell_indx = range(1,61)
    directed_edges = []

    directed_edges.append((3, 18, 1))
    directed_edges.append((18, 3, 1))
    directed_edges.append((6, 21, 1))
    directed_edges.append((21, 6, 1))
    directed_edges.append((9, 24, 1))
    directed_edges.append((24, 9, 1))
    directed_edges.append((12, 27, 1))
    directed_edges.append((27, 12, 1))

        # to left only:  
    for idx in range (17,31): 
        directed_edges.append((idx, idx - 1, 1))

    # to right:  
    for idx in range (47,61): 
        directed_edges.append((idx - 1, idx, 1))
    
    # to right:  
    for idx in range (32,46): 
        directed_edges.append((idx - 1, idx, 1))

    directed_edges.append((34, 19, 1))
    directed_edges.append((16, 31, 1))
    directed_edges.append((20, 35, 1))
    directed_edges.append((37, 22, 1))
    directed_edges.append((23, 38, 1))
    directed_edges.append((40, 25, 1))
    directed_edges.append((26, 41, 1))
    directed_edges.append((43, 28, 1))
    directed_edges.append((44, 29, 1))
    directed_edges.append((45, 30, 1))

    directed_edges.append((31, 46, 1))
    directed_edges.append((48, 33, 1))
    directed_edges.append((35, 50, 1))    
    directed_edges.append((51, 36, 1))
    directed_edges.append((38, 53, 1))
    directed_edges.append((54, 39, 1))
    directed_edges.append((41, 56, 1))
    directed_edges.append((57, 42, 1))
    directed_edges.append((58, 43, 1))
    directed_edges.append((59, 44, 1))
    directed_edges.append((60, 45, 1))

    graph = WarehouseGraph(cells = cell_indx, directed_edges = directed_edges)

    for idx in [3,6,9,12]:
        graph.cells[idx].tote = Tote(idx)
        graph.cells[idx].occupied_tote = True

    return  graph

class WarehouseGraph(object): 
    def __init__(self, cells = range(0,3), directed_edges = [(0,1, 10.0), (1,2, 50.0), (0,2, 10.0)]):
        self.cells = {}
        self.cell_mappings = {}
        for cell in cells:
            self.cells[cell] = Cell(cell)
        for d_edge in directed_edges:
            if d_edge[0] not in self.cell_mappings:
                self.cell_mappings[d_edge[0]] = {} 
            self.cell_mappings[d_edge[0]][d_edge[1]] = DirectedEdge(self.cells[d_edge[0]], self.cells[d_edge[1]], d_edge[2]) 

    # use to define a new utilization for AGV updated route within the shared state to use it later in route planning
    def update_utilization(self, agv_id, cell_utilization_list, prev_cell_utilization_list, edge_utilization_list, prev_edge_utilization_list):
        # remove old # remove old utolization for cells within the route for particular AGV for cells within the route for particular AGV
        for prev_cell_util in prev_cell_utilization_list:
            self.cells[prev_cell_util.cell_id].avg_utilization_slots.pop(agv_id) 
        # add new utilization for cells within the route for particular AGV
        for cell_util in cell_utilization_list:
            self.cells[cell_util.cell_id].avg_utilization_slots[agv_id] = cell_util 
        # remove old utilization for edges within the route for particular AGV
        for prev_edge_util in prev_edge_utilization_list:
            self.cell_mappings[prev_edge_util.from_cell][prev_edge_util.to_cell].avg_utilization_slots.pop(agv_id)
        # add new utilization for edges within the route for particular AGV
        for edge_util in edge_utilization_list:
            self.cell_mappings[edge_util.from_cell][edge_util.to_cell].avg_utilization_slots[agv_id] = edge_util

    

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
            
            if nodes[node].finished or nodes[destination].finished:
                continue
            nodes[node].finished=True
            # print ((d, node), end = " ")

            if node in self.cell_mappings: 
                for next_cell in self.cell_mappings[node]:  
                    if nodes[next_cell].finished:
                        continue
                    new_d = d + self.cell_mappings[node][next_cell].weight
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

    def str(self):
        return json.dumps(self.__dict__)





