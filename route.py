import time
import math
import argparse
import imutils
import numpy as np
import sys




from model.models import *
from model.warehouse_graph import *
from model.agv import *

def main():

    # graph = WarehouseGraph(cells = range(0,4), directed_edges = [(0,1, 10.0), (1,2, 4.0), (0,2, 15.0), (2,3, 15.0)])
    # print(graph.bfs(0,2))

    graph1 = build_graph_v1()
    # print(graph1.bfs(16, 63))
    # print(graph1.bfs(63, 16))

    agv1 = AGV(position = 70, agv_id = 0)
    agv2 = AGV(position = 60, agv_id = 0)
    agv1.position

    agv2.assign_task(Task(agv1.position, 17, type = 'TOTE_PICKUP'))

    agv1.assign_task(Task(agv1.position, 16, type = 'TOTE_PICKUP'))
    
    route1 = agv1.execute_task(graph1, sleep = False)
    print(route1)
    while route1 != []:
        route1 = agv1.execute_task(graph1, sleep = False)
        print(route1)

    agv1.assign_task(Task(16, 63, type = 'TOTE_TO_PERSON'))
    route2 = agv1.execute_task(graph1, sleep = False)
    print(route2)
    while route2 != []:
        route2 = agv1.execute_task(graph1, sleep = False)
        print(route2)

    agv1.assign_task(Task(63, 16, type = 'TOTE_TO_PLACEMENT'))
    route3 = agv1.execute_task(graph1, sleep = False)
    print(route3)
    while route3 != []:
        route3 = agv1.execute_task(graph1, sleep = False)
        print(route3)


    # print(agv1.tote)
    # print(agv1.occupied_tote)
    # print(agv1.position)
    # print(agv1.task)
    # print(graph1.cells[16].occupied_tote)

    # print(agv1.execute_task(graph1, sleep = False))

    # print(agv1.tote)
    # print(agv1.occupied_tote)
    # print(agv1.position)
    # print(agv1.task)
    # print(graph1.cells[16].occupied_tote)

    # print(agv1.execute_task(graph1, sleep = False))
    # print(agv1.execute_task(graph1, sleep = False))
    # print(agv1.execute_task(graph1, sleep = False))

    # print(graph1.str())


if __name__ == '__main__':
    sys.exit(main())


