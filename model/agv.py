


import imutils

import numpy as np
import cv2 as cv
import  heapq

from model.models import *
from model.warehouse_graph import *


class AGV(object): 
    def __init__(self, position, agv_id = 0, task = None, velocity = 0.5, time_projection_coeficiient = 1.05): 
        self.agv_id = agv_id
        self.position = position # cell_id
        self.task = task
        self.velocity = velocity #avg veloity m/s for vehicle while moving (could be described as a function which  inludes accelertion as well)
        self.cell_utilization_list = []
        self.edge_utilization_list = []
        self.ongoing_route = []
        self.time_projection_coeficiient = time_projection_coeficiient
        self.occupied_tote = False
        self.tote = None

    def assign_task(self, new_task):
        if self.task is not None: 
            return False
        if self.position != new_task.origin: 
            return False
        if self.occupied_tote == True and new_task.type == 'TOTE_TO_PERSON': 
            return False
        if self.occupied_tote == True and new_task.type == 'TOTE_PICKUP':
            return False
        self.task = new_task
        return True
    
    def tote_pickup(self, cell):
        if  cell.tote is None: 
            # nothing to pick up
            return
        self.occupied_tote = True
        self.tote = cell.tote
        cell.occupied_tote = False
        cell.tote = None
    
    def tote_place(self, cell): 
        if self.tote is None: 
            # nothing to place
            return 
        if self.tote is not None and cell.tote is not None:
            # not possible
            return 
        self.occupied_tote = False
        cell.occupied_tote = True
        cell.tote = self.tote
        self.tote = None


    def execute_task(self, warehouse_graph, sleep = True): 
        if self.task is None: 
            # no task, no actions
            return []
        
        start_milis = int(round(time.time() * 1000))
        
        if self.position == self.task.origin and self.task.type == 'TOTE_TO_PERSON' and warehouse_graph.cells[self.position].tote is not None: 
            # task start
            self.tote_pickup(warehouse_graph.cells[self.position])

        if self.position == self.task.destinations: 
            if self.task.type == 'TOTE_TO_PLACEMENT':
                self.tote_place(warehouse_graph.cells[self.position])    
            # task competed
            
            prev_cell_utilization = self.cell_utilization_list
            prev_edge_utilization = self.edge_utilization_list
            self.cell_utilization_list = [CellUtilization(self.position, start_milis, start_milis + 3 * 1000 ,self.task.priority)]
            self.edge_utilization_list = []
            warehouse_graph.update_utilization(self.agv_id, self.cell_utilization_list, prev_cell_utilization,[], prev_edge_utilization)
            self.task = None
            return []
        
        if len(self.ongoing_route) != 0:
            next_cell_move = self.ongoing_route[1] if len(self.ongoing_route) > 1 else self.ongoing_route[0]
            next_cell_occupied = False
            # check is you can move towards the next sell
            for occupied_agv_id in warehouse_graph.cells[next_cell_move].avg_utilization_slots:  
                cell_slot = warehouse_graph.cells[next_cell_move].avg_utilization_slots[occupied_agv_id]
                if(occupied_agv_id != self.agv_id and (start_milis >= cell_slot.time_start or start_milis <= cell_slot.time_start)): 
                    next_cell_occupied = True
                    continue
            if next_cell_occupied == False:
                move_time = (warehouse_graph.cells[self.position].length + warehouse_graph.cells[next_cell_move].length) / (2 * self.velocity)
                if sleep:
                    time.sleep(move_time) 
                self.position = next_cell_move
                

        # update the route to see where agv can move 
        route, cell_utilization_list, edge_utilization_list = self._bfs(warehouse_graph, self.position, self.task.destinations, start_milis)
        self.ongoing_route = route
        prev_cell_utilization = self.cell_utilization_list
        prev_edge_utilization = self.edge_utilization_list
        self.cell_utilization_list = cell_utilization_list
        self.edge_utilization_list = edge_utilization_list

        warehouse_graph.update_utilization(self.agv_id, cell_utilization_list, prev_cell_utilization, edge_utilization_list, prev_edge_utilization)

        return route
    
    def _bfs(self, warehouse_graph, cell_from, cell_to, start_milis = int(round(time.time() * 1000))): 
        class Node:
            def __init__(self, indx):
                self.d=float('inf') #current distance from source node
                self.parent=None
                self.finished=False
                self.indx = indx
                self.time_arival = None; 
        
        nodes = {}
        queue = [] 
        for cell in warehouse_graph.cells:
            nodes[cell]=Node(indx = cell)
        
        nodes[cell_from].d = 0
        nodes[cell_from].time_arival = start_milis
        heapq.heappush(queue, (0, cell_from))

        while queue:         
            d, node = heapq.heappop(queue)
            
            if nodes[node].finished:
                continue
            nodes[node].finished=True

            if node in warehouse_graph.cell_mappings: 
                for next_cell in warehouse_graph.cell_mappings[node]:  
                    #TODO: do not consider cell wich occupied with tote in case AGV is loaded
                    if nodes[next_cell].finished or (self.occupied_tote == True and warehouse_graph.cells[next_cell].occupied_tote == True): 
                        continue
                    # compute the arival time 
                    delta_seconds = self.time_projection_coeficiient * (warehouse_graph.cells[next_cell].length + warehouse_graph.cells[node].length) / (2 * self.velocity)
                    start_ms = nodes[node].time_arival
                    end_ms = start_ms + delta_seconds * 1000 
                    #TODO: consider cell occupancy and delay end ms untill max cell ocupancy timeslot which overlaps with existing
                    # calculate weights of utilization / occupancy
                    cummulated_weight = 0 
                    for agv_id in warehouse_graph.cell_mappings[node][next_cell].avg_utilization_slots:
                        edge_util = warehouse_graph.cell_mappings[node][next_cell].avg_utilization_slots[agv_id]
                        if self.agv_id != agv_id and (start_ms <= edge_util.time_end) and (end_ms >= edge_util.time_start):
                            cummulated_weight = cummulated_weight + 1
                        
                    new_d = d + cummulated_weight * warehouse_graph.cell_mappings[node][next_cell].weight #+ delta_seconds
                    if new_d < nodes[next_cell].d:
                        nodes[next_cell].d = new_d
                        nodes[next_cell].time_arival = end_ms
                        nodes[next_cell].parent = nodes[node]
                        heapq.heappush(queue,(new_d,next_cell))
        
        res =  []
        cell_utilization_list = []
        edge_utilization_list = []

        if nodes[cell_to].finished:
            current = nodes[cell_to]
            while cell_from != current.indx:
                res.append(current.indx)
                e_util = EdgeUtilization(current.parent.indx, current.indx, current.parent.time_arival, current.time_arival, self.task.priority)
                c_util = CellUtilization(current.indx, current.time_arival, current.time_arival + 2 * 1000 ,self.task.priority) # edge occupied for 2 sec 
                edge_utilization_list.append(e_util)
                cell_utilization_list.append(c_util)
                current = current.parent
            res.append(cell_from)
            return (res[::-1], cell_utilization_list, edge_utilization_list)
        else:
            return ([], [], [])



    



