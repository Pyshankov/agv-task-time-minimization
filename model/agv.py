

import imutils
import numpy as np
import cv2 as cv
import  heapq
from model.models import *
from model.warehouse_graph import *
import math



class AGV(object): 
    MAX_VELOCITY = AGV_MAX_SPEED_M_S

    def __init__(self, agv_id = 0, task = None, velocity = 0.0, time_projection_coeficiient = 1.05, color = 'blue'): 
        self.agv_id = agv_id
        self.color = color 
        self.task = task
        self.velocity = velocity #avg veloity m/s for vehicle while moving (could be described as a function which  inludes accelertion as well)
        self.edge_utilization_list = []
        self.ongoing_route = []
        self.time_projection_coeficiient = time_projection_coeficiient
        self.tote = None

        # localization
        self.position = None # graph cell_id for localization and intersection 
        self.x = None # position x in m
        self.y = None # position y in m
        self.heading = (1, 0) # default towards positive x axis, so 0 degree

    def calculate_rotation_angel(self, directed_edge): 
        def unit_vector(vector):
            return vector / np.linalg.norm(vector)  
        def rotate_vector(vector, angle):
            x = int(vector[0] * math.cos(angle) - vector[1] * math.sin(angle))
            y = int(vector[0] * math.sin(angle) + vector[1] * math.cos(angle))
            return (x, y)
        edge_direction = (directed_edge.cell_to.x - directed_edge.cell_from.x, directed_edge.cell_to.y - directed_edge.cell_from.y)
        robot_ang_rad = np.arctan2(self.heading[1], self.heading[0])
        direction_ang_rad = np.arctan2(edge_direction[1], edge_direction[0])
        delta = robot_ang_rad - direction_ang_rad
        return [rotate_vector(self.heading, -delta), -delta * 180 / math.pi]

    def is_busy(self):
        return self.task is not None and self.task.is_finished() is False

    def assign_position(self, new_cell_id):
        self.position = new_cell_id

    def assign_task(self, new_task):
        if(self.task is None or self.task.is_finished()): 
            self.task = new_task
        else: 
            raise Exception(f'AGV: {self.agv_id} has another task assigned.')
    
    def tote_pick(self, tote):
        self.tote = tote

    def tote_place(self): 
        self.tote = None
    
    # TODO: 
    # 1. include AGV length and width into route planning (usefull when edge length is bigger than MIN_CELL_DIAMETER_M )
    # 2. approach change in velocity as a smooth function (part of the actuall physical agv move)
    def execute_task(self, warehouse_graph, start_milis, moving_update_rate = 3): 
        if self.task is None or self.task.is_finished(): 
            # print("none")
            # no task, no actions
            return []
        if self.task.is_in_progress():
            finished = self.task.finish(self, warehouse_graph)
            if finished:
                # print("finished")
                return []
        if self.task.is_pending():
            started = self.task.start(self, warehouse_graph)
            # print("pending")
            if not started:
                return []
        
        ut = ''
        if(len(self.edge_utilization_list) > 0):
            ut = self.edge_utilization_list[0]
            print(f'time:{start_milis} agv: {self.agv_id} velocity: {self.velocity}, heading: {self.heading}, position: {self.position}, route: {self.ongoing_route}, util: {ut}')


        with warehouse_graph.lock:
            new_edge_utils = []
            if len(self.ongoing_route) == 1:
                prev_edge_utilization_list = self.edge_utilization_list
                self.edge_utilization_list = new_edge_utils
                warehouse_graph.update_utilization(self.agv_id, new_edge_utils, prev_edge_utilization_list)
                warehouse_graph.occupy_singe_cell(self, self.ongoing_route[0])
                self.velocity = 0.0
                self.ongoing_route.pop(0)
                return []
                
            next_cell = self.ongoing_route[1] 
            length_m = warehouse_graph.get_edge_length(self.position, next_cell)
            time_end = None
            new_velocity = None
            new_heading, angel_deg = self.calculate_rotation_angel(warehouse_graph.get_edge(self.position,next_cell))
            #avoid longer path for rotation
            angel_deg = angel_deg if angel_deg <=180 else angel_deg - 360

            rotation_time = abs(angel_deg * AGV_ROTATION_DEGREE_PER_S) * 1000

            # procceed = True
            # next cell is occuiped, agv have to wait
            if warehouse_graph.cell_occupied(self, next_cell):  
                time_end = float('inf')
                new_velocity = 0.0
            elif len(warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_cell)) > 0:
                all_blocked = True
                for util in warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_cell):
                    all_blocked = all_blocked and math.isinf(util.time_end)
                if all_blocked:
                    time_end = start_milis + (length_m / AGV.MAX_VELOCITY) * 1000 
                    new_velocity = AGV.MAX_VELOCITY
                else:
                    time_end = float('inf')
                    new_velocity = 0.0
            else: 
                next_next_cell = None if len(self.ongoing_route) < 3 else self.ongoing_route[2] 
                time_end = start_milis + (length_m / AGV.MAX_VELOCITY) * 1000 
                new_velocity = AGV.MAX_VELOCITY
                if next_next_cell is not None: 
                    
                    #case when it's dock point
                    if self.position in warehouse_graph.tote_pickup_stations\
                        and (len(warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_cell)) > 0\
                        or len(warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_next_cell)) > 0):
                        time_end = float('inf')
                        new_velocity = 0.0
            
                    #agv not have an intent to visit the doc, 
                    # and another agv from doc not started moving yet - we can bypass
                    elif warehouse_graph.check_bidirectional(next_cell)\
                        and warehouse_graph.check_bidirectional(next_next_cell) is False\
                        and len(warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_cell)) == 0:
                            time_end = start_milis + (length_m / AGV.MAX_VELOCITY) * 1000 
                            new_velocity = AGV.MAX_VELOCITY

                    # another agv from doc station shared an intent to use the road, awaiting
                    elif warehouse_graph.check_bidirectional(next_cell)\
                        and warehouse_graph.check_bidirectional(next_next_cell) is False\
                        and len(warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_cell)) > 0:
                        time_end = float('inf')
                        new_velocity = 0.0

                    # another agv from doc station, wait untill it leaves to enter the doc
                    elif warehouse_graph.check_bidirectional(next_cell)\
                        and warehouse_graph.check_bidirectional(next_next_cell)\
                        and warehouse_graph.cell_occupied(self, next_next_cell):
                        time_end = float('inf')
                        new_velocity = 0.0

                    #case when cell is planned to be occupied
                    elif len(warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_next_cell)) > 0:   
                        next_next_utilizations = warehouse_graph.get_occupied_timeslots_edges(self.agv_id, None, next_next_cell)
                        for util in next_next_utilizations:
                            if self.agv_id != util.agv_id and (start_milis <= util.time_end) and (time_end >= util.time_start):
                                if(util.time_end > time_end):
                                    time_end = util.time_end
                        new_velocity = float(length_m) / (time_end - start_milis)

            new_edge_utils.append(EdgeUtilization(self.agv_id, new_velocity, self.position, next_cell, start_milis, time_end + rotation_time))            
            self.velocity = new_velocity
            prev_edge_utilization_list = self.edge_utilization_list
            self.edge_utilization_list = new_edge_utils
            warehouse_graph.update_utilization(self.agv_id, new_edge_utils, prev_edge_utilization_list)
        
        # moving logic, could be a separate method which has to be executed immidiatelly after weight update
        # rotate towards a new direction
        
        time.sleep(rotation_time/1000)
        self.heading = new_heading
        # move the vehicle
        if self.velocity > 0.0: 
            util = self.edge_utilization_list[0]
            time1 = (util.time_end - util.time_start)/1000
            moving_time = time1 - rotation_time/1000
            de = warehouse_graph.get_edge(self.position,next_cell)
            dist = (de.cell_to.x - de.cell_from.x, de.cell_to.y - de.cell_from.y)

            for i in range(0, moving_update_rate):
                self.x = self.x + dist[0] / moving_update_rate
                self.y = self.y + dist[1] / moving_update_rate
                time.sleep(moving_time / moving_update_rate)

            with warehouse_graph.lock:
                warehouse_graph.cell_deoccupie(self.position)
                warehouse_graph.occupy_singe_cell(self, util.to_cell)
            self.ongoing_route.pop(0)
        else:
            time.sleep(0.3) # to avoid accessive lock concurrency or use print function to block thread for writing


        return self.ongoing_route
        
    


    



