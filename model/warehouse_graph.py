
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

    graph = WarehouseGraph(cells = cell_indx, \
        directed_edges = directed_edges, \
        operator_stations = [48, 51, 54, 57], \
        tote_pickup_stations = [3, 6, 9, 12], \
        edges_adjecent_operator_station_only = [(48, 49), (51, 52), (54, 55)]\
            )

    for idx in graph.tote_pickup_stations:
        graph.cells[idx].tote = Tote(idx)
        graph.cells[idx].occupied_tote = True

    return  graph

class WarehouseGraph(object): 
    def __init__(self, shape = (15, 4), cells = range(1,4), operator_stations = [1,2], tote_pickup_stations = [2], directed_edges = [(1,2, 10.0), (2,3, 50.0), (1,3, 10.0)], edges_adjecent_operator_station_only = [(1,2)]):
        self.shape = shape # columns, rows, cell_ids in ascending order
        self.lock = RLock()
        self.cells = {} # cell id starts from "1" not "0"
        self.cell_mappings = {}
        self.operator_stations = operator_stations
        self.tote_pickup_stations = tote_pickup_stations
        self.edges_adjecent_operator_station_only = edges_adjecent_operator_station_only
        for cell in cells:
            x = ((cell-1) % shape[0]) * MIN_CELL_DIAMETER_M
            y = (shape[1] - int((cell-1)/shape[0])) * MIN_CELL_DIAMETER_M

            self.cells[cell] = Cell(cell, x = x,  y = y)
            if cell in operator_stations:
                self.cells[cell].type = "OPERATOR_STATION"
            if cell in tote_pickup_stations:
                self.cells[cell].type = "TOTE_PICKUP_STATION"
            
        for d_edge in directed_edges:
            if d_edge[0] not in self.cell_mappings:
                self.cell_mappings[d_edge[0]] = {}
            distance = math.sqrt(math.pow(self.cells[d_edge[1]].x - self.cells[d_edge[0]].x, 2) + math.pow(self.cells[d_edge[1]].y - self.cells[d_edge[0]].y, 2)) 
            self.cell_mappings[d_edge[0]][d_edge[1]] = DirectedEdge(self.cells[d_edge[0]], self.cells[d_edge[1]], distance) 
        
        for edj in edges_adjecent_operator_station_only:
            self.cell_mappings[edj[0]][edj[1]].type = "ADJACENT_OPERATOR_STATION_ONLY"

    def is_operator_stations_adjacent(self, st1, st2):
        # with self.lock:
            if self.cells[st1].type == "OPERATOR_STATION" and self.cells[st2].type == "OPERATOR_STATION":
                for cell in self.operator_stations:
                    # if there is a cell within st1 and st2, they are not adjecent
                    if (cell > st1 and cell < st2) or (cell > st2 and cell < st1):
                        return False
                return True
            else: 
                return False

    
    # use to define a new utilization for AGV updated route within the shared state to use it later in route planning
    def update_utilization(self, agv_id, edge_utilization_list, prev_edge_utilization_list):
        with self.lock:
            # remove old utilization for edges within the route for particular AGV
            for prev_edge_util in prev_edge_utilization_list:
                self.cell_mappings[prev_edge_util.from_cell][prev_edge_util.to_cell].avg_utilization_slots.pop(agv_id)
            # add new utilization for edges within the route for particular AGV
            for edge_util in edge_utilization_list:
                self.cell_mappings[edge_util.from_cell][edge_util.to_cell].avg_utilization_slots[agv_id] = edge_util

    def occupy_singe_cell(self, agv, cell_id): # consider only while 
        with self.lock:
            self.cells[cell_id].agv_id = agv.agv_id
            agv.position = cell_id
            agv.x = self.cells[cell_id].x
            agv.y = self.cells[cell_id].y

    def cell_occupied(self, agv, cell_id):
         with self.lock:
            if self.cells[cell_id].agv_id is None: 
                return False
            else:
                return self.cells[cell_id].agv_id != agv.agv_id    
    
    def cell_deoccupie(self, cell_id):
         with self.lock:
            self.cells[cell_id].agv_id = None

    def get_edge(self, cell_from, cell_to): 
        with self.lock:
            return self.cell_mappings[cell_from][cell_to]
        
    
    def get_edge_length(self, cell_from, cell_to): 
        length = 0
        with self.lock:
            length = self.cell_mappings[cell_from][cell_to].length
        return length

    def get_adjacent_cells_occupied(self, agv, cell):
        with self.lock:
            cell_from_list = list(self.cell_mappings.keys())
            for cell_from in cell_from_list:
                if cell in self.cell_mappings[cell_from]:
                    if self.cell_occupied(agv, cell):
                        return True
            return False
    
    def get_adjacent_cell_list_occupied(self, agv, cell):
        with self.lock:
            li = []
            cell_from_list = list(self.cell_mappings.keys())
            for cell_from in cell_from_list:
                if cell in self.cell_mappings[cell_from]:
                    if self.cell_occupied(agv, cell):
                        li.append(cell)
            return li
        

    def get_occupied_timeslots_edges(self, agv_id, cell_from, cell_to):
        utilizations = []  
        with self.lock:
            cell_from_list = []
            if cell_from is None:
                cell_from_list = list(self.cell_mappings.keys())
            else:
                cell_from_list = [cell_from]
            for cell_from_idx in cell_from_list:
                if cell_to in self.cell_mappings[cell_from_idx]:
                    for agv_idx in self.cell_mappings[cell_from_idx][cell_to].avg_utilization_slots:
                        utiliz = self.cell_mappings[cell_from_idx][cell_to].avg_utilization_slots[agv_idx]
                        if utiliz.agv_id != agv_id:
                            utilizations.append(utiliz)
        return utilizations
    
    def check_bidirectional(self, cell_to): 
        with self.lock:
            cell_from_list = list(self.cell_mappings.keys())
            for cell_from in cell_from_list:
                if cell_to in self.cell_mappings and cell_to in self.cell_mappings[cell_from] and cell_from in self.cell_mappings[cell_to]:
                    return True
            return False



    def bfs(self, origin, destination): 
        can_use_edges_operator_adjecent = self.is_operator_stations_adjacent(origin, destination)
        # bfs search the shortest path
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
                    
                    #if used only for adjecent operator stations - skip
                    if can_use_edges_operator_adjecent == False \
                        and self.cell_mappings[node][next_cell].type == "ADJACENT_OPERATOR_STATION_ONLY":
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





