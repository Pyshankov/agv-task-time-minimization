import time
import math
import argparse
import imutils

import numpy as np
import cv2 as cv
import  heapq
import json
import logging

from threading import Thread
from threading import RLock
# from model.agv import *
from dataclasses import dataclass

# @dataclass(frozen=True)
class Tote(object): 
    def __init__(self, unique_id):
        self.unique_id = unique_id
    
class Cell(object): 
    def __init__(self, unique_id, length = 1.5,  x = 0, y = 0):
        self.unique_id = unique_id
        self.length = length
        self.x = x
        self.y = y
        self.avg_utilization_slots = {} # key value agv_id to CellUtilization
        self.agv_id = None

    def __str__(self):
        return f'{self.unique_id}: {self.avg_utilization_slots}'    
  
        
class DirectedEdge(object): 
    def __init__(self, cell_from, cell_to, weight = 1.0):
        self.cell_from = cell_from
        self.cell_to = cell_to
        self.weight = weight # length in m
        self.length = weight
        self.avg_utilization_slots = {} # key value agv_id to EdgeUtilization

    def __str__(self):
        return f'{self.cell_from.unique_id}_{self.cell_to.unique_id}:{self.avg_utilization_slots}'   

    def assign_weight(self, new_weight):
        self.weight = new_weight

# @dataclass(frozen=True)
class Utilization(object): 
    def __init__(self, agv_id, time_start, time_end, priority):
        self.agv_id = agv_id
        self.time_start = time_start
        self.time_end = time_end
        self.priority = priority
    
    def __str__(self):
        return f'agv: {self.agv_id} time_start: {self.time_start}, time_end: {self.time_end}'    

    def str(self):
        return f'agv: {self.agv_id} time_start: {self.time_start}, time_end: {self.time_end}' 

# @dataclass(frozen=True)
class EdgeUtilization(Utilization):
    def __init__(self, agv_id, velocity, from_cell, to_cell, time_start, time_end, priority = 1):  
        super().__init__(agv_id, time_start, time_end, priority)
        self.from_cell = from_cell
        self.to_cell = to_cell
        self.velocity = velocity

    def __str__(self):
        return f'agv: {self.agv_id} from_cell: {self.from_cell} to_cell: {self.to_cell}  time_start: {self.time_start}, time_end: {self.time_end}'    

    def str(self):
        return f'agv: {self.agv_id} time_start: {self.time_start}, time_end: {self.time_end}' 

# @dataclass(frozen=True)
class CellUtilization(Utilization):
    def __init__(self, agv_id, cell_id, time_start, time_end, priority):  
        super().__init__(agv_id, time_start, time_end, priority)
        self.cell_id = cell_id

class Task(object): 
    def __init__(self, origin, destinations, tote = None, priority = 1.0, type = 'TOTE_PICKUP'):
        self.type = type # TOTE_TO_PERSON, TOTE_TO_PLACEMENT, TOTE_PICKUP, REST_AREA
        self.origin = origin
        self.destinations = destinations
        self.priority = priority
        self.status = 'PENDING' #  PENDING, IN_PROGRESS, FINISHED
        self.tote = tote
        if type == 'TOTE_PICKUP' and tote is None:
            raise Exception("Sorry, 'TOTE_PICKUP' has to come with tote")
        
    def is_pending(self):
        return self.status == 'PENDING'

    def is_in_progress(self):
        return self.status == 'IN_PROGRESS'
    
    def is_finished(self):
        return self.status == 'FINISHED'
    
    def start(self, agv, warehouse):
        if(agv.position == self.origin):
            self.status = 'IN_PROGRESS'
            agv.ongoing_route = warehouse.bfs(agv.position, self.destinations[0])
            return True
        else:
            return False
    
    def finish(self, agv, warehouse):
        if(len(agv.ongoing_route) == 0 and len(self.destinations) == 0 and self.is_in_progress()):
            self.status = 'FINISHED'
            if(self.type == 'TOTE_PICKUP'):
                agv.tote_pick(self.tote)
            elif(self.type == 'TOTE_TO_PLACEMENT'):
                agv.tote_place()
            return True
        elif(len(self.destinations) > 0 and len(agv.ongoing_route) == 0 and self.is_in_progress()):
            agv.ongoing_route = warehouse.bfs(agv.position, self.destinations.pop(0))
            return False
        return False

