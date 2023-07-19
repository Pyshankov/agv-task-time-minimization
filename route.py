import time
import math
import argparse
import imutils
import numpy as np
import sys

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt, animation
import  heapq
import random
from threading import Thread



from model.models import *
from model.warehouse_graph import *
from model.agv import *

def draw_graph2(graph1, agvs, agvs2, agvs3, agvs4):
    points = []
    positions = {}

    with graph1.lock:

        for cell in graph1.cells:
          x = ((cell-1) % 15) 
          y = int((cell-1)/15)
          points.append((x,4-y))
          positions[cell] = (x,4-y)

        G = nx.DiGraph()

        def add_edge_to_graph(G, e1, e2, w):
            G.add_edge(e1, e2, weight=w)

        for frm in graph1.cell_mappings:
            for to in graph1.cell_mappings[frm]: 
                add_edge_to_graph(G, frm, to, 1)

        color_map = []
        for node in G:
            if graph1.cells[node].unique_id == agvs.position:
                    color_map.append('blue') 
            elif graph1.cells[node].unique_id == agvs2.position:
                    color_map.append('red') 
            elif graph1.cells[node].unique_id == agvs3.position:
                    color_map.append('green') 
            elif graph1.cells[node].unique_id == agvs4.position:
                    color_map.append('#C6442A') 
            else:
              color_map.append('white')

    plt.clf()
    nx.draw(G, pos=positions, node_size=500, node_color=color_map, arrows=True)
    nx.draw_networkx_labels(G, pos=positions)
    plt.show()
    plt.pause(0.001)

def main():
    graph1 = build_graph_v2()
    print(graph1.check_bidirectional(30))

    plt.rcParams["figure.autolayout"] = True
    plt.ion()   

    agv1 = AGV(agv_id = 0) # blue
    graph1.occupy_singe_cell(agv1, cell_id=30)

    agv2 = AGV(agv_id = 1) # red
    graph1.occupy_singe_cell(agv2, cell_id=45)

    agv3 = AGV(agv_id = 2) # green
    graph1.occupy_singe_cell(agv3, cell_id=44)

    agv4 = AGV(agv_id = 3) # yellow
    graph1.occupy_singe_cell(agv4, cell_id=59)


    draw_graph2(graph1, agv1, agv2, agv3, agv4)


    def start1():
        agv1.assign_task(Task(agv1.position, [9], type = 'TOTE_PICKUP', tote = Tote(unique_id=1) ))
        while agv1.task.is_finished() is not True:
            agv1.execute_task(graph1, start_milis = int(round(time.time() * 1000)))
        
        # time.sleep(1)
        agv1.assign_task(Task(agv1.position, [6], type = 'TOTE_TO_PERSON', tote = Tote(unique_id=1)))
        while agv1.task.is_finished() is not True:
            agv1.execute_task(graph1, start_milis = int(round(time.time() * 1000)))
        
        # time.sleep(1)
        agv1.assign_task(Task(agv1.position, [9], type = 'TOTE_TO_PLACEMENT', tote = Tote(unique_id=1)))
        while agv1.task.is_finished() is not True:
            agv1.execute_task(graph1, start_milis = int(round(time.time() * 1000)))
        
        # time.sleep(1)
        agv1.assign_task(Task(agv1.position, [30], type = 'REST_AREA', tote = Tote(unique_id=1)))
        while agv1.task.is_finished() is not True:
            agv1.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

    
    def start2():
        agv2.assign_task(Task(agv2.position, [6], type = 'TOTE_PICKUP', tote = Tote(unique_id=2) ))
        while agv2.task.is_finished() is not True:
            agv2.execute_task(graph1, start_milis = int(round(time.time() * 1000)))
        
        # time.sleep(1)
        agv2.assign_task(Task(agv2.position, [52], type = 'TOTE_TO_PERSON', tote = Tote(unique_id=1) ))
        while agv2.task.is_finished() is not True:
            agv2.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

        # time.sleep(1)
        agv2.assign_task(Task(agv2.position, [6], type = 'TOTE_TO_PLACEMENT', tote = Tote(unique_id=1)))
        while agv2.task.is_finished() is not True:
            agv2.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

        # time.sleep(1)
        agv2.assign_task(Task(agv2.position, [45], type = 'REST_AREA', tote = Tote(unique_id=1)))
        while agv2.task.is_finished() is not True:
            agv2.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

    def start3():
        agv3.assign_task(Task(agv3.position, [6], type = 'TOTE_PICKUP', tote = Tote(unique_id=2) ))
        while agv3.task.is_finished() is not True:
            agv3.execute_task(graph1, start_milis = int(round(time.time() * 1000)))
        
        # time.sleep(1)
        agv3.assign_task(Task(agv3.position, [52], type = 'TOTE_TO_PERSON', tote = Tote(unique_id=1) ))
        while agv3.task.is_finished() is not True:
            agv3.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

        # time.sleep(1)
        agv3.assign_task(Task(agv3.position, [6], type = 'TOTE_TO_PLACEMENT', tote = Tote(unique_id=1)))
        while agv3.task.is_finished() is not True:
            agv3.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

        # time.sleep(1)
        agv3.assign_task(Task(agv3.position, [60], type = 'REST_AREA', tote = Tote(unique_id=1)))
        while agv3.task.is_finished() is not True:
            agv3.execute_task(graph1, start_milis = int(round(time.time() * 1000)))



    def start4():
        agv4.assign_task(Task(agv4.position, [6], type = 'TOTE_PICKUP', tote = Tote(unique_id=2) ))
        while agv4.task.is_finished() is not True:
            agv4.execute_task(graph1, start_milis = int(round(time.time() * 1000)))
        
        # time.sleep(1)
        agv4.assign_task(Task(agv4.position, [52], type = 'TOTE_TO_PERSON', tote = Tote(unique_id=1) ))
        while agv4.task.is_finished() is not True:
            agv4.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

        # time.sleep(1)
        agv4.assign_task(Task(agv4.position, [6], type = 'TOTE_TO_PLACEMENT', tote = Tote(unique_id=1)))
        while agv4.task.is_finished() is not True:
            agv4.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

        # time.sleep(1)
        agv4.assign_task(Task(agv4.position, [59], type = 'REST_AREA', tote = Tote(unique_id=1)))
        while agv4.task.is_finished() is not True:
            agv4.execute_task(graph1, start_milis = int(round(time.time() * 1000)))

    Thread(target = start4).start()
    Thread(target = start3).start()
    Thread(target = start2).start()
    Thread(target = start1).start()
    

    while True:
            draw_graph2(graph1, agv1, agv2, agv3, agv4)
            print()



if __name__ == '__main__':
    sys.exit(main())


