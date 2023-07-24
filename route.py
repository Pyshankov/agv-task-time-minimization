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


def main():
    graph1 = build_graph_n_stations(4)

    plt.rcParams["figure.figsize"] = [17, 6]
    plt.rcParams["figure.autolayout"] = True
    plt.ion()   

    agv1 = AGV(agv_id = 0, color = 'blue') 
    graph1.occupy_singe_cell(agv1, cell_id=30)
    task_list1 = [
        Task(agv1.position, [9], type = 'TOTE_PICKUP', tote = Tote(unique_id=1) ),
        Task(9, [48, 54, 57], type = 'TOTE_TO_PERSON'), 
        Task(57, [9], type = 'TOTE_TO_PLACEMENT'),
        Task(9, [agv1.position], type = 'REST_AREA')
    ]

    agv2 = AGV(agv_id = 1, color = 'red') 
    graph1.occupy_singe_cell(agv2, cell_id=45)
    task_list2 = [
        Task(agv2.position, [9], type = 'TOTE_PICKUP', tote = Tote(unique_id=2) ),
        Task(9, [51], type = 'TOTE_TO_PERSON'), 
        Task(51, [9], type = 'TOTE_TO_PLACEMENT'),
        Task(9, [51], type = 'TOTE_TO_PERSON'), 
        Task(51, [9], type = 'TOTE_TO_PLACEMENT'),
        Task(9, [agv2.position], type = 'REST_AREA')
    ]

    agv3 = AGV(agv_id = 2, color = 'green') 
    graph1.occupy_singe_cell(agv3, cell_id=59)
    task_list3 = [
        Task(agv3.position, [6], type = 'TOTE_PICKUP', tote = Tote(unique_id=2) ),
        Task(6, [48, 54], type = 'TOTE_TO_PERSON'), 
        Task(54, [6], type = 'TOTE_TO_PLACEMENT'),
        Task(6, [9], type = 'TOTE_PICKUP', tote = Tote(unique_id=2) ),
        Task(9, [48, 54], type = 'TOTE_TO_PERSON'), 
        Task(54, [9], type = 'TOTE_TO_PLACEMENT'),
        Task(9, [agv3.position], type = 'REST_AREA')
    ]

    agv4 = AGV(agv_id = 3, color = 'yellow')
    graph1.occupy_singe_cell(agv4, cell_id=60)
    task_list4 = [
        Task(agv4.position, [6], type = 'TOTE_PICKUP', tote = Tote(unique_id=3) ),
        Task(6, [57], type = 'TOTE_TO_PERSON'), 
        Task(57, [6], type = 'TOTE_TO_PLACEMENT'),
        Task(6, [agv4.position], type = 'REST_AREA')
    ]


    draw_graph(graph1, [agv1, agv2, agv3, agv4])

    def start_agv(graph, agv, task_list):
        while len(task_list) > 0:
            agv.assign_task(task_list.pop(0))
            time.sleep(1)  # wait 1 sec between tasks
            while agv.task.is_finished() is not True:
                agv.execute_task(graph, start_milis = int(round(time.time() * 1000)))
        sys.exit()

    def start_visualization(graph, agvs):
         while True:
            draw_graph(graph, agvs)
         

    # input("Press Enter to continue...")
    # time.sleep(10)
    Thread(target = start_agv, args = (graph1, agv1, task_list1)).start()
    Thread(target = start_agv, args = (graph1, agv2, task_list2)).start()
    Thread(target = start_agv, args = (graph1, agv3, task_list3)).start()
    Thread(target = start_agv, args = (graph1, agv4, task_list4)).start()

    Thread(target = start_visualization, args = (graph1, [agv1, agv2, agv3, agv4])).run()
    

if __name__ == '__main__':
    sys.exit(main())


