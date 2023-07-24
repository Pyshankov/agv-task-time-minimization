import time
import math
import argparse
import imutils
import numpy as np
import sys

import networkx as nx
from matplotlib import pyplot as plt, animation
import  heapq
import random
from threading import Thread

from netx_visualization import *
from warehouse_config import *

from model.models import *
from model.warehouse_graph import *
from model.agv import *


def generate_and_execute_task(agv, init_position, warehouse, pickup_location = None, task_number = 0, max_tasks = 10): 
    pickup_location = random.choice(warehouse.tote_pickup_stations) if pickup_location is None else pickup_location
    if agv.task is None or (agv.task.type == "TOTE_TO_PLACEMENT" and agv.task.is_finished): 
        task = Task(agv.position, [pickup_location], type = 'TOTE_PICKUP', tote = Tote(unique_id=1) )
        agv.assign_task(task)

    elif agv.task.type == "TOTE_PICKUP" and agv.task.is_finished:
        num_operator_stations = np.random.poisson(3, 1)[0] % len(warehouse.operator_stations)
        num_operator_stations = num_operator_stations if num_operator_stations > 0 else 1
        task = Task(agv.position, [random.choice(warehouse.operator_stations) for x in range(num_operator_stations)], type = 'TOTE_TO_PERSON' )
        agv.assign_task(task)
    
    elif agv.task.type == "TOTE_TO_PERSON" and agv.task.is_finished:
        task = Task(agv.position, [pickup_location], type = 'TOTE_TO_PLACEMENT' )
        agv.assign_task(task)


    elif agv.task.type == "TOTE_TO_PLACEMENT" and agv.task.is_finished:
        if(task_number >= max_tasks - 1):
            task = Task(agv.position, [init_position], type = 'REST_AREA')
        else:
            task = Task(agv.position, [pickup_location], type = 'TOTE_PICKUP', tote = Tote(unique_id=1) )
        agv.assign_task(task)
         
    while agv.task.is_finished() is not True:
        agv.execute_task(warehouse, start_milis = int(round(time.time() * 1000)))
    
    return (agv.task.type, pickup_location) # gather some metircs?? 

def start_agv(agv, init_position, warehouse): 
     task_number = 0
     task_type, pickup_location = generate_and_execute_task(agv, init_position, warehouse, pickup_location = None, task_number = task_number, max_tasks = 10)
     while task_type != "REST_AREA":
         task_number = task_number + 1
         task_type, pickup_location = generate_and_execute_task(agv, init_position, warehouse, pickup_location = pickup_location, task_number = task_number, max_tasks = 10)

def start_visualization(graph, agvs):
         while True:
            time.sleep(0.2)
            draw_graph(graph, agvs)

def main():
    n = 4
    graph1 = build_graph_n_stations(n)
    colors = ["blue", "red", "yellow", "green"]
    init_positions = [30, 45, 60, 44]
    agvs = []
    for id in range(0, n):
        agv = AGV(agv_id = id, color = colors[id]) 
        graph1.occupy_singe_cell(agv, cell_id=init_positions[id])
        agvs.append(agv)

    plt.rcParams["figure.figsize"] = [17, 4]
    plt.rcParams["figure.autolayout"] = True
    plt.ion()   

    # draw_graph(graph1, agvs)

    for agv in agvs:
        Thread(target = start_agv, args = (agv, agv.position, graph1)).start()

    # Thread(target = start_visualization, args = (graph1, agvs)).run()


if __name__ == '__main__':
    sys.exit(main())