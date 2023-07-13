import time
import math
import argparse
import imutils

import numpy as np
import cv2 as cv
import  heapq
import json

from threading import Thread
from threading import RLock
# from model.agv import *


class Tote(object): 
    def __init__(self, unique_id):
        self.unique_id = unique_id
    

class Cell(object): 
    def __init__(self, unique_id, length = 1.5,  x = 0, y = 0, tote = None):
        self.lock = RLock()
        self.unique_id = unique_id
        self.length = length
        self.x = x
        self.y = y
    
        self.avg_utilization_slots = {} # key value agv_id to CellUtilization
        self.occupied_tote = False if tote is None else True 
        self.tote = tote
        self.occupied_agv = None

    
    def set_agv(self, agv):
        with self.lock:
            self.occupied_agv = agv
            agv.position = self.unique_id
    
    def set_tote(self, tote):
        with self.lock:
            self.tote = tote

        
    def __str__(self):
        return f'{self.unique_id}: {self.avg_utilization_slots}'    

    def str(self):
        return f'{self.unique_id}: {self.avg_utilization_slots}'    
        
class DirectedEdge(object): 
    def __init__(self, cell_from, cell_to, weight = 1.0):
        self.cell_from = cell_from
        self.cell_to = cell_to
        self.weight = weight
        self.avg_utilization_slots = {} # key value agv_id to EdgeUtilization

    def __str__(self):
        return f'{self.cell_from.unique_id}_{self.cell_to.unique_id}:{self.avg_utilization_slots}'   

    def assign_weight(self, new_weight):
        self.weight = new_weight

class Utilization(object): 
    def __init__(self, time_start, time_end, priority):
        self.time_start = time_start
        self.time_end = time_end
        self.priority = priority
    
    def __str__(self):
        return f'time_start: {self.time_start}, time_end: {self.time_end}'    

    def str(self):
        return f'time_start: {self.time_start}, time_end: {self.time_end}'    

class EdgeUtilization(Utilization):
    def __init__(self, from_cell, to_cell, time_start, time_end, priority):  
        super().__init__(time_start, time_end, priority)
        self.from_cell = from_cell
        self.to_cell = to_cell
    
    def __str__(self):
        return f'time_start: {self.time_start}, time_end: {self.time_end}'    

    def str(self):
        return f'time_start: {self.time_start}, time_end: {self.time_end}'   

class CellUtilization(Utilization):
    def __init__(self, cell_id, time_start, time_end, priority):  
        super().__init__(time_start, time_end, priority)
        self.cell_id = cell_id
    
    def __str__(self):
        return f'time_start: {self.time_start}, time_end: {self.time_end}'    

    def str(self):
        return f'time_start: {self.time_start}, time_end: {self.time_end}'   

class Task(object): 
    def __init__(self, origin, destinations, priority = 1.0, type = 'TOTE_TO_PERSON'):
        self.type = type # TOTE_TO_PERSON, TOTE_TO_PLACEMENT, TOTE_PICKUP
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
