

import imutils
import numpy as np
import cv2 as cv
import  heapq
from model.models import *
from model.warehouse_graph import *


class AGV(object): 
    MAX_VELOCITY = 2
    def __init__(self, agv_id = 0, task = None, velocity = 0.0, time_projection_coeficiient = 1.05): 
        self.agv_id = agv_id
        self.task = task
        self.velocity = velocity #avg veloity m/s for vehicle while moving (could be described as a function which  inludes accelertion as well)
        self.cell_utilization_list = []
        self.edge_utilization_list = []
        self.ongoing_route = []
        self.time_projection_coeficiient = time_projection_coeficiient
        self.tote = None
        self.position = None # cell_id

    def assign_position(self, new_cell_id):
        self.position = new_cell_id


    def assign_task(self, new_task):
        if(self.task is None): 
            self.task = new_task
        else: 
            raise Exception(f'AGV: {self.agv_id} has another task assigned.')
    
    def tote_pick(self, tote):
        self.tote = tote

    def tote_place(self): 
        self.tote = None

    def execute_task(self, warehouse_graph, start_milis = int(round(time.time() * 1000))): 
        if self.task is None or self.task.is_finished(): 
            print("none")
            # no task, no actions
            return []
        if self.task.is_pending():
            started = self.task.start(self)
            print("pending")
            if not started:
                return []
        if self.task.is_in_progress():
            finished = self.task.finish(self)
            if finished:
                print("finished")
                return []
        
        if len(self.ongoing_route) == 0 and len(self.task.destinations) > 0:
            self.ongoing_route = warehouse_graph.bfs(self.position, self.task.destinations[0])

        if len(self.ongoing_route) == 1 and self.position == self.ongoing_route[0]:
            # print(self.ongoing_route)
            # print(self.position)
            self.ongoing_route = []
            return self.ongoing_route

        next_cell = self.ongoing_route[1] 
        next_next_cell = None if len(self.ongoing_route) < 3 else self.ongoing_route[2] 

        with warehouse_graph.lock:
            new_edge_utils = []
            next_utilizations = warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_cell)
            occupied_by_other_agvs = False
            for util in next_utilizations:
                if util.agv_id != self.agv_id:
                    occupied_by_other_agvs = True

            if occupied_by_other_agvs is True:
                ongoing_util = self.edge_utilization_list[0]
                new_edge_utils.append(EdgeUtilization(self.agv_id, 0.0, ongoing_util.from_cell, self.position, start_milis, float('inf')))
                self.velocity = 0.0 # stop the vehicle
            else:
                length_m = warehouse_graph.get_edge_length(self.position, next_cell)
                time_end = start_milis + (length_m / AGV.MAX_VELOCITY) * 1000
                if next_next_cell is not None:
                    next_next_utilizations = warehouse_graph.get_occupied_timeslots_edges(self.agv_id, next_cell, next_next_cell)
                    for util in next_next_utilizations:
                        if self.agv_id != util.agv_id and (start_milis <= util.time_end) and (time_end >= util.time_start):
                            if(util.time_end > time_end):
                                time_end = util.time_end
                    self.velocity = length_m / (time_end - start_milis)
                new_edge_utils.append(EdgeUtilization(self.agv_id, self.velocity, self.position, next_cell, start_milis, time_end + 2000))
                if next_next_cell is not None:
                    l = warehouse_graph.get_edge_length(next_cell, next_next_cell)
                    time_end2 = time_end + (l / AGV.MAX_VELOCITY) * 1000
                    new_edge_utils.append(EdgeUtilization(self.agv_id, AGV.MAX_VELOCITY, next_cell, next_next_cell, time_end, time_end2 + 2000))
            
            prev_edge_utilization_list = self.edge_utilization_list
            self.edge_utilization_list = new_edge_utils
            warehouse_graph.update_utilization(self.agv_id, self.cell_utilization_list, self.cell_utilization_list, new_edge_utils, prev_edge_utilization_list)
        
        # check_can_move = warehouse_graph.check_cell_occupied(self, next_cell) == True
        # warehouse_graph.unlock()
        print(self.ongoing_route)
        print(self.position)

        # move vehicle
        if self.velocity != 0.0 : 
            util = self.edge_utilization_list[0]
            time1 = (util.time_end - util.time_start)/1000
            # print(time1)
            time.sleep(time1)
            self.position = util.to_cell
            # warehouse_graph.occupy_singe_cell(self, cell_id=util.to_cell)
            self.ongoing_route.pop(0)
        else:  
            time.sleep(1)

        return self.ongoing_route
    


    



