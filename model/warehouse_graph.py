
import imutils

import numpy as np
import cv2 as cv
import  heapq
import json
from model.models import *

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
        self.lock = RLock()
        self.cells = {}
        self.cell_mappings = {}
        for cell in cells:
            self.cells[cell] = Cell(cell)
        for d_edge in directed_edges:
            if d_edge[0] not in self.cell_mappings:
                self.cell_mappings[d_edge[0]] = {} 
            self.cell_mappings[d_edge[0]][d_edge[1]] = DirectedEdge(self.cells[d_edge[0]], self.cells[d_edge[1]], d_edge[2]) 
        
        #agv_cell_utilization_slots = {} # k:cell_id -> {k:agv_id -> utilization}
        #agv_edge_utilization_slots = {} # k:from_cell -> {k:to_cell -> {k:agv_id -> utilization}}

    def lock(self):
        self.lock.acquire() 
    
    def unlock(self):
        self.lock.release() 
    
    # use to define a new utilization for AGV updated route within the shared state to use it later in route planning
    def update_utilization(self, agv_id, cell_utilization_list, prev_cell_utilization_list, edge_utilization_list, prev_edge_utilization_list):
        with self.lock:
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

    def occupy_singe_cell(self, agv, timestamp_from = None, cell_id = None): # consider only while 
        with self.lock:
            if cell_id is None:
                cell_id = agv.position   
            self.cells[cell_id].avg_utilization_slots[agv.agv_id] = CellUtilization(agv.agv_id, cell_id, timestamp_from, float('inf'), 0) 
            # if agv.position is not None:
            #     self.cells[agv.position].occupied_agv = None
            # agv.assign_position(cell_id)
            # self.cells[cell_id].occupied_agv = agv
    
    # def check_cell_occupied(self, agv, cell_id):
    #     with self.lock:
    #         if self.cells[cell_id].occupied_agv is not None and self.cells[cell_id].occupied_agv.agv_id != agv.agv_id:
    #             return True 
    #         else:
    #             return False

    # def update_edge_utilization(self, agv_id, cell_from, cell_to, timestamp_from, timestamp_to):
    #     with self.lock:
    #         self.cell_mappings[cell_from][cell_to].avg_utilization_slots[agv_id] = EdgeUtilization(agv_id, cell_from, cell_to, timestamp_from, timestamp_to, 1)
    
    def get_edge_length(self, cell_from, cell_to): 
        length = 0
        with self.lock:
            length = self.cell_mappings[cell_from][cell_to].length
        return length



    def get_occupied_timeslots_edges(self, agv_id, cell_from, cell_to, bidirectional = False):
        utilizations = []  
        with self.lock:
            cell_from_list = []
            if cell_from is None:
                cell_from_list = list(self.cell_mappings.keys())
            else:
                cell_from_list = [cell_from]
            for cell_from_idx in cell_from_list:
                if cell_from_idx in self.cell_mappings[cell_from_idx]:
                    for agv_idx in self.cell_mappings[cell_from_idx][cell_to].avg_utilization_slots:
                        utiliz = self.cell_mappings[cell_from_idx][cell_to].avg_utilization_slots[agv_idx]
                        # if utiliz.agv_id != agv_id:
                        utilizations.append(utiliz)
        return utilizations


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
            d, node = heapq.heappop(queue)
            
            if nodes[node].finished or nodes[destination].finished:
                continue

            nodes[node].finished=True
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





